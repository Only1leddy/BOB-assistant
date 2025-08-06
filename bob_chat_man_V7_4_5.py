##################################################################################################
## LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC -LDMEC ##
##################################################################################################
##################################################################################################
##----------------------------------------------------------------------------------------------##
##--------#################------ ################-------#################----------------------##
##-------/=================\-----/================\-----/=================\---------------------##
##------/===================\---/==================\---/===================\---B-Barely---------##
##------|=====--------======|---|======------======|---|=====--------======|--------------------##
##------|=====---------=====|---|=====--------=====|---|=====---------=====|---O-Operational----##
##------|=====---------=====/---|=====--------=====|---|=====---------=====/--------------------##
##------|=====--------=====/----|=====--------=====|---|=====--------=====/----B-Butler---------##
##------|=================/-----|=====--------=====|---|=================/----------------------##
##------|=================\-----|=====--------=====|---|=================\----------------------##
##------|=====--------=====\----|=====--------=====|---|=====--------=====\---------------------##
##------|=====---------=====\---|=====--------=====|---|=====---------=====\--------------------##
##------|=====---------=====|---|=====--------=====|---|=====---------=====|- ##    ##  ##### --##
##------|=====--------======|---|======------======|---|=====--------======|-  #   #       #  --##
##------\===================/---\==================/---\===================/-   # #       #   --##
##-------\=================/---- \================/-----\=================/--   ##       #    --##
##--------#################-------################-------#################---___#___##__#__.4.5-##
##----------------------------------------------------------------------------------------------##
##################################################################################################
##################################################################################################
## LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC -LDMEC - LDMEC - LDMEC - LDMEC - LDMEC - LDMEC ##
##################################################################################################
import sys                                           
sys.path.append("/usr/lib/python3/dist-packages")
import libcamera
import speech_recognition as sr
from picamera2 import Picamera2, Preview
import psutil
import os
import time
import random
from time import sleep
from transformers import pipeline
import subprocess
import requests
import platform
import re
import serial
import select
import json
from datetime import datetime

####################################################################################
temperature = 28.0  # Initial temperature value
setting = "Normal"  # Initial setting value
esp_ip = "192.168.0.32"
pico_w_ip = 'http://192.168.0.35:85/temperature'

generator = pipeline('text-generation', model='distilgpt2')
recognizer = sr.Recognizer()

wake_word = "bob"      
sleep_word = "goodbye"
goodbuy = [ "goodbye", "later dude", "peace out Bitches!"]
tt = ["muppet", "dickhead", "fuck wit", "twat", "fool", "love you baby", "fucker"]
weed_list = []
heat = False
setTEMPnum = None
x = 0
heater = False
current_process = None


os.system(f'espeak -s 130 -p 40 -b 100 "Bob ON!"')

######################################################################################
def log(command):
    speak(f'Logging {command} conferm')
    spoken = get_words()
    
    if spoken:
        if spoken == "yes":
            speak("Recording log")
            if len(command) > 10:
                sp = command.split()
                print(sp)
                sp = sp[2:]
                print(f'test:{sp}')
                log = " ".join(sp)
                print(f'test:log:{log}')
                speak(log)
                save_log_entry(log)
        else:
            print(f'nuthing to log bro? {command}?')
            send_web_response("no log in command")
            speak("failed")
            
#############################################################
def read_today_logs(filename="bob_log.txt"):
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_entries = []
    
    try:
        with open(filename, "r") as file:
            for line in file:
                if line.startswith(f"[{today_str}"):
                    today_entries.append(line.strip())
                    
    except FileNotFoundError:
        print("No log file found.")
    
    for enrty in today_entries:
        enrty = enrty.split(" ")
        enrty = enrty[1:]
        enrty = " ".join(enrty)
        print(enrty)
        speak(enrty)
    

######################################################################################
def Mpass():
    print("opening muti pass")
    subprocess.Popen(["/usr/bin/python3", "/home/leddy/bob/Muti_cam_ld.py"])

######################################################################################
def Mpass_off():
    subprocess.call(["pkill", "-f", "Muti_cam_ld.py"])

    #kill_processes_by_name(["Muti_cam_ld.py"])

######################################################################################
def run(videoInput):
    
    query = videoInput
    video_id = subprocess.check_output(
        ["yt-dlp", f"ytsearch:{query}", "--get-id", "--quiet"]
    ).decode().splitlines()[0]

    url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
    #os.system(f"xdg-open \"{url}\"")
    subprocess.Popen(["xdg-open", url])
######################################################################################
def stop_ffplay():
    """Kill any running ffplay process."""
    global current_process
    if current_process and current_process.poll() is None:  # Check if process is still running
        print("Stopping existing ffplay process...")
        current_process.terminate()  # Try to terminate gracefully
        try:
            current_process.wait(timeout=2)  # Wait for it to stop
        except subprocess.TimeoutExpired:
            print("Force killing ffplay...")
            current_process.kill()  # Force kill if it doesn't stop
        current_process = None  # Clear the process handle

######################################################################################
def heat_is_on_song():
    """Play a song while ensuring only one instance runs at a time."""
    global current_process
    stop_ffplay()  # Ensure no previous process is running
    print("Starting new ffplay process...")
    current_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "output.mp3"])

######################################################################################       
def play_heat_on_sound():
    """Play a song while ensuring only one instance runs at a time."""
    global current_process
    stop_ffplay()  # Ensure no previous process is running
    print("Starting new ffplay process...")
    process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", "HeatON.m4a"])

######################################################################################
def send_update(var_name, value):
    url = "http://127.0.0.1:8000/update_vars"
    payload = {var_name: value}
    try:
        requests.post(url, json=payload, timeout=5)
    except requests.exceptions.ConnectionError:
        print("ERROR E001: Cannot connect to Flask server at 127.0.0.1:8000. Is it running?")
    except requests.exceptions.Timeout:
        print("ERROR E002: Connection to Flask server timed out.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR E003: Unexpected error during send_update: {e}")

######################################################################################
def send_web_response(text):
    print(json.dumps({"response": text}))

############################################################################
def check_for_messages():
    global heat, setTEMPnum, heater
    """Check for new messages from stdin and parse JSON."""
    ready, _, _ = select.select([sys.stdin], [], [], 0)

    if ready:
        try:
            line = sys.stdin.readline().strip()
            if line:
                data = json.loads(line)
                print(f"Received from GUI (type: {type(data)}): {data}")

                if isinstance(data, str):
                    data = json.loads(data)

                if isinstance(data, dict):
                    message = data.get("message", "").lower()
                    heating = data.get("heating", None)
                    temperature = data.get("temperature", None)

                    # ✅ Only update heater if explicitly provided
                    if "heater" in data:
                        heater = data["heater"]
                        if heater:
                            heatON()
                            send_update("heat", True)
                        else:
                            heatOFF()
                            send_update("heat", False)

                    # ✅ Same for heating and temp
                    if heating is not None:
                        heat = heating
                    if temperature is not None:
                        setTEMPnum = temperature

                    print(f"Updated heat: {heat}, temperature: {setTEMPnum}")
                    return message
                else:
                    print(f"Error: Expected dict but got {type(data)}")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {line}, Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    return None  # No message

########################################################################################
def check_for_messages1():
    global heat, setTEMPnum, heater
    """Check for new messages from stdin and parse JSON."""
    ready, _, _ = select.select([sys.stdin], [], [], 0)

    if ready:
        try:
            line = sys.stdin.readline().strip()  # Read one line of input
            #print(f"Raw input received in Bob Assistant: {line}")  # Debugging print

            if line:
                data = json.loads(line)  # Parse JSON
                print(f"Received from GUI (type: {type(data)}): {data}")  # Debugging print

                if isinstance(data, str):  # Check if JSON parsing failed
                    print("Error: JSON data is still a string, trying again...")
                    data = json.loads(data)  # Parse again if needed

                if isinstance(data, dict):  # Only process if it's a dictionary
                    # Extract values
                    message = data.get("message", "").lower()
                    heating = data.get("heating", False)
                    temperature = data.get("temperature", None)
                    heater = data.get("heater", False)
                    # Use the received variables in Bob Assistant
                    
                    if heater:
                        heatON()                        
                        send_update("heat", True)
                    if not heater:
                        heatOFF()
                        send_update("heat", False)
                        
                        
                    heat = heating
                    setTEMPnum = temperature if temperature is not None else setTEMPnum
                    
                    print(f"Updated heat: {heat}, temperature: {setTEMPnum}")  # Debugging
                    return message  # Return the message for processing
                else:
                    print(f"Error: Expected a dictionary, but got {type(data)}")

        except json.JSONDecodeError as e:
            print(f"Invalid JSON received: {line}, Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    return None  # No new message

###############################################################################
def vol_up():
    subprocess.run(["amixer", "set", "Master", "10%+"])
    
###############################################################################
def vol_down():
    subprocess.run(["amixer", "set", "Master", "10%-"])

###############################################################################
def mute():  
    subprocess.run(["amixer", "set", "Master", "toggle"])

###############################################################################
def pause():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"pause\n")
        print("Command sent to Pico [spacebar]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")
        
    ser.close()

###############################################################################
def next_l():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"next_l\n")
        print("Command sent to Pico [next_left]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()

###############################################################################
def next_r():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"next_r\n")
        print("Command sent to Pico [next_right]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()
###############################################################################
def fan_on():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"blow\n")
        print("Command sent to Pico [blow]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()

###############################################################################
def fan_off():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
        
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"suck\n")
        print("Command sent to Pico [suck]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()

##################################################################################
def full_screen():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
    
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"F11\n")
        print("Command sent to Pico [full]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()
    
##################################################################################
def close_vid():
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
    
    if not ser.is_open:
        ser.open()
        sleep(1)
    try:
        ser.write(b"exit\n")
        print("Command sent to Pico [exit]")
    except serial.SerialException as e:
        print(f"Error writing to serial port: {e}")

    ser.close()
        
#################################################################################
def get_words():
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening.....GO")
        sound = recognizer.listen(source, timeout=5)
        try:
            spoken = recognizer.recognize_google(sound).lower()
            print(f"Heard: {spoken}")
            
        except sr.UnknownValueError:
            print("Didn't understand")
            speak("cansiled video input too slow")
            sleep(0.2)
            spoken = "no"
            return
        
        except sr.RequestError:
            print("Speech recognition API unavailable.")                
            sleep(0.2)
            return
        
        except TypeError:
            print("Didn't understand the question momn.")
            speak("Type error cansile")
            os.system('espeak -s 120 -p 60 -b 100 "Type error cansile"')                
            sleep(0.2)
            return
        return spoken

##################################################################################
def stop_video():
    if platform.system() == "Linux":
        os.system("killall eom")
        os.system("pkill -f xdg-open")
        speak("image closed")
    

##################################################################################
def stop_pic():
    if platform.system() == "Linux":
        os.system("killall eom")
        os.system("pkill -f xdg-open")
        speak("image closed")
    
###################################################################################
def open_vid():
    speak("witch video")
    parth = get_words()
    print(parth)
    speak("opening  {parth}")
    if parth:
        parth = parth + ".mp4"
        img_path = parth
    else:    
        img_path = "BOB_VID.mp4"
        speak("video not found, heres a video tho")
    
    if not os.path.exists(img_path):
        print("Error: video not found or cannot be loaded.")
        speak("cant or cant be asked")
        return


    if platform.system() == "Linux":
        os.system(f'xdg-open "{img_path}" &') 
    elif platform.system() == "Darwin": 
        os.system(f'open "{img_path}" &')
    elif platform.system() == "Windows":
        os.system(f'start "" "{img_path}"')
    
    speak("playing video")
    
###################################################################################
def show_pic2():
    speak("witch image")
    parth = get_words()
    print(parth)
    speak(f"opening  {parth}")
    if parth:
        parth = parth + ".jpg"
        img_path = parth
    else:    
        img_path = "BOB_IMG.jpg"
        speak("image not found, heres a pic tho")
    
    if not os.path.exists(img_path):
        print("Error: Image not found or cannot be loaded.")
        speak("cant or cant be asked")
        return


    if platform.system() == "Linux":
        os.system(f'xdg-open "{img_path}" &') 
    elif platform.system() == "Darwin": 
        os.system(f'open "{img_path}" &')
    elif platform.system() == "Windows":
        os.system(f'start "" "{img_path}"')
    
    speak("image displayed")
    
###################################################################################
def show_pic():
    img_path = "BOB_IMG.jpg"

    if not os.path.exists(img_path):
        print("Error: Image not found or cannot be loaded.")
        speak("cant or cant be asked")
        return


    if platform.system() == "Linux":
        os.system(f'xdg-open "{img_path}" &')
    elif platform.system() == "Darwin": 
        os.system(f'open "{img_path}" &')
    elif platform.system() == "Windows":
        os.system(f'start "" "{img_path}"')

    speak("image displayed")
###################################################################################

###################################################################################
def record_video():    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for lenth of video....")
        lenth_in = recognizer.listen(source, timeout=5)
        try:
            lenth = recognizer.recognize_google(lenth_in).lower()
            print(f"Heard: {lenth}")
        except sr.UnknownValueError:
            print("Didn't understand")
            speak("cansiled video input too slow")
            
            sleep(0.2)
            return
        except sr.RequestError:
            print("Speech recognition API unavailable")
            speak("goolge is fucking about")
            sleep(0.2)
            return
        except TypeError:
            print("Didn't understand the question")
            speak("Type error cansile")
            
            sleep(0.2)
            return
        
    match = re.search(r'\d+', lenth)
    if match:
        lenth = int(match.group())
        speak(f"will record for {lenth} seconds")
    else:
        return
        
    duration = int(lenth)
    if duration:
        picam2 = Picamera2()
        config = picam2.create_video_configuration(main={"size": (2048, 1536)}, lores={"size": (320, 240)}, encode="main")
        sleep(0.2)
        picam2.configure(config)
        speak("Recording!")
        picam2.start_and_record_video("BOB_VID.mp4", duration=duration)
  
        print(f"Recording for {duration} seconds...")
        
        start_time = time.time()
              
        while time.time() - start_time < duration:
            time.sleep(0.2)

        picam2.stop()
        picam2.close()
        print("Video saved as")
        speak("Video Saved!")

##########################################

def open_outside_cam():
    print("opening camera outside")
    subprocess.Popen([
        "gst-launch-1.0",
        "rtspsrc", "location=rtsp://ledy:leddy@192.168.0.25:8085/h264.sdp", "latency=100",
        "!", "rtph264depay",
        "!", "avdec_h264",
        "!", "autovideosink"
    ])

#######################################################################################
def take_photo(filename="BOB_IMG.jpg"):
    picam2 = Picamera2()
    speak("Say Chesse!")
    
    picam2.start()
    time.sleep(2)
    picam2.capture_file(filename)
    picam2.stop()
    picam2.close()
    print("Photo saved as {filename}")
    speak("CLICK!")


def handle_chatbot_command(command):
    # Remove 'chatbot' from the beginning
    question = command.replace("chatbot", "", 1).strip()

    if not question:
        # No question provided – fall back to microphone
        chatbot(None)
    else:
        # Pass the question to chatbot
        chatbot(question)

#########################################################################################
def get_temp():
    global heat
    try:
        response = requests.get(pico_w_ip, timeout=5)
        response.raise_for_status()

        print("Temperature:", response.text)
        tempNow = response.text
        return tempNow

    except requests.exceptions.HTTPError as http_err:
        print('fucked')
        print(f"HTTP error occurred: {http_err}")
        heatOFF()
        heat = False
        
    except requests.exceptions.ConnectionError:
        print("Connection error: Unable to reach Pico W.")
        heatOFF()
        heat = False
        
    except requests.exceptions.Timeout:
        print("Request timed out.")
        heatOFF()
        heat = False
        
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: {err}")
        heatOFF()
        heat = False
    heatOFF()    
    heat = False
    return None

#########################################################################################
def set_heat():
    global setTEMPnum
    global heat
    heat = True
    setTEMPstrH = None
    os.system(f'espeak -s 120 -p 60 -b 100 "What is the desiered Temp?"')
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for question...")
        TS = recognizer.listen(source, timeout=5)
        try:
            setTEMPstrH = recognizer.recognize_google(TS).lower()
            print(f"Heard: {setTEMPstrH}")
        except sr.UnknownValueError:
            print("Didn't understand the question")
            setTEMPstr = None
            heat = False
            os.system(f'espeak -s 120 -p 60 -b 100 "heating control cansiled input too slow"')
            return
        except sr.RequestError:
            print("Speech recognition API unavailable")
            return
        except TypeError:
            print("Didn't understand the question")
            setTEMPstr = None
            heat = False
            return
        
    tem1 = get_temp()
    
    if tem1 != None:
        os.system(f'espeak -s 120 -p 60 -b 100 "current temp is {tem1} Degrues"')
        
        if setTEMPstrH:
            match = re.search(r'\d+', setTEMPstrH)
            if match:
                setTEMPstrH = int(match.group())
                os.system(f'espeak -s 120 -p 60 -b 100 "heating set too {setTEMPstrH} Degrues"')                  
                setTEMPnum = int(setTEMPstrH)
                print(setTEMPnum)
                TS = None
                send_update("setTEMPnum", setTEMPnum)
            else:
                os.system(f'espeak -s 120 -p 60 -b 100 "heating control cansiled input not understood"')
                heat = False
    else:
        print("Error: Could not get temperature.")
        os.system(f'espeak -s 120 -p 60 -b 100 "Its fucked no temp returned!"')
        heat = False

###################################33
def kill_processes_by_name(names):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(name in ' '.join(cmdline).lower() for name in names):
                print(f"Killing process '{proc.info['name']}' PID {proc.pid}")
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
def ppl_det(video_source):
    subprocess.Popen([
        "python", "/home/leddy/hailo-rpi5-examples/basic_pipelines/fukedBOB_eyes3.py",
        "--source", video_source
    ])
     
def ppl_det2(video_source):
    subprocess.Popen([
        "python", "/home/leddy/hailo-rpi5-examples/basic_pipelines/fukedBOB_eyes3.2.py",
        "--source", video_source
    ])
#########################################################################################
def people_detector_from_ip(rtsp_url, alarm_action=None):
    """
    Continuously detects people from an IP camera RTSP stream and triggers an alarm when a person is detected.

    Args:
        rtsp_url (str): The RTSP URL of the IP camera.
        alarm_action (function): A function to call when a person is detected.
    """
    if not rtsp_url.startswith("rtsp://"):
        print("❌ Invalid RTSP URL. Must start with 'rtsp://'")
        return

    print(f"📡 Starting continuous person detection from IP camera: {rtsp_url}")

    if "venv_hailo_rpi5_examples" not in os.getenv("VIRTUAL_ENV", ""):
        print("📦 Activating virtual environment...")
        subprocess.run(
            "source /home/leddy/hailo-rpi5-examples/setup_env.sh",
            shell=True, executable="/bin/bash"
        )

    detect_command = (
        f"source /home/leddy/hailo-rpi5-examples/setup_env.sh && "
        f"python BOB_eyes2.py --input '{rtsp_url}'"
    )
    detect_process = subprocess.Popen(
        detect_command,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  # combine output for easier read
        shell=True, executable="/bin/bash",
        cwd="/home/leddy/hailo-rpi5-examples/basic_pipelines",
        text=True  # auto-decode stdout lines
    ) 
    try:
        for line in detect_process.stdout:
            line = line.strip().lower()
            if not line:
                continue
            #print(f"📥 {line}")
            if "person" in line:
                print("🚨 Person detected!")
                if alarm_action:
                    alarm_action()
                else:
                    default_ip_alarm()

    except KeyboardInterrupt:
        print("🛑 Stopping detection...")
        detect_process.terminate()
        detect_process.wait()

def default_ip_alarm():
    
    print(" 📢 Default Alarm: Person detected on IP cam!")
    # Example action: play sound or log alert
    # os.system("aplay /home/leddy/ip_alarm.wav")



def start_object_detection():
    if "venv_hailo_rpi5_examples" not in os.getenv("VIRTUAL_ENV", ""):
        print("Activating virtual environment...")
        subprocess.run("source /home/leddy/hailo-rpi5-examples/setup_env.sh", shell=True, executable="/bin/bash")

    print("Starting object detection...")
    detect_process = subprocess.Popen(
    "source /home/leddy/hailo-rpi5-examples/setup_env.sh && python BOB_eyes2.py --input rpi", 
    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    shell=True, executable="/bin/bash", cwd="/home/leddy/hailo-rpi5-examples/basic_pipelines"
    )
    
    time.sleep(12)
    detect_process.terminate()
    stdout, stderr = detect_process.communicate()
    
    print("Raw Output:")
    print(stdout.decode("utf-8"))
    print("Error Output (if any):")
    print(stderr.decode("utf-8"))

    if stdout:
        output = stdout.decode("utf-8").strip().split("\n")
        unique_objects = list(set(output))
        print("Detected Objects:", unique_objects)
        return unique_objects
    else:
        print("No output from detection process")
        return []

#########################################################################################
def controlHeat():
    global setTEMPnum, heat, x, heater
    
    tempNow = get_temp()
    
    if tempNow:    
        tempNow_round = int(tempNow)
        if tempNow_round < setTEMPnum:
            heatON()
            heater = True
            x = 0
        else:
            heatOFF()
            heater = False
            x = 0
    else:
        print("Error: Could not get temperature.")
        os.system(f'espeak -s 120 -p 60 -b 100 "Its fucked no temp returned!"')
        sleep(1)
        os.system(f'espeak -s 120 -p 60 -b 100 "Turning off heating control!"')
        heat = False
        
##############################################################################3
def save_log_entry(message, filename="bob_log.txt"):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    with open(filename, "a") as file:
        file.write(entry)
        
#########################################################################################
def speak(words):
    os.system(f'espeak -s 130 -p 40 -b 100 "{words}"')

#########################################################################################
def heatON():
    send_update("heat", True)
    try:
        response = requests.get(f"http://{esp_ip}/on")
        print("ESP Response:", response.text)
    except:
        speak("Sumthing has gone wrong didnt turn on")

#########################################################################################
def heatOFF():
    send_update("heat", False)
    try:
        response = requests.get(f"http://{esp_ip}/off")
        print("ESP Response:", response.text)
    except:
        os.system('espeak -s 120 -p 60 -b 100 "Sumthing has gone wrong didnt turn off"')
  
#########################################################################################

def chatbot(question=None):
    os.system('espeak -s 120 -p 60 -b 100 "Ok, Chat BOT now"')
    sleep(2)

    # If no text provided, listen with microphone
    if not question:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening for question...")
                audio = recognizer.listen(source, timeout=5)
                question = recognizer.recognize_google(audio).lower()
                print(f"User asked: {question}")
        except sr.UnknownValueError:
            print("Didn't understand the question")
            os.system('espeak -s 120 -p 60 -b 100 "Sorry, I didn\'t get that."')
            return
        except sr.RequestError:
            print("Speech recognition API unavailable")
            os.system('espeak -s 120 -p 60 -b 100 "Google speech service down."')
            return

    # Now run the chatbot regardless of how we got the question
    result = subprocess.run(
        ['ollama', 'run', 'deepseek-r1:7b'],
        input=question.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    output = result.stdout.decode().strip()
    answer = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()

    print(f"Chatbot Response: {answer}")
    os.system(f'espeak -s 120 -p 60 -b 100 "{answer}"')

    # Send reply to web UI if needed
    send_web_response(answer)

    listen_for_command()


def chatbot1(question):
    os.system('espeak -s 120 -p 60 -b 100 "Ok, Chat BOT now"')
    sleep(2)
    
 
        
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for question...")
        audio = recognizer.listen(source, timeout=5)
    try:
        question = recognizer.recognize_google(audio).lower()
        print(f"User asked: {question}")

    
        result = subprocess.run(
            ['ollama', 'run', 'deepseek-r1:7b'],
            input=question.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
            
        output = result.stdout.decode().strip()
        answer = re.sub(r"<think>.*?</think>", "", output, flags=re.DOTALL).strip()
        print(f"Chatbot Response: {answer}")
        os.system(f'espeak -s 120 -p 60 -b 100 "{answer}"')
        listen_for_command()
        
    except sr.UnknownValueError:
        print("Didn't understand the question")
    except sr.RequestError:
        print("Speech recognition API unavailable")

#########################################################################################
def listen_for_command():
    global setTEMPnum
        
    with sr.Microphone() as source:
        print("Listening for a command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        #command = check_for_messages()
        while True:
            
            global heat, x, heater
            
            if heat and x >10:
                controlHeat()
                  
            try:
                command = check_for_messages()
                #print(f'Typed input Command: {command}')

                if not command:
                    mainTA = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(mainTA).lower()
                    print(f"Command heard: {command}")
                                
                if sleep_word in command:
                    g = random.randint(0, 2)
                    os.system(f'espeak -s 120 -p 60 -b 100 "ok {goodbuy[g]}"')
                    print("Sleep word detected. Going to sleep mode.")
                    stop()
#TELL_TIME      #########################################################################################
                elif "what is the time" in command:
                    current_time = time.strftime("%I:%M %p")
                    os.system(f'espeak -s 120 -p 60 -b 100 "The time is {current_time}"')
                    print(f"The time is {current_time}")
                    send_web_response(f"The time is {current_time}")
#U_SAID_FUCK    #########################################################################################
                elif "fuck" in command:
                    slers = len(tt)
                    t = random.randint(0, (slers - 1))
                    os.system(f'espeak -s 120 -p 60 -b 100 "Your a fucking {tt[t]}."')
                    print('your a twat')
#ADD TO LIST    #########################################################################################
                elif "add to list" in command:
                    os.system('espeak -s 120 -p 60 -b 100 "ok what shall i add to the list?"')
                    sleep(1)
                    audio = recognizer.listen(source, timeout=5)
                    weed = recognizer.recognize_google(audio).lower()
                    weed_list.append(weed)
                    os.system(f'espeak -s 120 -p 60 -b 100 "ok {weed} added to the list"')
                    print(f"Heard: {weed}")
                    send_web_response(f"Added '{weed}' to the list.")
#WHAT_ON_LIST   #########################################################################################
                elif "what's on list" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "you have got, {weed_list}"')
                    print(weed_list)
                    send_web_response(weed_list)
#TAKE_OFF_LIST  #########################################################################################
                elif "take off list" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "what shall i take off the list?"')
                    sleep(1)
                    audio = recognizer.listen(source, timeout=5)
                    off = recognizer.recognize_google(audio).lower()
                    if off in weed_list:
                        weed_list.remove(off)
                        os.system(f'espeak -s 120 -p 60 -b 100 "ok i have taken {off} off list"')                       
                    else:
                        os.system(f'espeak -s 120 -p 60 -b 100 "{off} is not in the list"')                        
                    print(off)
#DEEPSEEK       #########################################################################################
                elif "chatbot" in command:
                    send_web_response("Starting chatbot...")
                    handle_chatbot_command(command)
#talklogs    ########################################################################################    
                elif "read captain's log" in command:
                    speak("reporting logs")
                    read_today_logs()                  
#LOGSTUFF       #########################################################################################
                elif "captain's log" in command:
                    log(command)
                    
#SET_HEATING    #########################################################################################
                elif "set temp" in command:
                    set_heat()
                    
#TELL_SETING_HT #########################################################################################
                elif "heating settings" in command:
                    if setTEMPnum:
                        os.system(f'espeak -s 120 -p 60 -b 100 "The desired temp is set too {setTEMPnum} Degrues"')
                    else:
                        os.system(f'espeak -s 120 -p 60 -b 100 "I duno man, you tell me"')
#HEAT_ON        #########################################################################################      
                elif "heat on" in command:
                    response = requests.get(f"http://{esp_ip}/on")
                    print("ESP Response:", response.text)
                    heater = True
                    play_heat_on_sound()
                    print(json.dumps({"response": "heat is ON!!"}))
#HEAT_OFF       #########################################################################################   
                elif "heat off" in command:
                    response = requests.get(f"http://{esp_ip}/off")
                    print("ESP Response:", response.text)
                    os.system('espeak -s 120 -p 60 -b 100 "heater off"')
                    heat = False
                    heater = False
                    send_web_response("Heater turned off.")
#TELL_TEMP      #########################################################################################
                elif "temp" in command:
                    tempNow = get_temp()
                    if tempNow:
                        os.system(f'espeak -s 120 -p 60 -b 100 "Current temp is {tempNow} Degrues"')
                    else:
                        os.system(f'espeak -s 120 -p 60 -b 100 "No temp returned"')
#LOOK_AROUND    #########################################################################################   
                elif "look around" in command:
                    print("Object detection started!")
                    unique_objects = start_object_detection()
                    if unique_objects:
                        sleep(1)
                        print(f'LIST B4 STRIP::{unique_objects}')
                        
                        object_dict = {} 
        
                        for obj in unique_objects:
                            if any(x in obj for x in ["FPS:", "Droprate:", "Avg FPS"]):
                                continue
                            obj = obj.replace("Detection: ", "") 
                            parts = obj.rsplit(" ", 1)
                            if len(parts) == 2:
                                object_name, confidence_str = parts
                                try:
                                    confidence = float(confidence_str)
                                    if object_name not in object_dict or confidence > object_dict[object_name]:
                                        object_dict[object_name] = confidence
                                except ValueError:
                                    pass
                                
                        unique_detected_list = list(object_dict.keys())
                        print(f'LIST AFTER STRIP::{unique_detected_list}')
                        
                        if unique_detected_list:
                            os.system(f'espeak -s 120 -p 60 -b 100 "i see with my little eye! {", ".join(unique_detected_list)}"')
                            summary = ", ".join(unique_detected_list)
                            send_web_response(f"I see: {summary}")
                        else:
                            print("No recognizable objects detected.")
                            send_web_response("No objects detected.")
                            
                     
                            
                    else:
                        print("No objects detected.")
                        
#TAKE_PIC       ######################################################################################### 
                elif "take picture" in command:          
                    take_photo()
                    os.system('espeak -s 120 -p 60 -b 100 "Photo compleate"')
                    send_web_response("Photo taken.")
#RECORD_VIDEO   #########################################################################################    
                elif "record video" in command:
                    record_video()
                    send_web_response("Video recorded.")
#SHOW_PIC       #########################################################################################    
                elif "show pic" in command:
                    show_pic()
                    send_web_response("Picture displayed.")
#PLAY_VIDEO     #########################################################################################    
                elif "open video" in command:
                    open_vid()
#STOP_PIC       #########################################################################################    
                elif "close pic" in command:
                    stop_pic()
                    send_web_response("Image closed.")
#SHOW_PIC2      #########################################################################################    
                elif "open pic" in command:
                    show_pic2()
                    send_web_response("Image opened.")
#FUL_SCREEN_TOG #########################################################################################    
                elif "full screen" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "fullscreen!"')
                    full_screen()
#NEXT_RIGHT     #########################################################################################    
                elif "next please" in command:
                    next_r()
#PLAY_SPACEBAR  #########################################################################################    
                elif "play" in command:
                    pause()
#PAUSE_SPACEBAR #########################################################################################    
                elif "pause" in command:
                    pause()
#NEXT_LEFT      #########################################################################################    
                elif "back please" in command:
                    next_l()
#RENAME_IMG     #########################################################################################    
                elif "rename image" in command:
                    save()
#VOLOME_UP      #########################################################################################    
                elif "louder" in command:
                    vol_up()
                    os.system(f'espeak -s 120 -p 60 -b 100 "vol up!"')
#VOLOME_DOWN    #########################################################################################    
                elif "quiet" in command:
                    vol_down()
                    os.system(f'espeak -s 120 -p 60 -b 100 "vol down!"')
#VOLOME_MUTE    #########################################################################################    
                elif "mute" in command:
                    mute()
                    send_web_response("Volume muted.")
#CLOSE_VID      #########################################################################################    
                elif "close video" in command:
                    close_vid()
#START_SONG     #########################################################################################    
                elif "music" in command:
                    heat_is_on_song()                   
#START_SONG     #########################################################################################    
                elif "panic off" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "panic mode off!"')
                    kill_processes_by_name(["bob_eye3.py", "halrot", "hailo"])
#STOP_SONG      #########################################################################################    
                elif "shut up" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "closing utube!"')
                    stop_ffplay()
                    os.system("pkill -f 'https://www.youtube.com'")
 #START_SONG     #########################################################################################    
                elif "panic over" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "panic mode beta off!"')
                    kill_processes_by_name(["fukedBOB_eyes3.py", "halrot", "hailo"])                  
#UTUBE_PLAY     #########################################################################################    
                elif "utube" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "serching utube now"')
                    if len(command) > 8:
                        sp = command.split()
                        print(sp)
                        sp = sp[1:]
                        videoInput = " ".join(sp)
                        print(f'{videoInput}')
                        run(videoInput)
                    else:
                        print(f'not video to look for ? {command}?')
                        send_web_response("no video in command")
#PANIC_MODE     #########################################################################################    
                elif "panic test" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "panic test beta!"')
                    print("panic mode on beta!")
                    ppl_det2("rtsp://ledy:leddy@192.168.0.25:8085/h264.sdp")
#PANIC_MODE     #########################################################################################    
                elif "panic mode" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "panic on!"')
                    print("panic mode on!")
                    ppl_det("rtsp://ledy:leddy@192.168.0.25:8085/h264.sdp")
                    #people_detector_from_ip("rtsp://ledy:leddy@192.168.0.25:8085/h264.sdp", alarm_action=None)
#INSIDE_CAM     ########################################################################################    
                elif "inside camera" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "inside cam on!"')
                    ppl_det("tcp://192.168.0.14:5000")
#fannnny     ########################################################################################    
                elif "blow me" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "blowing hard fanny on!"')
                    fan_on()
#fannyoff    ########################################################################################    
                elif "suck out" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "stoping fanny no more blowing!"')
                    fan_off()

#########################################################################################    
                elif "outside shut" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "outside cam off!"')
                    kill_processes_by_name(["rtsp"])       
    #########################################################################################    
                elif "outside camera" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "outside cam on"')
                    open_outside_cam()
    ########################################################
                elif "multipass" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "mutipass on!"')
                    Mpass()
      ########################################################
                elif "pass off" in command:
                    os.system(f'espeak -s 120 -p 60 -b 100 "mutipass off!"')
                    Mpass_off()
            except sr.UnknownValueError:
                print("Didn't understand, listening for command...")
                print(f'Heating on?:{heat}, Heater on/off : {heater}')
                
                x +=1
            except sr.RequestError:
                print("API unavailable, check your connection.")
            except sr.WaitTimeoutError:
                print("Timeout reached, still listening...")


#########################################################################################
                


import requests

def stop():
    try:
        url = "http://127.0.0.1:8000/goodbuy"
        response = requests.get(url, timeout=2)
        print("✅ Sent shutdown signal to Bob:", response.text)
    except requests.exceptions.RequestException as e:
        print("❌ Failed to contact Bob:", e)
    
    
    
    
    
    
listen_for_command()








