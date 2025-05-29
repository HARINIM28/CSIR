import requests
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

CHANNEL_ID = "2973674"
READ_API_KEY = "NIHBA3PD0MFLWVQZ"
RESULTS = 10  
REFRESH_INTERVAL_MS = 15000 

def fetch_thingspeak_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results={RESULTS}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            feeds = response.json().get("feeds", [])
            temperature_data = []
            humidity_data = []
            time_data = []
            for entry in feeds:
                temp = entry.get("field1")
                hum = entry.get("field2")
                time = entry.get("created_at", "")[-8:]  
                if temp and hum:
                    temperature_data.append(float(temp))
                    humidity_data.append(float(hum))
                    time_data.append(time)
            return time_data, temperature_data, humidity_data
        else:
            print("Failed to fetch data:", response.status_code)
            return [], [], []
    except Exception as e:
        print("Error:", e)
        return [], [], []

def plot_data():
    time_data, temp_data, hum_data = fetch_thingspeak_data()
    if not time_data:
        result_label.config(text="No data to display.")
        return

    result_label.config(text="Data fetched successfully.")

    fig.clear()
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    ax1.plot(time_data, temp_data, marker='o', color='orange')
    ax1.set_title("Temperature (°C)")
    ax1.set_ylabel("Temperature")
    ax1.grid(True)

    ax2.plot(time_data, hum_data, marker='o', color='blue')
    ax2.set_title("Humidity (%)")
    ax2.set_ylabel("Humidity")
    ax2.set_xlabel("Time")
    ax2.grid(True)

    fig.tight_layout()
    canvas.draw()

def auto_refresh():
    plot_data()
    root.after(REFRESH_INTERVAL_MS, auto_refresh)

# GUI Setup
root = tk.Tk()
root.title("ThingSpeak Real-Time Data Viewer")
root.geometry("800x600")

frame = ttk.Frame(root)
frame.pack(pady=20)

button = ttk.Button(frame, text="Fetch and Plot Data", command=plot_data)
button.pack(pady=5)

result_label = ttk.Label(frame, text="")
result_label.pack()

fig = plt.Figure(figsize=(8, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Start auto-refresh loop
auto_refresh()

root.mainloop()
