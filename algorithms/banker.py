
from copy import deepcopy


# 1. Validate the resource-allocation state
def validate_state(allocation, maximum, available):
    if not allocation or len(allocation) != len(maximum):
        raise ValueError(
            "Allocation and Maximum must have equal, non-zero process counts."
        )

    resource_count = len(available)

    if resource_count == 0:
        raise ValueError("At least one resource type is required.")

    for name, matrix in [
        ("Allocation", allocation),
        ("Maximum", maximum),
    ]:
        for row in matrix:
            if len(row) != resource_count:
                raise ValueError(
                    f"{name} dimensions do not match Available."
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

    for i in range(len(allocation)):
        for j in range(resource_count):
            if allocation[i][j] > maximum[i][j]:
                raise ValueError(
                    f"Allocation exceeds Maximum for P{i}, resource {j}."
                )


# 2. Calculate Need = Maximum - Allocation
def calculate_need(allocation, maximum):
    validate_state(
        allocation,
        maximum,
        [0] * len(allocation[0]) if allocation else []
    )

    need = []

    for i in range(len(allocation)):
        row = []

        for j in range(len(allocation[i])):
            row.append(maximum[i][j] - allocation[i][j])

        need.append(row)

    return need


# 3. Banker's Safety Algorithm
def safety_algorithm(allocation, maximum, available):
    validate_state(allocation, maximum, available)

    need = calculate_need(allocation, maximum)

    process_count = len(allocation)
    resource_count = len(available)

    # Step 1: Initialize Work and Finish
    work = available.copy()
    finish = [False] * process_count

    safe_sequence = []

    work_updates = [
        {
            "step": 0,
            "process": "Initial",
            "work": work.copy(),
        }
    ]

    # Step 2: Find an unfinished process with Need <= Work
    while len(safe_sequence) < process_count:

        found = False

        for i in range(process_count):

            if finish[i]:
                continue

            can_finish = all(
                need[i][j] <= work[j]
                for j in range(resource_count)
            )

            if can_finish:

                # Step 3: Work = Work + Allocation[i]
                for j in range(resource_count):
                    work[j] += allocation[i][j]

                # Step 4: Mark process finished
                finish[i] = True
                safe_sequence.append(f"P{i}")
                found = True

                # Record the Work vector after completion
                work_updates.append({
                    "step": len(safe_sequence),
                    "process": f"P{i}",
                    "work": work.copy(),
                })

                # Continue searching for the next process
                break

        # Step 5: Stop if no unfinished process can proceed
        if not found:
            break

    # Step 6: Check whether every process finished
    is_safe = all(finish)

    return {
        "safe": is_safe,
        "need": need,
        "safe_sequence": safe_sequence if is_safe else [],
        "partial_sequence": safe_sequence,
        "work_updates": work_updates,
        "unfinished": [
            f"P{i}"
            for i in range(process_count)
            if not finish[i]
        ],
    }


# 4. Resource Request Algorithm
def request_resources(
    allocation,
    maximum,
    available,
    process_index,
    request,
):
    validate_state(allocation, maximum, available)

    process_count = len(allocation)
    resource_count = len(available)

    # Check whether the process ID is valid
    if (
        type(process_index) is not int
        or process_index < 0
        or process_index >= process_count
    ):
        return {
            "status": "invalid",
            "message": "Invalid process identifier.",
        }

    # Validate the request vector
    if (
        not isinstance(request, (list, tuple))
        or len(request) != resource_count
        or any(type(x) is not int or x < 0 for x in request)
    ):
        return {
            "status": "invalid",
            "message": "Request must contain non-negative integers.",
        }

    need = calculate_need(allocation, maximum)

    # Check 1: Request <= Need
    if any(
        request[j] > need[process_index][j]
        for j in range(resource_count)
    ):
        return {
            "status": "invalid",
            "message": "Request exceeds the process's remaining Need.",
        }

    # Check 2: Request <= Available
    if any(
        request[j] > available[j]
        for j in range(resource_count)
    ):
        return {
            "status": "waiting",
            "message": (
                "Request exceeds Available. Defer the request; "
                "the original state remains unchanged."
            ),
        }

    # Check 3: Pretend to allocate the requested resources
    new_allocation = deepcopy(allocation)
    new_available = available.copy()

    for j in range(resource_count):
        new_allocation[process_index][j] += request[j]
        new_available[j] -= request[j]

    # Check 4: Run the safety algorithm on the temporary state
    result = safety_algorithm(
        new_allocation,
        maximum,
        new_available,
    )

    # Check 5: Grant only if the state remains safe
    if result["safe"]:
        return {
            "status": "granted",
            "message": "Request granted. The state remains safe.",
            "allocation": new_allocation,
            "available": new_available,
            "safety_result": result,
        }

    # Do not commit the temporary allocation
    return {
        "status": "denied",
        "message": (
            "Request denied because it produces an unsafe state. "
            "The original allocation remains unchanged."
        ),
        "allocation": deepcopy(allocation),
        "available": available.copy(),
        "safety_result": result,
    }
