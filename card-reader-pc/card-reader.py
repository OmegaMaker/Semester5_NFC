from flask import Flask, request, render_template_string, redirect, url_for
import requests
from py122u import nfc

app = Flask(__name__)

# Adress for Gateway receiver in GKC project
DEFAULT_POST_URL = "http://34.51.247.142/card-scan"

DOORS = [
    ("d-1.1", "Door 1 - Main"),
    ("d-1.2", "Door 2 - Side"),
    ("d-2.1", "Door 3 - Lab"),
    ("d-2.2", "Door 4 - Office"),
    ("d-4.0", "Door Secret - Basement"),
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
        <select name="door">
            {% for id, name in doors %}
                <option value="{{ id }}">{{ name }} ({{ id }})</option>
            {% endfor %}
        </select>
        <br><br>
        <button type="submit">Send UID</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE, default_url=DEFAULT_POST_URL, doors=DOORS)

@app.route("/send", methods=["POST"])
def send():
    post_url = request.form.get("address")
    door = request.form.get("door", DOORS[0][0])

    reader = nfc.Reader()
    reader.connect()
    reader.print_data(reader.get_uid())
    UID = reader.get_uid()
    # Hexadecimal representation of UID
    UIDhex = "".join(f"{b:02X}" for b in UID)

    payload = {"uid": UIDhex,"door": door}

    try:
        response = requests.post(post_url, json=payload, timeout=5)
        if response.status_code == 200:
            try:
                resp_json = response.json()
                access = resp_json.get("access")
                if access == "granted" or access is True:
                    return f"Access Granted for UID {UIDhex} to Door {door}."
                else:
                    return f"Access Denied for UID {UIDhex} to Door {door}."
            except ValueError:
                return f"Error: Received non-JSON response from server."
        else:
            return f"Error: Received status code {response.test} from server."
    except requests.RequestException as e:
        return f"Error: Could not connect to server. Details: {e}"
    

if __name__ == "__main__":
    print("[SENDER] Running on http://localhost:5000/")
    app.run(host="0.0.0.0", port=5000)
