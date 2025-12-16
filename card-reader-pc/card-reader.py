from flask import Flask, request, render_template_string, redirect, url_for
import requests
from py122u import nfc
import random
import time
import threading

app = Flask(__name__)

# Adress for Gateway receiver in GKC project
DEFAULT_POST_URL = "http://34.51.169.81/card-scan"

DOORS = [
    ("d-1.1", "Door 1 - Main"),
    ("d-1.2", "Door 2 - Side"),
    ("d-2.1", "Door 3 - Lab"),
    ("d-2.2", "Door 4 - Office"),
    ("d-4.0", "Door Secret - Basement"),
    ("d-3.55", "Zipline")
    ]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sender UI</title>
</head>
<body>
    <form method="POST" action="/send">
        <label>POST Address:</label><br>
        <input type="text" name="address" value="{{ default_url }}" style="width:400px;"><br><br>
        <label>Select Door:</label><br>
        <select name="door_id">
            {% for id, name in doors %}
                <option value="{{ id }}">{{ name }} ({{ id }})</option>
            {% endfor %}
        </select>
        <br><br>
        <button type="submit">Send UID</button>
    </form>
    <form method="POST" action="/stress-test">
        <button type="submit">Run Stress Test</button>
    </form>
</body>
</html>
"""

@app.route("/stress-test", methods=["POST"])
def stress_test():

    def worker(url=DEFAULT_POST_URL, num_requests=100):
        for i in range(num_requests):
            random_uid = "".join(f"{random.randint(0, 255):02X}" for _ in range(4))
            door = random.choice(DOORS)[0]
            payload = {"uid": random_uid, "door_id": door}
            try:
                response = requests.post(url, json=payload, timeout=5)
                print(f"Request {i+1}: UID={random_uid}, Door={door}, Status={response.status_code}, Access={response.text}")
            except requests.RequestException as e:
                print(f"Request {i+1} failed: {e}")
        print("Stress test finished.")

    post_url = request.form.get("address", DEFAULT_POST_URL)
    num_requests = 50  # Number of requests to send in the stress test

    for i in range(20):
        t = threading.Thread(target=worker, args=(post_url, num_requests), daemon=True)
        t.start()

    return f"Stress test started: sending {num_requests} requests to {post_url}."

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE, default_url=DEFAULT_POST_URL, doors=DOORS)

@app.route("/send", methods=["POST"])
def send():
    timeStart = time.time()
    post_url = request.form.get("address")
    door = request.form.get("door_id", DOORS[0][0])

    reader = nfc.Reader()
    reader.connect()
    reader.print_data(reader.get_uid())
    UID = reader.get_uid()
    # Hexadecimal representation of UID
    UIDhex = "".join(f"{b:02X}" for b in UID)

    payload = {"uid": UIDhex,"door_id": door}

    try:
        response = requests.post(post_url, json=payload, timeout=5)
        timeEnd = time.time()
        rtt= timeEnd - timeStart
        print(f"Request took {timeEnd - timeStart} seconds")
        if response.status_code == 200:
            try:
                resp_json = response.json()
                access = resp_json.get("access")
                if access == "granted" or access is True:
                    return f"Access Granted for UID {UIDhex} to Door {door}. Request took {rtt} seconds."
                else:
                    return f"Access Denied for UID {UIDhex} to Door {door}. Request took {rtt} seconds."
            except ValueError:
                return f"Error: Received non-JSON response from server."
        else:
            return f"Error: Received status code {response.test} from server."
    except requests.RequestException as e:
        return f"Error: Could not connect to server. Details: {e}"
    

if __name__ == "__main__":
    print("[SENDER] Running on http://localhost:5000/")
    app.run(host="0.0.0.0", port=5000)
