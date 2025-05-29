IoT-based Real-Time Temperature and Humidity Monitoring System


📌 Project Overview

This project allows real-time monitoring of temperature and humidity using an ESP32 microcontroller, with data logged to Google Sheets and visualized on ThingSpeak and a custom Python GUI built with Tkinter and Matplotlib.



Components & Technologies Used

- ESP32 Microcontroller
- Google Apps Script + Google Sheets(cloud logging)
- ThingSpeak(real-time data visualization)
- Python (Tkinter + Matplotlib) (GUI visualization)
- HTTP GET Requests, REST APIs

Features

- Real-time data collection 
- Dual cloud-based visualization (ThingSpeak and Google Sheets)
- Desktop GUI to fetch and display live graphs
- Auto-refresh every 15 seconds
- Error handling and feedback messages

How It Works

1. ESP32 generates random temperature and humidity data.
2. Sends data to:
   - Google Apps Script Web App → logs into Google Sheets
   - ThingSpeak Channel → for live data charting
3. Python GUI:
   - Fetches recent data from ThingSpeak via API
   - Displays temperature and humidity in line graphs



Setup Instructions

ESP32 (Arduino IDE)

1. Install the WiFi libraries.
2. Modify the code with:
   - Your WiFi credentials
   - ThingSpeak API Key
   - Google Apps Script URL
3. Upload code to ESP32.

Google Apps Script

1. Create a new Apps Script project in Google Sheets.
2. Paste the `doGet(e)` function from this repo.
3. Deploy as web app:
   - Access: "Anyone, even anonymous"
   - Copy the deployed URL

Python GUI

1. Install required packages:
   
   pip install requests matplotlib


2. Run the GUI script:

   python3 thingspeak_gui.py
  

ThingSpeak Dashboard

* Channel ID: `2973674`
* API Key: `NIHBA3PD0MFLWVQZ`
* Visualizes: Temperature (Field1), Humidity (Field2)

