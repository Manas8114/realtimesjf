import tkinter as tk
from tkinter import ttk
import psutil
import os
import time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from pandas.plotting import scatter_matrix

class ProcessInfo:
    def __init__(self, pid, create_time, arrival_time, burst_time, completion_time):
        self.pid = pid
        self.create_time = create_time
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.completion_time = completion_time

    def age(self, aging_factor):
        self.burst_time += aging_factor

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

def sjf_schedule(processes, aging_factor):
    for process in processes:
        process.age(aging_factor)

    processes.sort(key=lambda x: x.burst_time)
    return processes

def calculate_average_turnaround_time(processes):
    total_turnaround_time = sum(abs(process.completion_time - process.arrival_time) for process in processes)
    return total_turnaround_time / len(processes)

def retrieve_process_info():
    processes = [p for p in psutil.process_iter(['pid', 'create_time', 'cpu_times']) if p.info['create_time'] > 0]
    process_info_text.delete(1.0, tk.END)
    
    # Define column widths
    col_widths = [10, 15, 15, 15, 15]
    
    # Create headers
    headers = ["PID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time"]
    
    # Format headers
    header_format = " | ".join(["{:<{}}".format(headers[i], col_widths[i]) for i in range(len(headers))])
    
    process_info_text.insert(tk.END, header_format + "\n")
    
    # Add divider line
    divider = ["-" * width for width in col_widths]
    divider_format = " | ".join(["{:<{}}".format(divider[i], col_widths[i]) for i in range(len(divider))])
    
    process_info_text.insert(tk.END, divider_format + "\n")
    
    process_list = []
    for process in processes:
        info = get_process_info(process)
        if info:
            process_list.append(info)
    
    # Aging factor (e.g., increase priority every 10 seconds)
    aging_factor = 10
    
    sjf_processes = sjf_schedule(process_list, aging_factor)
    current_time = 0
    for process in sjf_processes:
        completion_time = current_time + process.burst_time
        process.completion_time = completion_time
        turnaround_time = abs(process.completion_time - process.arrival_time)
        
        
        # Format process information
        process_info_format = " | ".join(["{:<{}}".format(str(process.pid), col_widths[0]),
                                          "{:<{}}".format(str(process.arrival_time), col_widths[1]),
                                          "{:<{}}".format(str(process.burst_time), col_widths[2]),
                                          "{:<{}}".format(str(completion_time), col_widths[3]),
                                          "{:<{}}".format(str(turnaround_time), col_widths[4])])
        
        process_info_text.insert(tk.END, process_info_format + "\n")
        current_time = completion_time
    avg_turnaround_time = calculate_average_turnaround_time(sjf_processes)
    
    divider_format = " | ".join(["{:<{}}".format(divider[i], col_widths[i]) for i in range(len(divider))])
    process_info_text.insert(tk.END, divider_format + "\n")
    process_info_text.insert(tk.END, "Average Turnaround Time: {:.2f}\n".format(avg_turnaround_time))


def create_pairplot():
    data = pd.read_csv('process_info.csv')
    sns.set(style="whitegrid")
    scatter_matrix(data, diagonal='kde', c='blue')  # You can change the color 'c' to any color you prefer
    plt.suptitle('Multivariate Analysis: Pairplot of Process Data')
    plt.show()


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

# Add a button to retrieve process info
retrieve_button = ttk.Button(process_info_frame, text="Retrieve Process Info", command=retrieve_process_info)
retrieve_button.pack(pady=10)

# Graphical Analysis Tab
graphical_analysis_frame = ttk.Frame(notebook)
graphical_analysis_button = ttk.Button(graphical_analysis_frame, text="Create Pairplot", command=create_pairplot)
graphical_analysis_button.pack(pady=10)
graphical_analysis_frame.pack(fill="both", expand=True)
notebook.add(graphical_analysis_frame, text="Graphical Analysis")

# Start the Tkinter main loop
root.mainloop()
