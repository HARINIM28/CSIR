import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial, threading, time, csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

PORT = '/dev/cu.usbserial-110'
BAUD = 115200
CMD_START, CMD_STOP = "START\n", "STOP\n"
INTERVAL = 1000  # ms
DATA_SIZE = 50

class SensorMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3-Sensor Monitor")
        self.running = False
        self.serial_conn = None
        self.data_lock = threading.Lock()
        self.s1, self.s2, self.s3, self.times = [], [], [], []
        self.vars = {
            "show1": tk.BooleanVar(value=True),
            "show2": tk.BooleanVar(value=True),
            "show3": tk.BooleanVar(value=True),
            "min1": tk.StringVar(value="10"), "max1": tk.StringVar(value="90"),
            "min2": tk.StringVar(value="60"), "max2": tk.StringVar(value="140"),
            "min3": tk.StringVar(value="-15"), "max3": tk.StringVar(value="15")
        }

        self.setup_ui()
        self.update_plot()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def setup_ui(self):
        top = tk.Frame(self.root); top.pack()
        btn_style = {"padx": 10, "pady": 5}
        tk.Button(top, text="Start", bg="green", fg="white", command=self.start, **btn_style).pack(side=tk.LEFT)
        tk.Button(top, text="Stop", bg="red", fg="white", command=self.stop, **btn_style).pack(side=tk.LEFT)
        tk.Button(top, text="Save Graph", command=self.save_plot).pack(side=tk.LEFT)
        tk.Button(top, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT)

        left = tk.Frame(self.root); left.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.val_labels = [tk.Label(left, text=f"Sensor {i+1}: --") for i in range(3)]
        for lbl in self.val_labels: lbl.pack(anchor="w")

        self.checks = [
            ttk.Checkbutton(left, text="Show Sensor 1", variable=self.vars["show1"], command=self.update_plot),
            ttk.Checkbutton(left, text="Show Sensor 2", variable=self.vars["show2"], command=self.update_plot),
            ttk.Checkbutton(left, text="Show Sensor 3", variable=self.vars["show3"], command=self.update_plot)
        ]
        for chk in self.checks: chk.pack(anchor="w")

        self.status = tk.Label(left, text="Status: Normal", fg="green")
        self.status.pack(pady=5)

        for i in range(3):
            tk.Label(left, text=f"S{i+1} Min:").pack(anchor="w")
            tk.Entry(left, textvariable=self.vars[f"min{i+1}"], width=6).pack(anchor="w")
            tk.Label(left, text=f"S{i+1} Max:").pack(anchor="w")
            tk.Entry(left, textvariable=self.vars[f"max{i+1}"], width=6).pack(anchor="w")

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def start(self):
        if self.running: return
        try:
            self.serial_conn = serial.Serial(PORT, BAUD, timeout=1)
            for _ in range(5): self.serial_conn.readline()
        except:
            messagebox.showerror("Error", "Cannot open serial port.")
            return

        self.send(CMD_START)
        self.running = True
        self.start_time = time.time()
        self.clear_data()
        threading.Thread(target=self.read_serial, daemon=True).start()
        self.root.after(INTERVAL, self.update_loop)

    def stop(self):
        if self.running:
            self.running = False
            self.send(CMD_STOP)

    def send(self, cmd):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(cmd.encode())

    def read_serial(self):
        while self.running:
            try:
                line = self.serial_conn.readline().decode().strip()
                if line.startswith("INFO") or not line: continue
                parts = list(map(float, line.split(',')))
                if len(parts) == 3:
                    t = round(time.time() - self.start_time, 2)
                    with self.data_lock:
                        self.s1.append(parts[0])
                        self.s2.append(parts[1])
                        self.s3.append(parts[2])
                        self.times.append(t)
                        for lst in [self.s1, self.s2, self.s3, self.times]:
                            if len(lst) > DATA_SIZE: lst.pop(0)
            except: continue

    def update_loop(self):
        if self.running:
            self.update_plot()
            self.root.after(INTERVAL, self.update_loop)

    def update_plot(self):
        with self.data_lock:
            t, s1, s2, s3 = list(self.times), list(self.s1), list(self.s2), list(self.s3)

        self.ax.clear()
        alerts = []

        def check(val, minv, maxv, idx):
            if val is None: return "--"
            try:
                minv, maxv = float(minv), float(maxv)
                if val < minv: alerts.append(f"S{idx+1} LOW")
                elif val > maxv: alerts.append(f"S{idx+1} HIGH")
                return f"{val:.1f}"
            except: return "Err"

        vals = [s1[-1] if s1 else None, s2[-1] if s2 else None, s3[-1] if s3 else None]
        for i, val in enumerate(vals):
            text = check(val, self.vars[f"min{i+1}"].get(), self.vars[f"max{i+1}"].get(), i)
            self.val_labels[i].config(text=f"Sensor {i+1}: {text}")

        if alerts:
            self.status.config(text="Alert: " + ", ".join(alerts), fg="red")
        else:
            self.status.config(text="Status: Normal", fg="green")

        if t:
            if self.vars["show1"].get(): self.ax.plot(t, s1, label="Sensor 1")
            if self.vars["show2"].get(): self.ax.plot(t, s2, label="Sensor 2")
            if self.vars["show3"].get(): self.ax.plot(t, s3, label="Sensor 3")
            self.ax.legend()

        self.ax.set_title("Live Sensor Data")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Value")
        self.ax.grid(True)
        self.canvas.draw_idle()

    def save_plot(self):
        if not self.times: return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path: self.fig.savefig(path)

    def export_csv(self):
        if not self.times: return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Sensor 1", "Sensor 2", "Sensor 3"])
                for i in range(len(self.times)):
                    writer.writerow([self.times[i], self.s1[i], self.s2[i], self.s3[i]])

    def clear_data(self):
        with self.data_lock:
            self.s1.clear(), self.s2.clear(), self.s3.clear(), self.times.clear()

    def close(self):
        self.stop()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorMonitorApp(root)
    root.mainloop()
