
def validate_detection_data(allocation, request, available):
    """
    Validate the current resource allocation,
    outstanding requests, and available resources.
    """

    if not allocation or len(allocation) != len(request):
        raise ValueError(
            "Allocation and Request must have equal, non-zero process counts."
        )

    resource_count = len(available)

    if resource_count == 0:
        raise ValueError("At least one resource type is required.")

    for name, matrix in [
        ("Allocation", allocation),
        ("Request", request),
    ]:
        for row in matrix:
            if len(row) != resource_count:
                raise ValueError(
                    f"{name} dimensions must match Available."
                )

            for value in row:
                if type(value) is not int or value < 0:
                    raise ValueError(
                        f"{name} must contain non-negative integers."
                    )

    for value in available:
        if type(value) is not int or value < 0:
            raise ValueError(
                "Available must contain non-negative integers."
            )


def detect_deadlock(allocation, request, available):
    """
    Deadlock Detection Algorithm.

    Allocation[i][j] = resources of type j held by process i.
    Request[i][j] = additional resources process i currently needs.
    Available[j] = currently available resources of type j.
    """

    # STEP 1: Validate the input data.
    validate_detection_data(allocation, request, available)

    process_count = len(allocation)
    resource_count = len(available)

    # STEP 2: Initialize Work = Available.
    work = available.copy()

    # STEP 3: Initialize Finish.
    # If a process holds no resources, it can finish without
    # releasing any allocated resources.
    finish = [
        not any(allocation[i])
        for i in range(process_count)
    ]

    completed_processes = []

    work_updates = [
        {
            "step": 0,
            "process": "Initial",
            "work": work.copy(),
        }
    ]

    # STEP 4: Find an unfinished process whose current Request
    # can be satisfied by Work.
    while True:

        selected_process = None

        for i in range(process_count):

            if finish[i]:
                continue

            request_can_be_satisfied = all(
                request[i][j] <= work[j]
                for j in range(resource_count)
            )

            if request_can_be_satisfied:
                selected_process = i
                break

        # STEP 5: If no process can proceed, stop.
        if selected_process is None:
            break

        # STEP 6: Assume the selected process finishes.
        # Release its allocated resources back to Work.
        for j in range(resource_count):
            work[j] += allocation[selected_process][j]

        finish[selected_process] = True

        completed_processes.append(
            f"P{selected_process}"
        )

        # Record the Work vector for dashboard display.
        work_updates.append({
            "step": len(completed_processes),
            "process": f"P{selected_process}",
            "work": work.copy(),
        })

    # STEP 7: Processes that remain unfinished are detected
    # as deadlocked under the stated resource model.
    deadlocked_processes = [
        f"P{i}"
        for i in range(process_count)
        if not finish[i]
    ]

    return {
        "detected": bool(deadlocked_processes),
        "deadlocked": deadlocked_processes,
        "completed": completed_processes,
        "work_updates": work_updates,
        "work": work,
        "finish": finish,
    }


def recover_by_terminating(
    allocation,
    request,
    available,
    process_index,
):
    """
    Simulate terminating one process.

    Its allocated resources are released, and the detection
    algorithm is run again. Original inputs remain unchanged.
    """

    # Validate the original state first.
    validate_detection_data(allocation, request, available)

    if (
        type(process_index) is not int
        or not 0 <= process_index < len(allocation)
    ):
        raise ValueError("Invalid process identifier.")

    # STEP 1: Make copies so recovery is only simulated.
    new_allocation = [
        row.copy() for row in allocation
    ]

    new_request = [
        row.copy() for row in request
    ]

    new_available = available.copy()

    # STEP 2: Record the resources held by the victim.
    released_resources = new_allocation[process_index].copy()

    # STEP 3: Return the victim's resources to Available.
    for j in range(len(new_available)):
        new_available[j] += released_resources[j]

    # STEP 4: Remove the terminated process's allocation
    # and outstanding request from the simulated state.
    new_allocation[process_index] = [
        0
    ] * len(new_available)

    new_request[process_index] = [
        0
    ] * len(new_available)

    # STEP 5: Detect deadlock again after recovery.
    result = detect_deadlock(
        new_allocation,
        new_request,
        new_available,
    )

    result.update({
        "terminated": f"P{process_index}",
        "released": released_resources,
        "available_after": new_available,
        "allocation_after": new_allocation,
    })

    return result
