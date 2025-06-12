import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import PhotoImage
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os
from PIL import Image, ImageTk 
import matplotlib.ticker as ticker

class VoltageMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Voltage Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f4f7")

        self.serial_port = "/dev/cu.usbserial-10"  
        self.baud_rate = 115200
        self.serial_connection = None
        self.running = False
        self.voltages = []
        self.times = []
        self.start_time = 0

        self._setup_ui()

    def _setup_ui(self):
        # Header 
        header = tk.Frame(self.root, bg="#f0f4f7", height=80)
        header.pack(fill="x")

        tk.Label(header, text="ESP32 Voltage Monitor", font=("Segoe UI", 24, "bold"),
                 bg="#f0f4f7", fg="#222").pack(side="left", padx=20, pady=10)

        try:
            img = Image.open("csir logo.jpeg")
            img = img.resize((60, 60), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.logo, bg="#f0f4f7").pack(side="right", padx=20, pady=10)
        except:
            tk.Label(header, text="Logo N/A", bg="#f0f4f7", fg="#888",
                     font=("Segoe UI", 10)).pack(side="right", padx=20, pady=10)

        # Control Panel
        control_frame = tk.Frame(self.root, bg="#f0f4f7")
        control_frame.pack(pady=10)

        self.start_btn = ttk.Button(control_frame, text="Start", command=self.start_plotting)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_plotting, state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        self.save_btn = ttk.Button(control_frame, text="Save Graph", command=self.save_graph)
        self.save_btn.pack(side="left", padx=10)

        self.export_btn = ttk.Button(control_frame, text="Export CSV", command=self.export_csv)
        self.export_btn.pack(side="left", padx=10)

        # Voltage Display
        self.voltage_label = tk.Label(self.root, text="Voltage: -- V", font=("Segoe UI", 16), bg="#f0f4f7", fg="#333")
        self.voltage_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate", maximum=3.3)
        self.progress.pack(pady=5)

        self.indicator = tk.Label(self.root, text="●", font=("Segoe UI", 24), bg="#f0f4f7", fg="gray")
        self.indicator.pack(pady=2)

        # Graph
        self.fig, self.ax = plt.subplots()
        self.ax.set_title("Live Voltage")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Voltage (V)")
        self.ax.set_ylim(0, 3.3)
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], label="Voltage", color="#0077b6")
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def start_plotting(self):
        try:
            self.serial_connection = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(1.5)
            self.serial_connection.write(b'START\n')
            self.running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.voltages.clear()
            self.times.clear()
            self.start_time = time.time()

            threading.Thread(target=self.read_serial_data, daemon=True).start()
            self.update_plot()
        except serial.SerialException as e:
            self.voltage_label.config(text=f"Error: {e}")

    def stop_plotting(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(b'STOP\n')
                self.serial_connection.close()
            except:
                pass
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def read_serial_data(self):
        while self.running:
            try:
                line = self.serial_connection.readline().decode().strip()
                if "Voltage:" in line:
                    voltage_str = line.split("Voltage:")[1].strip().replace(" V", "")
                    voltage = float(voltage_str)
                    current_time = time.time() - self.start_time
                    self.voltages.append(voltage)
                    self.times.append(current_time)

                    self.voltage_label.config(text=f"Voltage: {voltage:.3f} V")
                    self.progress['value'] = voltage

                    if voltage < 1.5:
                        self.indicator.config(fg="green")
                    elif voltage < 2.8:
                        self.indicator.config(fg="orange")
                    else:
                        self.indicator.config(fg="red")
            except:
                continue

    def update_plot(self):
        if self.running:
            self.line.set_data(self.times, self.voltages)
            self.ax.set_xlim(0, max(10, time.time() - self.start_time))
            self.ax.set_ylim(0, 3.3)
            self.canvas.draw()
            self.root.after(500, self.update_plot)

    def save_graph(self):
        if not self.times:
            messagebox.showinfo("Save Graph", "No data to save.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if file_path:
            self.fig.savefig(file_path, dpi=300)
            messagebox.showinfo("Success", f"Graph saved as:\n{file_path}")

    def export_csv(self):
        if not self.times:
            messagebox.showinfo("Export CSV", "No data to export.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV File", "*.csv")])
        if file_path:
            try:
                with open(file_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Time (s)", "Voltage (V)"])
                    for t, v in zip(self.times, self.voltages):
                        
                        writer.writerow([round(t, 2), round(v, 3)])
                messagebox.showinfo("Success", f"CSV saved:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save CSV:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoltageMonitorApp(root)
    root.mainloop()
