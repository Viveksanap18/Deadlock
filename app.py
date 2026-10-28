
# ==========================================================
# 1. IMPORTS
# ==========================================================
# Streamlit builds the interactive web application.
# Pandas displays tables. Plotly draws the resource-allocation graph.
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import the algorithms implemented in the algorithms/ folder.
from algorithms.banker import calculate_need, safety_algorithm, request_resources
from algorithms.detection import detect_deadlock, recover_by_terminating
from algorithms.prevention import (
    resource_order_check,
    hold_and_wait_check,
    preemption_policy,
    prevention_summary,
)

# ==========================================================
# 2. PAGE CONFIGURATION AND NAVIGATION
# ==========================================================
st.set_page_config(
    page_title="OS Deadlock Lab | MITAOE",
    page_icon="🔐",
    layout="wide",
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

with st.sidebar:
    if __import__("pathlib").Path("assets/college_logo.png").exists():
        st.image("assets/college_logo.png", use_container_width=True)

    st.markdown("## OS Deadlock Lab")
    st.caption("Operating Systems • Interactive Learning")

    st.session_state.theme = st.radio(
        "Appearance",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
    )

    theme = st.session_state.theme

    slide = st.radio(
        "Navigate modules",
        [
            "1 · Deadlock Prevention",
            "2 · Deadlock Avoidance",
            "3 · Detection & Recovery",
            "4 · Deadlock Ignorance",
            "5 · Deadlock Games",
            "6 · Team & Resources",
        ],
    )

    st.divider()
    st.caption("MIT Academy of Engineering • Alandi")

# Apply the selected appearance.
if theme == "Dark":
    st.markdown(
        "<style>.stApp{background:#101827;color:#edf2f7}"
        "[data-testid='stSidebar']{background:#111f32}"
        "[data-testid='stMetric']{background:#1c2b40;padding:14px;"
        "border-radius:12px}.stButton button{border-radius:10px}</style>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<style>.stApp{background:#f5f8fc;color:#172033}"
        "[data-testid='stSidebar']{background:#edf3fb}"
        "[data-testid='stMetric']{background:white;padding:14px;"
        "border-radius:12px;border:1px solid #e3eaf4}"
        ".stButton button{border-radius:10px}</style>",
        unsafe_allow_html=True,
    )


# ==========================================================
# 3. REUSABLE HELPER FUNCTIONS
# ==========================================================
# Display a consistent heading for each module.
def heading(kicker, title, subtitle):
    st.caption(kicker.upper())
    st.title(title)
    st.write(subtitle)
    st.divider()


# Display a video and its description.
def video(url, title):
    st.subheader("Watch & learn")
    st.video(url)
    st.caption(title)


# Provide an expandable place for revision notes.
def notes_area(key):
    with st.expander("📚 Instructor notes / class PPT", expanded=False):
        st.write(
            "Put instructor-authorized PDF/PPT/PPTX files in the "
            "`class_notes/` folder. No instructor PPT was included "
            "in the uploaded files, so no class notes are embedded yet."
        )
        st.text_area(
            "My revision notes",
            key=f"notes_{key}",
            placeholder="Write your notes here...",
        )


# ==========================================================
# MODULE 1: DEADLOCK PREVENTION
# ==========================================================
if slide.startswith("1"):
    heading(
        "Module 01 · Prevention",
        "Deadlock Prevention Lab",
        "Learn how to prevent deadlocks by breaking at least one "
        "of the four necessary conditions.",
    )

    st.info(
        "How to use this lab: Read the concept, enter the values, "
        "click the test button, and read the explanation."
    )

    # Step 1: Explain the four necessary conditions for deadlock.
    st.subheader("Step 1 — Understand the four conditions")

    conditions = [
        (
            "1. Mutual Exclusion",
            "Only one process can use a non-shareable resource at a time.",
            "Prevention idea: Share resources only when technically safe.",
        ),
        (
            "2. Hold and Wait",
            "A process holds one resource while waiting for another.",
            "Prevention idea: Request resources together or release held "
            "resources before waiting.",
        ),
        (
            "3. No Preemption",
            "A resource cannot normally be taken away forcibly.",
            "Prevention idea: Reclaim resources when they can safely "
            "be taken back.",
        ),
        (
            "4. Circular Wait",
            "Processes wait in a circular chain for resources held "
            "by one another.",
            "Prevention idea: Enforce one global resource order.",
        ),
    ]

    condition_columns = st.columns(4)

    for column, (title, meaning, policy) in zip(condition_columns, conditions):
        with column:
            st.markdown(f"### {title}")
            st.write(meaning)
            st.caption(policy)

    st.warning(
        "Prevention policies aim to ensure that at least one necessary "
        "deadlock condition cannot hold. These controls are educational "
        "simulations."
    )

    st.divider()

    # Step 2: Select which prevention policy to simulate.
    st.subheader("Step 2 — Choose a prevention method")

    mode = st.selectbox(
        "Which concept do you want to practise?",
        [
            "Circular Wait — Global Resource Order",
            "Hold and Wait — Request Resources Together",
            "No Preemption — Release and Retry",
        ],
        help="Choose a concept to see its inputs, rule, and result.",
    )

    resources = ["A", "B", "C"]

    # Method 1: Prevent circular wait using a fixed resource order.
    if mode == "Circular Wait — Global Resource Order":
        st.markdown("### Method 1: Global Resource Ordering")
        st.write(
            "Example global order: A → B → C. "
            "All processes must follow the same order."
        )

        held = st.multiselect(
            "1. Resources currently held by the process",
            options=resources,
            default=["B"],
            help="These are the resources the process already owns.",
        )

        requested = st.selectbox(
            "2. Resource requested next",
            options=resources,
            help="This is the next resource the process wants to acquire.",
        )

        order_text = st.selectbox(
            "3. Global resource order",
            options=["A → B → C", "B → C → A", "C → A → B"],
            help="Every process must follow this selected order.",
        )

        order = order_text.split(" → ")

        with st.expander("What do these values mean?"):
            st.write("**Held resources:** resources already owned.")
            st.write("**Requested resource:** the next resource wanted.")
            st.write("**Global order:** the fixed order for requesting resources.")

        if st.button("Check Resource Order", key="check_order", type="primary"):
            result = resource_order_check(held, requested, order)

            if result["allowed"]:
                st.success("Request allowed")
            else:
                st.error("Request blocked")

            st.write("**Reason:**", result["reason"])

            if held:
                highest_held = max(order.index(resource) for resource in held)
                requested_position = order.index(requested)

                st.write(
                    "**Highest position among held resources:**",
                    highest_held + 1,
                )
                st.write(
                    "**Position of requested resource:**",
                    requested_position + 1,
                )

                if requested_position < highest_held:
                    st.warning(
                        "The requested resource comes before a resource "
                        "already held, so it violates the global order."
                    )
                else:
                    st.info("The requested resource follows the global order.")
            else:
                st.info(
                    "The process holds no resources, so this request "
                    "does not violate the selected order."
                )

        with st.expander("Worked example"):
            st.write("Order: A → B → C; Held: B; Requested: A.")
            st.write(
                "A comes before B, so the request is blocked to enforce "
                "the global order."
            )

    # Method 2: Prevent hold-and-wait by requesting resources together.
    elif mode == "Hold and Wait — Request Resources Together":
        st.markdown("### Method 2: Prevent Hold and Wait")
        st.write(
            "The process should obtain its complete requested set together. "
            "If it cannot, it must release resources it already holds before waiting."
        )

        held = st.multiselect(
            "1. Resources currently held",
            options=resources,
            default=["A"],
            key="hw_held",
            help="Resources the process currently owns.",
        )

        requested = st.multiselect(
            "2. New resources requested",
            options=resources,
            default=["B"],
            key="hw_requested",
            help="Resources the process wants to obtain together.",
        )

        all_available = st.checkbox(
            "3. The entire requested set is available now",
            value=False,
            help="Check only if every requested resource can be granted together.",
        )

        with st.expander("What does availability mean?"):
            st.write("**Checked:** the complete request can be granted now.")
            st.write("**Unchecked:** the complete request cannot be granted now.")

        if st.button(
            "Check Hold-and-Wait Policy",
            key="check_hold_wait",
            type="primary",
        ):
            if not requested:
                st.warning("Select at least one requested resource.")
            else:
                result = hold_and_wait_check(held, requested, all_available)

                if result["allowed"]:
                    st.success("Policy allows the request")
                else:
                    st.error("Request blocked by the policy")

                st.write("**Reason:**", result["reason"])

                if held and not all_available:
                    st.write(
                        "**Next step:** Release the held resources, "
                        "then retry the complete request."
                    )
                elif held:
                    st.write(
                        "**Next step:** The request is available now, "
                        "so this simulation allows it."
                    )
                else:
                    st.write(
                        "**Next step:** The process holds no resources "
                        "while waiting."
                    )

        with st.expander("Worked example"):
            st.write("Held: A; Requested: B; Entire request available: No.")
            st.write(
                "The process must release A before waiting for B "
                "under this policy."
            )

    # Method 3: Simulate releasing resources and retrying later.
    else:
        st.markdown("### Method 3: Release Resources and Retry")
        st.write(
            "If the complete new request cannot be granted, this simulation "
            "asks the process to release its held resources and retry later."
        )

        st.warning(
            "Real systems can only safely reclaim certain resources. "
            "This policy is not suitable for every device or operation."
        )

        held = st.multiselect(
            "1. Resources currently held",
            options=resources,
            default=["A"],
            key="preempt_held",
            help="These resources may be released by the simulation.",
        )

        request_available = st.checkbox(
            "2. The entire new request can be granted now",
            value=False,
            key="preempt_available",
            help="Check if the full request can be satisfied immediately.",
        )

        if st.button(
            "Simulate Release and Retry",
            key="check_preemption",
            type="primary",
        ):
            result = preemption_policy(held, request_available)

            if result["action"] == "grant":
                st.success("Action: Grant request")
            else:
                st.warning("Action: Release resources and retry")

            st.write("**Reason:**", result["reason"])
            st.write("**Resources released:**", result["released"])

            if result["action"] == "release_and_wait":
                st.info(
                    "This is a simulation; it does not release "
                    "real operating-system resources."
                )

        with st.expander("Worked example"):
            st.write("Held: A, B; Entire new request available: No.")
            st.write(
                "The simulation releases A and B, then asks the process "
                "to retry later."
            )

    # Step 3: Display the summary of conditions and trade-offs.
    st.divider()
    st.subheader("Step 3 — Compare prevention methods")

    st.dataframe(
        pd.DataFrame(prevention_summary()),
        use_container_width=True,
        hide_index=True,
    )

    # Display the optional diagram only when the asset exists.
    if __import__("pathlib").Path("assets/deadlock_conditions.png").exists():
        st.image(
            "assets/deadlock_conditions.png",
            caption="Reference diagram: methods of handling deadlocks",
            use_container_width=True,
        )

    st.info(
        "These controls are educational policy simulations. "
        "Sharing and preemption depend on resource semantics."
    )

    video(
        "https://www.youtube.com/live/wIqn3n2ATQ0",
        "Instructor-linked lecture video",
    )
    notes_area("prevention")


# ==========================================================
# MODULE 2: DEADLOCK AVOIDANCE AND BANKER'S ALGORITHM
# ==========================================================
elif slide.startswith("2"):
    heading(
        "Module 02 · Avoidance",
        "Deadlock Avoidance",
        "Check a resource request before granting it. Grant only if "
        "the simulated state remains safe.",
    )

    st.markdown(
        "**Banker's Algorithm** supports multiple instances of resource "
        "types. A **Resource Allocation Graph (RAG)** cycle-based avoidance "
        "approach is suitable for single-instance resources when claim edges are used."
    )

    # Configure the number of processes and resource types.
    n = st.number_input("Number of processes", 1, 8, 5)
    m = st.number_input("Number of resource types", 1, 4, 3)
    names = [chr(65 + i) for i in range(m)]

    # Default Allocation and Maximum matrices.
    da = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2],
    ]
    dm = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3],
    ]

    alloc_seed = [
        [da[i][j] if i < 5 and j < 3 else 0 for j in range(m)]
        for i in range(n)
    ]
    max_seed = [
        [dm[i][j] if i < 5 and j < 3 else 1 for j in range(m)]
        for i in range(n)
    ]

    with st.expander("Configure Allocation, Maximum and Available", expanded=True):
        a_df = st.data_editor(
            pd.DataFrame(
                alloc_seed,
                index=[f"P{i}" for i in range(n)],
                columns=names,
            ),
            key=f"avoid_a_{n}_{m}",
            num_rows="fixed",
            use_container_width=True,
        )

        mx_df = st.data_editor(
            pd.DataFrame(
                max_seed,
                index=[f"P{i}" for i in range(n)],
                columns=names,
            ),
            key=f"avoid_m_{n}_{m}",
            num_rows="fixed",
            use_container_width=True,
        )

        avcols = st.columns(m)
        available = [
            int(
                avcols[j].number_input(
                    f"Available {names[j]}",
                    min_value=0,
                    value=[3, 3, 2, 1][j],
                    key=f"avoid_av_{j}",
                )
            )
            for j in range(m)
        ]

    # Calculate Need and check whether the current state is safe.
    try:
        allocation = [
            [int(v) for v in row]
            for row in a_df.values.tolist()
        ]
        maximum = [
            [int(v) for v in row]
            for row in mx_df.values.tolist()
        ]

        need = calculate_need(allocation, maximum)
        result = safety_algorithm(allocation, maximum, available)

        st.subheader("Need = Maximum − Allocation")
        st.dataframe(
            pd.DataFrame(
                need,
                index=[f"P{i}" for i in range(n)],
                columns=names,
            ),
            use_container_width=True,
        )

        col1, col2 = st.columns(2)
        col1.metric("State", "SAFE" if result["safe"] else "UNSAFE")
        col2.metric(
            "Processes in completion prefix",
            len(result["partial_sequence"]),
        )

        if result["safe"]:
            st.success("Safe sequence: " + " → ".join(result["safe_sequence"]))
        else:
            st.error(
                "No complete safe sequence. Unfinished: "
                + ", ".join(result["unfinished"])
            )

        st.subheader("Safety algorithm steps")
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Step": item["step"],
                        "Process": item["process"],
                        "Work": str(item["work"]),
                    }
                    for item in result["work_updates"]
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

        # Let the user simulate a request by a process.
        st.subheader("Evaluate a resource request")
        process = st.selectbox(
            "Requesting process",
            list(range(n)),
            format_func=lambda value: f"P{value}",
        )

        request_columns = st.columns(m)
        request = [
            int(
                request_columns[j].number_input(
                    f"Request {names[j]}",
                    min_value=0,
                    value=0,
                    key=f"avoid_req_{j}",
                )
            )
            for j in range(m)
        ]

        if st.button("Simulate request", type="primary"):
            outcome = request_resources(
                allocation,
                maximum,
                available,
                process,
                request,
            )

            if outcome["status"] == "granted":
                st.success(outcome["message"])
                st.write("Updated Available:", outcome["available"])
                st.write(
                    "Safe sequence:",
                    " → ".join(outcome["safety_result"]["safe_sequence"]),
                )
            elif outcome["status"] == "waiting":
                st.warning(outcome["message"])
                st.write("State unchanged.")
            elif outcome["status"] == "denied":
                st.error(outcome["message"])
                st.write(
                    "Original state retained; temporary allocation "
                    "was not committed."
                )
            else:
                st.error(outcome["message"])

    except (ValueError, TypeError) as error:
        st.error(f"Invalid configuration: {error}")

    # Draw a Resource Allocation Graph cycle illustration.
    st.subheader("RAG cycle illustration · single-instance resources")

    positions = {
        "P0": (0, 1),
        "R0": (1, 1),
        "P1": (1, 0),
        "R1": (0, 0),
    }
    edges = [
        ("P0", "R0"),
        ("R0", "P1"),
        ("P1", "R1"),
        ("R1", "P0"),
    ]
    fig = go.Figure()

    for source, target in edges:
        x0, y0 = positions[source]
        x1, y1 = positions[target]
        fig.add_annotation(
            x=x1,
            y=y1,
            ax=x0,
            ay=y0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowcolor="#e45756",
        )

    for node, (x, y) in positions.items():
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[node],
                textposition="middle center",
                marker=dict(
                    size=54,
                    color="#b9d8ff" if node.startswith("P") else "#ffd99b",
                    line=dict(width=2, color="#344054"),
                ),
                showlegend=False,
            )
        )

    fig.update_layout(
        height=330,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False, range=[-0.5, 1.5]),
        yaxis=dict(visible=False, range=[-0.5, 1.5]),
    )
    st.plotly_chart(fig, use_container_width=True)

    video(
        "https://www.youtube.com/watch?v=JTgP3mblSB4",
        "Banker's Algorithm / avoidance video",
    )
    video("https://youtu.be/7gMLNiEz3nw", "Additional avoidance video")
    notes_area("avoidance")


# ==========================================================
# MODULE 3: DEADLOCK DETECTION AND RECOVERY
# ==========================================================
elif slide.startswith("3"):
    heading(
        "Module 03 · Detection & Recovery",
        "Deadlock Detection and Recovery",
        "Detection checks outstanding requests; recovery changes the "
        "state to break the wait.",
    )

    st.markdown(
        "**Detection:** periodically checks outstanding requests against "
        "available resources. **Recovery:** terminate a process or preempt "
        "a resource where safe, then rerun detection."
    )

    st.warning(
        "The example uses an outstanding-request detection algorithm "
        "with two single-instance resource types."
    )

    # Example: P0 holds A and requests B; P1 holds B and requests A.
    allocation = [[1, 0], [0, 1]]
    request = [[0, 1], [1, 0]]
    available = [0, 0]

    st.subheader("Example state")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Allocation")
        st.dataframe(
            pd.DataFrame(
                allocation,
                index=["P0", "P1"],
                columns=["A", "B"],
            )
        )

    with col2:
        st.write("Outstanding Request")
        st.dataframe(
            pd.DataFrame(
                request,
                index=["P0", "P1"],
                columns=["A", "B"],
            )
        )

    with col3:
        st.write("Available")
        st.write(available)

    if st.button("Run deadlock detection", type="primary"):
        result = detect_deadlock(allocation, request, available)
        st.session_state.det_result = result

        if result["detected"]:
            st.error("Deadlock detected: " + ", ".join(result["deadlocked"]))
        else:
            st.success("No deadlock detected.")

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Step": item["step"],
                        "Process": item["process"],
                        "Work": str(item["work"]),
                    }
                    for item in result["work_updates"]
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )

    # Demonstrate recovery by terminating one process.
    st.subheader("Recovery simulation")
    victim = st.selectbox(
        "Choose process to terminate",
        [0, 1],
        format_func=lambda value: f"P{value}",
    )

    if st.button("Terminate process and release its resources"):
        outcome = recover_by_terminating(
            allocation,
            request,
            available,
            victim,
        )

        st.success(
            f"Terminated {outcome['terminated']}; "
            f"released {outcome['released']}."
        )
        st.write("Available after recovery:", outcome["available_after"])

        if outcome["detected"]:
            st.warning(
                "Remaining deadlocked processes: "
                + ", ".join(outcome["deadlocked"])
            )
        else:
            st.success("No deadlock remains in the simulated state.")

    video("https://youtu.be/LTr1a643FiQ", "Deadlock detection and recovery video")
    notes_area("detection")


# ==========================================================
# MODULE 4: DEADLOCK IGNORANCE (OSTRICH APPROACH)
# ==========================================================
elif slide.startswith("4"):
    heading(
        "Module 04 · Deadlock Ignorance",
        "Deadlock Ignorance · Ostrich Algorithm",
        "Ignore deadlocks when they are rare and prevention or detection "
        "overhead is judged more costly.",
    )

    st.markdown(
        "In this simplified teaching model, the OS assumes deadlock will "
        "be rare; if one occurs, an administrator may restart the "
        "application or system. Rebooting is a blunt option, not a universal OS rule."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Advantages")
        st.write("Simple • Low runtime overhead • No continuous detection cost")

    with col2:
        st.markdown("### Risks")
        st.write(
            "Unsaved work may be lost • Resources may remain blocked • "
            "Unsuitable for critical systems"
        )

    frequency = st.radio(
        "How often is deadlock expected?",
        ["Very rarely", "Occasionally", "Frequently"],
    )
    impact = st.radio(
        "Cost of a deadlock",
        ["Low", "Medium", "High"],
    )

    if st.button("Discuss strategy"):
        if frequency == "Very rarely" and impact == "Low":
            st.success(
                "Ignoring deadlocks may be a reasonable trade-off "
                "in a non-critical system."
            )
        else:
            st.warning(
                "Consider prevention, avoidance, or detection/recovery "
                "because impact or frequency is not negligible."
            )

    video(
        "https://youtu.be/HP1JuTbJMN4",
        "Deadlock ignorance / Ostrich Algorithm video",
    )
    notes_area("ignorance")


# ==========================================================
# MODULE 5: GIVE QUIZ
# ==========================================================
elif slide.startswith("5"):
    heading(
        "Module 05 · Assessment",
        "Give Quiz",
        "Answer five questions covering deadlock prevention, avoidance, "
        "detection, recovery, and ignorance.",
    )

    # Each question has four choices, one correct answer, and an explanation.
    quiz_questions = [
        {
            "question": (
                "1. Which technique prevents circular wait in a "
                "resource-allocation system?"
            ),
            "options": [
                "Allow processes to request resources in any order",
                "Enforce a global order for requesting resources",
                "Allocate every resource to one process",
                "Ignore the order in which resources are requested",
            ],
            "answer": "Enforce a global order for requesting resources",
            "explanation": (
                "A global resource order requires processes to request "
                "resources in increasing order. This prevents circular wait."
            ),
        },
        {
            "question": (
                "2. What does the Need matrix represent in Banker's Algorithm?"
            ),
            "options": [
                "Resources currently available in the system",
                "Resources already allocated to each process",
                "The additional resources each process may still need to finish",
                "The total number of processes waiting for resources",
            ],
            "answer": (
                "The additional resources each process may still need to finish"
            ),
            "explanation": (
                "Need = Maximum − Allocation. It represents the additional "
                "resources a process may require to finish."
            ),
        },
        {
            "question": (
                "3. In Banker's Algorithm, when is a state considered safe?"
            ),
            "options": [
                "When every resource is available immediately",
                "When at least one process has completed already",
                "When no process currently requests resources",
                "When a sequence exists in which every process can finish",
            ],
            "answer": (
                "When a sequence exists in which every process can finish"
            ),
            "explanation": (
                "A safe state has a safe sequence. Each process can obtain "
                "its remaining Need, finish, and release its allocated "
                "resources for later processes."
            ),
        },
        {
            "question": (
                "4. In the detection algorithm, what happens when no "
                "unfinished process can satisfy its outstanding request?"
            ),
            "options": [
                "The algorithm increases Available automatically",
                "The algorithm declares every process completed",
                "The algorithm stops and identifies unfinished processes "
                "as deadlocked under the model's assumptions",
                "The algorithm grants each process its maximum claim",
            ],
            "answer": (
                "The algorithm stops and identifies unfinished processes "
                "as deadlocked under the model's assumptions"
            ),
            "explanation": (
                "If no unfinished process can proceed, the algorithm stops. "
                "Processes left unfinished are identified as deadlocked "
                "under the detection model used in this project."
            ),
        },
        {
            "question": (
                "5. What is the main idea behind the Ostrich Algorithm?"
            ),
            "options": [
                "Ignore deadlocks when the expected handling cost exceeds "
                "the expected cost of ignoring them",
                "Prevent every deadlock by ordering resources",
                "Run Banker's Algorithm after every resource request",
                "Terminate every process whenever a resource is requested",
            ],
            "answer": (
                "Ignore deadlocks when the expected handling cost exceeds "
                "the expected cost of ignoring them"
            ),
            "explanation": (
                "The Ostrich approach accepts the possibility of deadlock "
                "when handling it may cost more than ignoring it, "
                "particularly when deadlocks are rare."
            ),
        },
    ]

    # Keep quiz status and attempt number across Streamlit reruns.
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if "quiz_attempt" not in st.session_state:
        st.session_state.quiz_attempt = 0

    # Incrementing the attempt number creates fresh answer widgets on reset.
    if st.button("Start / Reset Quiz", key="reset_quiz"):
        st.session_state.quiz_submitted = False
        st.session_state.quiz_attempt += 1
        st.rerun()

    st.markdown("### Answer all five questions")
    st.caption(
        "Select one answer for each question, then submit to see "
        "your score and explanations."
    )

    # A form prevents evaluation after every answer selection.
    with st.form(f"deadlock_quiz_form_{st.session_state.quiz_attempt}"):
        for index, question in enumerate(quiz_questions):
            st.markdown(f"#### Question {index + 1}")
            st.write(question["question"])

            st.radio(
                "Choose one answer:",
                question["options"],
                index=None,
                key=f"quiz_question_{st.session_state.quiz_attempt}_{index}",
            )

            st.divider()

        submitted = st.form_submit_button(
            "Submit Quiz",
            type="primary",
            use_container_width=True,
        )

    # Evaluate and store the submitted answers.
    if submitted:
        st.session_state.quiz_submitted = True
        st.session_state.quiz_answers = {
            index: st.session_state.get(
                f"quiz_question_{st.session_state.quiz_attempt}_{index}"
            )
            for index in range(len(quiz_questions))
        }

    # Show the score and feedback after submission.
    if st.session_state.quiz_submitted:
        answers = st.session_state.get("quiz_answers", {})

        score = sum(
            answers.get(index) == question["answer"]
            for index, question in enumerate(quiz_questions)
        )

        total = len(quiz_questions)
        percentage = (score / total) * 100

        st.divider()
        st.subheader("Your Quiz Result")

        score_col, percentage_col, correct_col = st.columns(3)
        score_col.metric("Score", f"{score} / {total}")
        percentage_col.metric("Percentage", f"{percentage:.0f}%")
        correct_col.metric("Correct Answers", str(score))

        if score == total:
            st.success("Excellent! You answered all five questions correctly.")
        elif score >= 3:
            st.info("Good work! Review the explanations below to improve further.")
        else:
            st.warning("Review Modules 1–4 and try the quiz again.")

        st.subheader("Answer Review")

        for index, question in enumerate(quiz_questions):
            user_answer = answers.get(index)
            correct_answer = question["answer"]
            status = (
                "Correct"
                if user_answer == correct_answer
                else "Review needed"
            )

            with st.expander(f"Question {index + 1}: {status}"):
                st.write(question["question"])
                st.write(
                    "**Your answer:**",
                    user_answer if user_answer is not None else "Not answered",
                )
                st.write("**Correct answer:**", correct_answer)
                st.write("**Explanation:**", question["explanation"])

    # Summarize the topics covered by the quiz.
    with st.expander("Topics covered in this quiz"):
        st.write("1. Deadlock Prevention — global resource ordering")
        st.write("2. Deadlock Avoidance — Need matrix")
        st.write("3. Banker's Algorithm — safe state and safe sequence")
        st.write("4. Deadlock Detection — unfinished processes")
        st.write("5. Deadlock Ignorance — Ostrich Algorithm")


# ==========================================================
# MODULE 6: PROJECT TEAM AND LEARNING RESOURCES
# ==========================================================
else:
    heading(
        "Module 06 · Team & Resources",
        "Project Team and Learning Resources",
        "Operating Systems · Deadlock handling strategies",
    )

    # Display the college logo if the asset exists.
    if __import__("pathlib").Path("assets/college_logo.png").exists():
        st.image("assets/college_logo.png", width=360)

    # Display the project guide's photo and details.
    st.subheader("Project Guide")
    col1, col2 = st.columns([1, 2])

    with col1:
        if __import__("pathlib").Path("assets/guide_photo.png").exists():
            st.image("assets/guide_photo.png", use_container_width=True)

    with col2:
        st.markdown("### Dr. Vijaykumar P. Mantri")
        st.write("Project Guide · MIT Academy of Engineering, Alandi")

    # Display group member details exactly as previously supplied.
    st.subheader("Group Members")

    members = [
        {
            "Name": "Vivek Vilas Sanap",
            "PRN": "202401040091",
            "Roll No.": "91",
        },
        {
            "Name": "Vyankatesh Kulkarni",
            "PRN": "202401040134",
            "Roll No.": "99",
        },
        {
            "Name": "Omkar Vairagkar",
            "PRN": "202401040091",
            "Roll No.": "91",
        },
        {
            "Name": "Sanaskar Chandawar",
            "PRN": "202401040091",
            "Roll No.": "100",
        },
    ]

    st.dataframe(
        pd.DataFrame(members),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Repeated PRNs were preserved exactly as provided; "
        "verify group records before submission."
    )

    # Explain where to put authorized class materials.
    st.subheader("Class notes / PPT")
    st.write(
        "Create `class_notes/` in the project root and place the "
        "instructor's authorized PDF/PPT/PPTX files there. No instructor "
        "notes/PPT were included in the supplied files."
    )

    # Provide the video links for all course topics.
    st.subheader("Video library")

    videos = [
        (
            "https://www.youtube.com/live/wIqn3n2ATQ0",
            "Deadlock prevention lecture",
        ),
        (
            "https://www.youtube.com/watch?v=JTgP3mblSB4",
            "Banker's Algorithm",
        ),
        (
            "https://youtu.be/7gMLNiEz3nw",
            "Deadlock avoidance",
        ),
        (
            "https://youtu.be/LTr1a643FiQ",
            "Detection and recovery",
        ),
        (
            "https://youtu.be/HP1JuTbJMN4",
            "Deadlock ignorance",
        ),
    ]

    for url, label in videos:
        st.markdown(f"- [{label}]({url})")

    notes_area("team")
