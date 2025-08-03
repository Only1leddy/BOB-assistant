import subprocess
import threading
from flask import Flask, jsonify, request, render_template
import time
import json
import os
# Global variables for heating settings and assistant shell output
heat = False  # Heating state (False means off, True means on)
setTEMPnum = None  # Set temperature (None means no set temperature)
assistant_response = "Assistant is ready to receive messages."
shell_output = ""  # This will store the assistant's shell output
process = None
read_output_thread_started = False
heater = False

def start_assistant():
    """Start the assistant process only if it's not already running."""
    global process, read_output_thread_started

    if process is None or process.poll() is not None:  # Start only if not already running
        print("Starting Assistant...")
        process = subprocess.Popen(
            ["python",
             "/home/leddy/bob/bob_chat_man_V7_4_4.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
            
        )
        
        
        # Start `read_output()` thread only ONCE
        if not read_output_thread_started:
            read_output_thread_started = True  # Mark as started
            threading.Thread(target=read_output, daemon=True).start()
            print("Started read_output() thread")

def read_output():
    """Read and process output from the assistant."""
    global shell_output
    max_lines = 20  # Limit output to the last 20 lines

    while process.poll() is None:  # Read output while process is running
        line = process.stdout.readline().strip()  # Read one line at a time
        if not line:
            continue  # Avoid processing empty lines

        if "Temperature Update:" in line:
            new_temp = line.split(":")[1].strip()
            update_temperature(new_temp)
        try:
            maybe_json = json.loads(line)
            if isinstance(maybe_json, dict) and "response" in maybe_json:
                shell_output += maybe_json["response"] + "\n"
            else:
                shell_output += line + "\n"
        except json.JSONDecodeError:
            shell_output += line + "\n"
       
        # Keep only the last `max_lines` of output
        shell_output_lines = shell_output.split("\n")[-max_lines:]  # Trim to last 20 lines
        shell_output = "\n".join(shell_output_lines)

# Function to update temperature
def update_temperature(new_temp):
    """Update temperature value."""
    global setTEMPnum
    setTEMPnum = float(new_temp)
    print(f"Temperature updated: {setTEMPnum}°C")

# Flask API setup
app = Flask(__name__)

@app.route('/')
def home():
    global heat, heater, setTEMPnum, shell_output

    heat_status = "On" if heat else "Off"
    temp_status = f"{setTEMPnum}°C" if setTEMPnum is not None else "Not Set"
    heater_status = "On" if heater else "Off"  # Assuming 'heater' holds the heater state

    return render_template('home_web_7_4_3.html', heat=heat_status, temperature=temp_status, shell_output=shell_output, heater=heater_status)
    

@app.route('/update_vars', methods=['POST'])
def update_vars():
    global heat, setTEMPnum
    data = request.get_json()

    if "heat" in data:
        heat = data["heat"]

    if "setTEMPnum" in data:
        setTEMPnum = data["setTEMPnum"]
    print(heat)
    print(setTEMPnum)
    return jsonify({"success": True, "heat": heat, "setTEMPnum": setTEMPnum})

@app.route('/home')
def homey():
    return render_template('home_web_7_4_3.html')

@app.route('/links')
def links():
    return render_template('home_web_7_4_3.html')

@app.route('/output')
def output():
    return render_template('home_web_7_4_3.html')


# Endpoint to toggle heating state

@app.route('/toggle_heating', methods=['POST'])
def toggle_heating():
    global heat
    heat = not heat  # Toggle heating state
    return jsonify({"success": True, "heating": "On" if heat else "Off"})

@app.route("/goodbuy", methods=["GET"])
def goodbuy():   
    process.kill()
    print('bob shutdown goodbuy')
    os._exit(0)

@app.route('/get_status', methods=['GET'])
def get_status():
    heat_status = "On" if heat else "Off"  # Use the correct status of the heat
    temp_status = f"{setTEMPnum}°C" if setTEMPnum is not None else "Not Set"  # Correct temperature format
    return jsonify({
        "heating": heat_status,  # Return the correct heating status
        "temperature": temp_status,  # Return the correct temperature status
        "heater": heater  # Keep the heater status as it is
    })




# Endpoint to set the temperature
@app.route('/set_temperature', methods=['POST'])
def set_temperature():
    global setTEMPnum
    data = request.get_json()
    if 'temperature' in data:
        setTEMPnum = data['temperature']
        return jsonify({"success": True, "temperature": setTEMPnum})
    return jsonify({"success": False, "error": "No temperature provided"}), 400

@app.route('/send_message', methods=['POST'])
def send_message():
    global process

    data = request.get_json()
    if 'message' in data:
        message = data['message']
        print(f"Message received in Flask: {message}")

        # Start with only the message
        payload = {
            "message": message
        }

        # Only include heating data if it's a heating-related command
        if any(kw in message for kw in ["heat", "temp", "set", "on", "off"]):
            payload["heating"] = heat
            payload["temperature"] = setTEMPnum
            payload["heater"] = heater

        try:
            print(f"Sending to Bob Assistant: {payload}")
            json.dump(payload, process.stdin)
            process.stdin.write("\n")
            process.stdin.flush()
            print("Message sent to Bob Assistant!")
            return jsonify({"success": True, "response": f"Message sent: {message}"})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": False, "error": "No message provided"}), 400


# Endpoint to send a message to the assistant
@app.route('/send_message', methods=['POST'])
def send_message1():
    global process
    global assistant_response
    
    data = request.get_json()
    if 'message' in data:
        message = data['message']
        print(f"Message received in flask: {message}")
        
        payload = {
                "message": message,
                "heating": heat,
                "temperature": setTEMPnum,
                "heater": heater
        }
        
        try:
            print(f"Sending to Bob Assistant: {payload}")
            json.dump(payload, process.stdin)  # Directly dump the JSON object
            process.stdin.write("\n")  # Add 
            process.stdin.flush()  # Ensure the message is sent
            print("Message sent to Bob Assistant!")
            return jsonify({"success": True, "response": "Message sent to assistant."})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": False, "error": "No message provided"}), 400


# Endpoint to get the latest shell output
@app.route('/get_shell_output', methods=['GET'])
def get_shell_output():
    return jsonify({"shell_output": shell_output})

threading.Thread(target=start_assistant, daemon=True).start()

# Run the entire system
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
    
