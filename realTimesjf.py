import tkinter as tk
from tkinter import ttk
import psutil
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

class ProcessScheduler:
    def __init__(self, aging_factor=10):
        self.process_list = []
        self.aging_factor = aging_factor

    def age_processes(self):
        for process in self.process_list:
            process.age(self.aging_factor)

    def sjf_schedule(self):
        self.process_list.sort(key=lambda x: x.burst_time)

    def calculate_average_turnaround_time(self):
        total_turnaround_time = sum(abs(process.completion_time - process.arrival_time) for process in self.process_list)
        return total_turnaround_time / len(self.process_list)

    def retrieve_process_info(self):
        processes = [p for p in psutil.process_iter(['pid', 'create_time', 'cpu_times']) if p.info['create_time'] > 0]
        self.process_list = [self.get_process_info(process) for process in processes if self.get_process_info(process)]

        self.age_processes()
        self.sjf_schedule()

    def get_process_info(self, process):
        try:
            pid = process.pid
            create_time = process.create_time()
            current_time = int(time.time())
            arrival_time = current_time - create_time
            burst_time = process.cpu_times().user + process.cpu_times().system
            return ProcessInfo(pid, create_time, arrival_time, burst_time, 0)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    def create_pairplot(self):
        data = pd.DataFrame([
            {'PID': process.pid, 'Arrival Time': process.arrival_time, 'Burst Time': process.burst_time,
             'Completion Time': process.completion_time, 'Turnaround Time': abs(process.completion_time - process.arrival_time)}
            for process in self.process_list
        ])

        sns.set(style="whitegrid")
        scatter_matrix(data, diagonal='kde', c='blue')
        plt.suptitle('Multivariate Analysis: Pairplot of Process Data')
        plt.show()

class ProcessInfoTab(ttk.Frame):
    def __init__(self, parent, process_scheduler):
        super().__init__(parent)
        self.process_scheduler = process_scheduler

        self.process_info_text = tk.Text(self, wrap=tk.WORD, height=20, width=70)
        self.process_info_text.pack(padx=10, pady=10, fill="both", expand=True)

        retrieve_button = ttk.Button(self, text="Retrieve Process Info", command=self.retrieve_process_info)
        retrieve_button.pack(pady=10)

        rearrange_button = ttk.Button(self, text="Rearrange by Arrival Time", command=self.rearrange_by_arrival_time)
        rearrange_button.pack(pady=10)

    def retrieve_process_info(self):
        self.process_scheduler.retrieve_process_info()
        self.update_process_info_text()

    def rearrange_by_arrival_time(self):
        self.process_scheduler.process_list.sort(key=lambda x: x.arrival_time)
        self.update_process_info_text()

    def update_process_info_text(self):
        self.process_info_text.delete(1.0, tk.END)

        # Define column widths
        col_widths = [10, 15, 15, 15, 15]

        # Create headers
        headers = ["PID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time"]

        # Format headers
        header_format = " | ".join(["{:<{}}".format(headers[i], col_widths[i]) for i in range(len(headers))])

        self.process_info_text.insert(tk.END, header_format + "\n")

        # Add divider line
        divider = ["-" * width for width in col_widths]
        divider_format = " | ".join(["{:<{}}".format(divider[i], col_widths[i]) for i in range(len(divider))])

        self.process_info_text.insert(tk.END, divider_format + "\n")

        for process in self.process_scheduler.process_list:
            # Format process information
            process_info_format = " | ".join([
                "{:<{}}".format(str(process.pid), col_widths[0]),
                "{:<{}}".format(str(process.arrival_time), col_widths[1]),
                "{:<{}}".format(str(process.burst_time), col_widths[2]),
                "{:<{}}".format(str(process.completion_time), col_widths[3]),
                "{:<{}}".format(str(abs(process.completion_time - process.arrival_time)), col_widths[4])
            ])

            self.process_info_text.insert(tk.END, process_info_format + "\n")

        avg_turnaround_time = self.process_scheduler.calculate_average_turnaround_time()

        divider_format = " | ".join(["{:<{}}".format(divider[i], col_widths[i]) for i in range(len(divider))])
        self.process_info_text.insert(tk.END, divider_format + "\n")
        self.process_info_text.insert(tk.END, "Average Turnaround Time: {:.2f}\n".format(avg_turnaround_time))

class GraphicalAnalysisTab(ttk.Frame):
    def __init__(self, parent, process_scheduler):
        super().__init__(parent)
        self.process_scheduler = process_scheduler

        create_pairplot_button = ttk.Button(self, text="Create Pairplot", command=self.create_pairplot)
        create_pairplot_button.pack(pady=10)

    def create_pairplot(self):
        self.process_scheduler.create_pairplot()

def main():
    root = tk.Tk()
    root.title("SJF Process Scheduler")

    process_scheduler = ProcessScheduler()

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    process_info_tab = ProcessInfoTab(notebook, process_scheduler)
    notebook.add(process_info_tab, text="Process Info")

    graphical_analysis_tab = GraphicalAnalysisTab(notebook, process_scheduler)
    notebook.add(graphical_analysis_tab, text="Graphical Analysis")

    root.mainloop()

if __name__ == "__main__":
    main()
