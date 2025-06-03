import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import serial
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random 
import time
import csv

SERIAL_PORT = '/dev/cu.usbserial-110' 
BAUD_RATE = 115200
DATA_WINDOW_SIZE = 50
GUI_UPDATE_INTERVAL = 1000  
SERIAL_READ_TIMEOUT = 1.0  

CMD_START_SENDING = "START\n"
CMD_STOP_SENDING = "STOP\n"


class SerialPlotterApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("ESP Temperature & Humidity Monitor")
        self.root.geometry("1100x800")
        self.root.configure(bg="#e6e6fa")

        self.temperatures = []
        self.humidities = []
        self.times = []

        self.running = False
        self.serial_thread = None
        self.data_lock = threading.Lock()
        self.serial_connection = None
        self.start_time_session = 0 

        self.show_temp_var = tk.BooleanVar(value=True)
        self.show_hum_var = tk.BooleanVar(value=True)

        self.min_temp_thresh_var = tk.StringVar(value="15")
        self.max_temp_thresh_var = tk.StringVar(value="35")
        self.min_hum_thresh_var = tk.StringVar(value="30")
        self.max_hum_thresh_var = tk.StringVar(value="70")

        self.setup_ui()
        self._update_button_states()
        self.update_plot_and_values()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        #  Main layout
        top_controls_frame = tk.Frame(self.root, bg="#e6e6fa")
        top_controls_frame.pack(fill=tk.X, pady=5)

        left_panel_frame = tk.Frame(self.root, bg="#e6e6fa", width=200)
        left_panel_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_panel_frame.pack_propagate(False)

        right_panel_frame = tk.Frame(self.root, bg="#e6e6fa")
        right_panel_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = tk.Frame(top_controls_frame, bg="#e6e6fa")
        header_frame.pack(fill=tk.X, pady=(10, 0))

        self.title_label = tk.Label(header_frame, text="ESP Temperature & Humidity Monitor",
                                    font=("Segoe UI", 24, "bold"), bg="#e6e6fa", fg="#4b0082")
        self.title_label.pack(side=tk.LEFT, padx=20)
        try:
           
            img = Image.open("csir logo.jpeg")
            img = img.resize((80, 80), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(img)
            self.logo_label = tk.Label(header_frame, image=self.logo, bg="#e6e6fa")
            self.logo_label.pack(side=tk.RIGHT, padx=20)
        except Exception as e:
            self.logo_label = tk.Label(header_frame, text="Logo N/A", bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 10))
            self.logo_label.pack(side=tk.RIGHT, padx=20)
            print(f"Error loading image: {e}")

        # Buttons
        button_frame = tk.Frame(top_controls_frame, bg="#e6e6fa")
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start_plotting,
                                      bg="#d0f4de", fg="#1b4332", font=("Segoe UI", 11, "bold"),
                                      padx=15, pady=7, relief="flat", bd=0)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_plotting,
                                     bg="#ffd6d6", fg="#a4161a", font=("Segoe UI", 11, "bold"),
                                     padx=15, pady=7, relief="flat", bd=0)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.save_img_button = tk.Button(button_frame, text="Save Graph", command=self.save_graph,
                                         bg="#bae8e8", fg="#000000", font=("Segoe UI", 11, "bold"),
                                         padx=15, pady=7, relief="flat", bd=0)
        self.save_img_button.pack(side=tk.LEFT, padx=10)

        self.export_csv_button = tk.Button(button_frame, text="Export CSV", command=self.export_csv,
                                           bg="#fcd5ce", fg="#000000", font=("Segoe UI", 11, "bold"),
                                           padx=15, pady=7, relief="flat", bd=0)
        self.export_csv_button.pack(side=tk.LEFT, padx=10)

        # Live Value
        live_values_outer_frame = tk.LabelFrame(left_panel_frame, text="Live Readings", bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        live_values_outer_frame.pack(fill=tk.X, pady=(0, 10))

        self.temp_val_label = tk.Label(live_values_outer_frame, text="Temp: -- °C", font=("Segoe UI", 12), bg="#e6e6fa", fg="#333")
        self.temp_val_label.pack(anchor="w", pady=2)
        self.hum_val_label = tk.Label(live_values_outer_frame, text="Hum: -- %", font=("Segoe UI", 12), bg="#e6e6fa", fg="#333")
        self.hum_val_label.pack(anchor="w", pady=2)

        # Plot Options
        plot_options_frame = tk.LabelFrame(left_panel_frame, text="Plot Options", bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        plot_options_frame.pack(fill=tk.X, pady=10)

        self.show_temp_cb = ttk.Checkbutton(plot_options_frame, text="Show Temperature", variable=self.show_temp_var, command=self.update_plot_and_values)
        self.show_temp_cb.pack(anchor="w")
        self.show_hum_cb = ttk.Checkbutton(plot_options_frame, text="Show Humidity", variable=self.show_hum_var, command=self.update_plot_and_values)
        self.show_hum_cb.pack(anchor="w")

        # Threshold Alerts
        thresholds_frame = tk.LabelFrame(left_panel_frame, text="Alert Thresholds", bg="#e6e6fa", fg="#4b0082", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        thresholds_frame.pack(fill=tk.X, pady=10)

        tk.Label(thresholds_frame, text="Min Temp (°C):", bg="#e6e6fa", fg="#000000").grid(row=0, column=0, sticky="w", pady=2)
        self.min_temp_entry = tk.Entry(thresholds_frame, textvariable=self.min_temp_thresh_var, width=7)
        self.min_temp_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=5)

        tk.Label(thresholds_frame, text="Max Temp (°C):", bg="#e6e6fa", fg="#000000").grid(row=1, column=0, sticky="w", pady=2)
        self.max_temp_entry = tk.Entry(thresholds_frame, textvariable=self.max_temp_thresh_var, width=7)
        self.max_temp_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=5)

        tk.Label(thresholds_frame, text="Min Hum (%):", bg="#e6e6fa", fg="#000000").grid(row=2, column=0, sticky="w", pady=2)
        self.min_hum_entry = tk.Entry(thresholds_frame, textvariable=self.min_hum_thresh_var, width=7)
        self.min_hum_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=5)

        tk.Label(thresholds_frame, text="Max Hum (%):", bg="#e6e6fa", fg="#000000").grid(row=3, column=0, sticky="w", pady=2)
        self.max_hum_entry = tk.Entry(thresholds_frame, textvariable=self.max_hum_thresh_var, width=7)
        self.max_hum_entry.grid(row=3, column=1, sticky="ew", pady=2, padx=5)
        thresholds_frame.columnconfigure(1, weight=1)

        self.alert_status_label = tk.Label(left_panel_frame, text="Status: Normal", font=("Segoe UI", 10, "italic"), bg="#e0e0e0", fg="green", relief="sunken", bd=1, anchor="w", padx=5)
        self.alert_status_label.pack(fill=tk.X, pady=(10, 0), ipady=3)

        # Plot
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('#e6e6fa')
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.ax.set_xlabel("Time (s)", fontsize=10, labelpad=8)
        self.ax.set_ylabel("Readings", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.fig.tight_layout(pad=2.0)

    def _update_button_states(self):
        if self.running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def _send_serial_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(command.encode('utf-8'))
                self.serial_connection.flush() 
                print(f"Sent command: {command.strip()}")
                return True
            except serial.SerialException as e:
                messagebox.showerror("Serial Error", f"Failed to send command {command.strip()}: {e}")
                return False
        else:
            messagebox.showerror("Serial Error", "Serial connection not available to send command.")
            return False

    def read_serial_data(self):
      

        while self.running:
            line_bytes = None
            temp_val, hum_val = None, None
            try:
                if not (self.serial_connection and self.serial_connection.is_open):
                    print("Serial connection lost or closed unexpectedly during read.")
                    self.root.after(0, lambda: messagebox.showerror("Serial Error", "Connection lost."))
                    self.running = False 
                    break

                line_bytes = self.serial_connection.readline()

                if not line_bytes: 
                    continue

                decoded_line = line_bytes.decode('utf-8', errors='ignore').strip()

                if decoded_line:
                    parts = decoded_line.split(',')
                    if len(parts) == 2:
                        try:
                            temp_val = float(parts[0])
                            hum_val = float(parts[1])
                        except ValueError:
                            print(f"Warning: Non-numeric data in '{decoded_line}'")
                            continue
                    else:
                        print(f"Warning: Malformed data '{decoded_line}'")
                        continue
                else: 
                    continue

                current_time_elapsed = round(time.time() - self.start_time_session, 2)
                with self.data_lock:
                    self.temperatures.append(temp_val)
                    self.humidities.append(hum_val)
                    self.times.append(current_time_elapsed)

                    self.temperatures = self.temperatures[-DATA_WINDOW_SIZE:]
                    self.humidities = self.humidities[-DATA_WINDOW_SIZE:]
                    self.times = self.times[-DATA_WINDOW_SIZE:]

            except serial.SerialTimeoutException: 
                continue 
            except serial.SerialException as e:
                self.root.after(0, lambda: messagebox.showerror("Serial Error", f"Serial communication error: {e}\nStopping data collection."))
                self.running = False
                break
            except Exception as e:
                print(f"Unexpected error in serial reading loop: {e}")
                
                continue

        print("Serial reading thread finished.")
        
        self.root.after(0, self._update_button_states)
        self.root.after(0, self.update_plot_and_values)


    def start_plotting(self):
        if self.running:
            return

        
        if not (self.serial_connection and self.serial_connection.is_open):
            try:
                print(f"Attempting to open serial port {SERIAL_PORT} at {BAUD_RATE} baud.")
                self.serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=SERIAL_READ_TIMEOUT)
                time.sleep(1.5) 
                print("Serial port opened successfully.")
            except serial.SerialException as e:
                messagebox.showerror("Serial Error", f"Could not open serial port {SERIAL_PORT}:\n{e}")
                self.serial_connection = None 
                return 

        
        if not self._send_serial_command(CMD_START_SENDING):
           
            return

        self.running = True
        self.start_time_session = time.time() # Record session start time
        self._update_button_states()

        with self.data_lock:
            self.temperatures.clear()
            self.humidities.clear()
            self.times.clear()
        self.update_plot_and_values() # Clear plot

        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        self.root.after(GUI_UPDATE_INTERVAL, self.plotter_update_tick)

    def stop_plotting(self):
        if not self.running:
            return

        self.running = False 
        self._update_button_states()

        
        self._send_serial_command(CMD_STOP_SENDING)

        
    def plotter_update_tick(self):
        if self.running:
            self.update_plot_and_values()
            self.root.after(GUI_UPDATE_INTERVAL, self.plotter_update_tick)
        else:
            self.update_plot_and_values()

    def update_plot_and_values(self):
        with self.data_lock:
            times_data = list(self.times)
            temps_data = list(self.temperatures)
            hums_data = list(self.humidities)

        self.ax.clear()
        current_alert_messages = []
        temp_color, hum_color = "black", "black"

        if temps_data:
            latest_temp = temps_data[-1]
            self.temp_val_label.config(text=f"Temp: {latest_temp:.2f} °C")
            try:
                min_t = float(self.min_temp_thresh_var.get())
                max_t = float(self.max_temp_thresh_var.get())
                if latest_temp < min_t:
                    temp_color = "blue"
                    current_alert_messages.append(f"Temp LOW ({latest_temp:.1f} < {min_t:.1f})")
                elif latest_temp > max_t:
                    temp_color = "red"
                    current_alert_messages.append(f"Temp HIGH ({latest_temp:.1f} > {max_t:.1f})")
            except ValueError:
                current_alert_messages.append("Invalid Temp Thresh.")
        else:
            self.temp_val_label.config(text="Temp: -- °C")
        self.temp_val_label.config(fg=temp_color)

        if hums_data:
            latest_hum = hums_data[-1]
            self.hum_val_label.config(text=f"Hum: {latest_hum:.2f} %")
            try:
                min_h = float(self.min_hum_thresh_var.get())
                max_h = float(self.max_hum_thresh_var.get())
                if latest_hum < min_h:
                    hum_color = "orange"
                    current_alert_messages.append(f"Hum LOW ({latest_hum:.1f} < {min_h:.1f})")
                elif latest_hum > max_h:
                    hum_color = "purple"
                    current_alert_messages.append(f"Hum HIGH ({latest_hum:.1f} > {max_h:.1f})")
            except ValueError:
                current_alert_messages.append("Invalid Hum Thresh.")
        else:
            self.hum_val_label.config(text="Hum: -- %")
        self.hum_val_label.config(fg=hum_color)

        if current_alert_messages:
            self.alert_status_label.config(text="Alert: " + "; ".join(current_alert_messages), fg="red", bg="#ffdddd")
        else:
            self.alert_status_label.config(text="Status: Normal", fg="green", bg="#ddffdd")

        plot_title = "Live Sensor Data"
        if self.serial_connection and self.serial_connection.is_open:
            if self.running:
                plot_title += " - Running" if times_data else " - Waiting for data..."
            else: 
                 plot_title += " - Ready" if not times_data else " - Stopped"
        else: 
            plot_title += " - Disconnected"

        self.ax.set_title(plot_title, fontsize=12, pad=10)

        legend_items = []
        if self.show_temp_var.get() and temps_data:
            line_t, = self.ax.plot(times_data, temps_data, label='Temperature (°C)', color='#f72585', linewidth=2, marker='o', markersize=3)
            legend_items.append(line_t)
        if self.show_hum_var.get() and hums_data:
            line_h, = self.ax.plot(times_data, hums_data, label='Humidity (%)', color='#3a0ca3', linewidth=2, marker='o', markersize=3)
            legend_items.append(line_h)

        if legend_items:
            self.ax.legend(handles=legend_items, loc="upper right")

        self.ax.set_xlabel("Time (s)", fontsize=10, labelpad=8)
        self.ax.set_ylabel("Readings", fontsize=10)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw_idle()

    def save_graph(self):
        with self.data_lock:
            if not self.times:
                messagebox.showinfo("Save Graph", "No data available to save.")
                return
        try:
            file_path = filedialog.asksaveasfilename(
                title="Save Graph As",
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf")]
            )
            if file_path:
                self.fig.savefig(file_path, dpi=300)
                messagebox.showinfo("Success", f"Graph saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save graph: {e}")

    def export_csv(self):
        with self.data_lock:
            if not self.times:
                messagebox.showinfo("Export CSV", "No data available to export.")
                return

            data_to_write = []
           
            min_len = min(len(self.times), len(self.temperatures), len(self.humidities))
            for i in range(min_len):
                data_to_write.append((self.times[i], self.temperatures[i], self.humidities[i]))

        file_path = filedialog.asksaveasfilename(
            title="Export CSV As",
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv")]
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Time (s)", "Temperature (°C)", "Humidity (%)"])
                    writer.writerows(data_to_write)
                messagebox.showinfo("Success", f"CSV exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export CSV: {e}")

    def on_closing(self):
        print("Closing application...")
        if self.running:
            self.running = False 
            self._send_serial_command(CMD_STOP_SENDING) 

        if self.serial_thread and self.serial_thread.is_alive():
            print("Waiting for serial thread to join...")
            self.serial_thread.join(timeout=SERIAL_READ_TIMEOUT + 0.5) 
            if self.serial_thread.is_alive():
                print("Serial thread did not join in time.")

        if self.serial_connection and self.serial_connection.is_open:
            print("Closing serial connection...")
            self.serial_connection.close()
            self.serial_connection = None

        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SerialPlotterApp(root)
    root.mainloop()