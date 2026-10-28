# OS Deadlock Lab — Streamlit Dashboard

Six modules: (1) Deadlock Prevention, (2) Deadlock Avoidance with Banker's Algorithm and a single-instance RAG illustration, (3) Deadlock Detection & Recovery, (4) Deadlock Ignorance / Ostrich Algorithm, (5) Mini-games, and (6) Team & Learning Resources.

## Run on Windows / VS Code
1. Extract this ZIP and open the `Deadlock_Learning_Dashboard` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create a virtual environment: `python -m venv .venv`
4. Activate: `\.venv\Scripts\Activate.ps1` (PowerShell). If blocked, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.
5. Install dependencies: `python -m pip install --upgrade pip` then `pip install -r requirements.txt`
6. Launch: `python -m streamlit run app.py`
7. Open the local URL printed in terminal (normally `http://localhost:8501`).
8. Run tests: `python -m pytest tests -v`

## Add instructor notes / PPT
Put authorized instructor PDFs/PPT/PPTX in `class_notes/`. The uploaded images include notebook reference photos, but no instructor PPT/notes file was supplied. Add the actual PPT when available. `assets/` contains the provided college logo, guide photo, deadlock concept diagram and notebook photos.

## Correctness notes
- Need = Maximum − Allocation.
- Requests exceeding Need are invalid; requests within Need but exceeding Available are waiting/deferred.
- Requests within Need and Available are temporarily simulated. If unsafe, the request is denied and the original state is retained.
- Detection uses outstanding requests, allocation, and available vectors. A graph cycle is not conclusive for every multiple-instance resource model.
- Prevention controls are educational simulations. Resource sharing/preemption depends on resource semantics.
- Confirm group PRNs before submission: repeated PRNs were preserved exactly as supplied.
