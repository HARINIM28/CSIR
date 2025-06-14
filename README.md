Task 1: ESP32 to ThingSpeak and Google Sheets Integration

What It Does:

   Reads temperature and humidity data using ESP32.
   Sends data to:
      ThingSpeak for real-time graph visualization.
      Google Sheets using a Google Apps Script for cloud logging.

Key Features:

   Wi-Fi enabled data transmission from ESP32.
   Cloud-based data logging in Google Sheets.
   Real-time data visualization on ThingSpeak.
   Automatic timestamping of each entry.

Task 2: Python GUI for Real-Time Data Visualization

What It Does:
   Builds a Python GUI application to fetch and display temperature and humidity data from ESP through serial communication.

Key Features:

   GUI created using Tkinter.
   Real-time graphs using Matplotlib.
   Export latest data to CSV.
   Add custom or institution logo to the interface.
   Set temperature alert threshold.
   Toggle display of temperature and humidity.
   Save graph as PNG image.


Task3: ESP32 Voltage Monitor

What It Does
   This project uses an ESP32 and ADS1115 (16-bit ADC) to read analog voltage from a potentiometer, and displays it in a Python GUI.

Key Features:

   Reads 0–3.3V analog input using ADS1115 (channel A0)
   Sends data from ESP32 over serial (only after START command)
   GUI plots real-time graph, shows voltage with progress bar
   Allows saving graph and exporting data as CSV
