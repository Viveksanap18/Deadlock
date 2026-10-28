
def resource_order_check(held_resources, requested_resource, order):
    """
    Prevents circular wait by enforcing a global resource order.

    Example:
        order = ["R1", "R2", "R3"]
        If a process holds R2, it cannot request R1.
    """

    # Validate the requested and held resources.
    if requested_resource not in order:
        return {
            "allowed": False,
            "reason": "Unknown requested resource."
        }

    if any(resource not in order for resource in held_resources):
        return {
            "allowed": False,
            "reason": "Unknown resource in held resources."
        }

    # Find the highest-ranked resource already held.
    if held_resources:
        highest_held_order = max(
            order.index(resource) for resource in held_resources
        )

        requested_order = order.index(requested_resource)

        # New resources must follow increasing order.
        if requested_order < highest_held_order:
            return {
                "allowed": False,
                "reason": (
                    "Blocked: request violates the global "
                    "increasing resource order."
                )
            }

    return {
        "allowed": True,
        "reason": "Allowed by the global resource order."
    }


def hold_and_wait_check(held_resources, requested_resources, all_available):
    """
    Prevents hold-and-wait by requiring a process to obtain
    its requested resources together, or release its current
    resources before waiting for more.
    """

    # A process cannot wait for new resources while holding others.
    if held_resources and not all_available:
        return {
            "allowed": False,
            "reason": (
                "Blocked: release held resources before waiting "
                "for the requested resources."
            )
        }

    return {
        "allowed": True,
        "reason": (
            "Allowed: the selected policy does not permit "
            "hold-and-wait."
        )
    }


def preemption_policy(held_resources, request_available):
    """
    Prevents the no-preemption condition.

    If the complete request cannot be satisfied, the process
    releases its held resources and retries later.
    """

    if request_available:
        return {
            "action": "grant",
            "released": [],
            "reason": "Requested resources are available."
        }

    return {
        "action": "release_and_wait",
        "released": held_resources.copy(),
        "reason": (
            "Release held resources and retry when the full "
            "request can be satisfied."
        )
    }


def prevention_summary():
    """
    Returns the four deadlock conditions, prevention policies,
    and their trade-offs for display in the dashboard.
    """

    return [
        {
            "Condition": "Mutual exclusion",
            "Policy": (
                "Share resources where safe, such as read-only files."
            ),
            "Trade-off": "Some devices cannot be shared."
        },
        {
            "Condition": "Hold and wait",
            "Policy": (
                "Request all resources together, or release "
                "held resources before requesting more."
            ),
            "Trade-off": "Lower utilization and longer waits."
        },
        {
            "Condition": "No preemption",
            "Policy": (
                "Release held resources if the full request "
                "cannot be satisfied."
            ),
            "Trade-off": "Not suitable for every resource type."
        },
        {
            "Condition": "Circular wait",
            "Policy": (
                "Enforce a global order and request resources "
                "in increasing order only."
            ),
            "Trade-off": "Less flexibility in resource requests."
        }
    ]
