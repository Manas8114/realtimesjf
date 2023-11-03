import tkinter as tk
from tkinter import ttk
import psutil
import time

class ProcessInfo:
    def __init__(self, pid, create_time, arrival_time, burst_time, completion_time):
        self.pid = pid
        self.create_time = create_time
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.completion_time = completion_time

def get_process_info(process):
    try:
        pid = process.pid
        create_time = process.create_time()
        current_time = int(time.time())
        arrival_time = current_time - create_time
        burst_time = process.cpu_times().user + process.cpu_times().system
        return ProcessInfo(pid, create_time, arrival_time, burst_time, 0)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def sjf_schedule(processes):
    processes.sort(key=lambda x: x.burst_time)
    return processes

def calculate_average_turnaround_time(processes):
    total_turnaround_time = sum(abs(process.completion_time - process.arrival_time) for process in processes)
    return total_turnaround_time / len(processes)

def retrieve_process_info():
    processes = [p for p in psutil.process_iter(['pid', 'create_time', 'cpu_times']) if p.info['create_time'] > 0]
    process_info_text.delete(1.0, tk.END)
    process_info_text.insert(tk.END, "{:<10} | {:<15} | {:<15} | {:<15} | {:<15}\n".format("PID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time"))
    process_info_text.insert(tk.END, "{:<10} | {:<15} | {:<15} | {:<15} | {:<15}\n".format("-" * 10, "-" * 15, "-" * 15, "-" * 15, "-" * 15))  # Divider line
    process_list = []
    for process in processes:
        info = get_process_info(process)
        if info:
            process_list.append(info)
    sjf_processes = sjf_schedule(process_list)
    current_time = 0
    for process in sjf_processes:
        completion_time = current_time + process.burst_time
        process.completion_time = completion_time
        turnaround_time = abs(process.completion_time - process.arrival_time)  # Calculate the absolute value
        process_info_text.insert(tk.END, "{:<10} | {:<15} | {:<15} | {:<15} | {:<15}\n".format(process.pid, process.arrival_time, process.burst_time, completion_time, turnaround_time))
        current_time = completion_time
    avg_turnaround_time = calculate_average_turnaround_time(sjf_processes)
    process_info_text.insert(tk.END, "{:<10} | {:<15} | {:<15} | {:<15} | {:<15}\n".format("-" * 10, "-" * 15, "-" * 15, "-" * 15, "-" * 15))  # Divider line
    process_info_text.insert(tk.END, "Average Turnaround Time: {:.2f}\n".format(avg_turnaround_time))

# Create the main window
root = tk.Tk()
root.title("SJF Process Scheduler")

# Create and configure the notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Process Info Tab
process_info_frame = ttk.Frame(notebook)
process_info_text = tk.Text(process_info_frame, wrap=tk.WORD, height=20, width=70)
process_info_text.pack(padx=10, pady=10, fill="both", expand=True)
process_info_frame.pack(fill="both", expand=True)
notebook.add(process_info_frame, text="Process Info")

# Button to retrieve process info and calculate SJF
retrieve_button = ttk.Button(process_info_frame, text="Retrieve Process Info and Calculate SJF", command=retrieve_process_info)
retrieve_button.pack(pady=10)

# Start the Tkinter main loop
root.mainloop()
