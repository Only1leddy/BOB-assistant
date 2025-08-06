## LDMEC - LDMEC - LDMEC - LDMEC - LDMEC ##
###########################################

BOB-assistant
Bob is a custom assistant I've built to run on my Raspberry Pi. It uses Python and camera input to interact with the real world. The project includes features like camera streaming, object detection, RTSP/TCP support, and inverted video. This repo is for keeping it safe, sharing updates, and tracking improvements over time.

**main.py is for a pico that emulates a usb keyboard also mine has fan attached to gpio 16

**BOB 7.4.4 will run alone or if website requered run/start with gui_bob that starts flask witch opens bob and runs web page.

#########################################################################################

✨ Features
🎙️ Voice-activated command system using speech_recognition and espeak

🔥 Heating control via ESP microcontroller and temperature readings from a Pico W

🤖 AI chatbot using HuggingFace Transformers and DeepSeek via Ollama

🎥 Video and photo capture using Picamera2

📺 YouTube search and play via yt-dlp

🧠 Object/person detection with Hailo AI inference on RTSP and local camera feeds

📋 Voice-logged to-do list (a.k.a. weed list 🌿)

🎵 Media playback, fan control, and volume adjustment through serial commands

🚨 "Panic mode" with AI-powered person detection for security

📝 Logging system to record voice-based commands or notes

#######################################################################################

🔧 Technologies Used
Python 3.11+

Raspberry Pi + Picamera2 + Hailo AI

transformers, speech_recognition, requests, subprocess, serial, psutil

Voice TTS via espeak

Chatbot backend using ollama + DeepSeek-R1 7B model

#####################################################################################

📦 System Requirements
Raspberry Pi (tested on Pi 4/5)

Mic + Speakers

ESP device for heating control

Optional: Hailo accelerator for object detection






  
