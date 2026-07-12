# realtimesjf

Real-time Shortest Job First (SJF) process scheduler with GUI — monitors live system processes via `psutil`, applies aging + SJF scheduling, visualizes with matplotlib/seaborn.

## Features

- **Live process inspection** — Reads PID, creation time, CPU times from `psutil`
- **Aging factor** — Increases burst time of waiting processes to prevent starvation
- **SJF scheduling** — Sorts by burst time (shortest first)
- **Tkinter GUI** — Two tabs: Process Info table + Graphical Analysis (pairplot)
- **Metrics** — Turnaround time, average turnaround time calculation
- **Visualization** — Seaborn pairplot (KDE diagonals) of process attributes

## Files

| File | Purpose |
|------|---------|
| `realTimesjf.py` | Main application (GUI + scheduler logic) |
| `README.md` | This file |

## Requirements

```bash
pip install psutil matplotlib seaborn pandas scipy
```

Python 3.8+ recommended (install via Microsoft Store or python.org).

## Run

```bash
python realTimesjf.py
```

## GUI Overview

**Tab 1: Process Info**
- "Retrieve Process Info" — Scans live processes, applies aging + SJF, displays table
- "Rearrange by Arrival Time" — Re-sorts table by arrival time
- Table columns: PID, Arrival Time, Burst Time, Completion Time, Turnaround Time
- Footer: Average Turnaround Time

**Tab 2: Graphical Analysis**
- "Create Pairplot" — Opens matplotlib window with multivariate scatter/KDE matrix

## Algorithm

```
1. retrieve_process_info() → psutil.process_iter()
2. For each process:
   - arrival_time = now - create_time
   - burst_time = cpu_times.user + cpu_times.system
3. age_processes() → burst_time += aging_factor (default 10)
4. sjf_schedule() → sort by burst_time ascending
5. calculate_average_turnaround_time()
```

## Notes

- Educational/academic project (OS scheduling simulation)
- Completion time = 0 in current impl (would need actual execution simulation)
- Requires admin/root for full process access on some systems
- Windows: prefer Microsoft Store Python for `psutil` compatibility