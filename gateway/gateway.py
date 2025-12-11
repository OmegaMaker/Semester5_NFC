from flask import Flask, request, render_template_string, jsonify
import requests
import logging
import google.cloud.logging 
from google.cloud.logging.handlers import CloudLoggingHandler

app = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Google Cloud Logging
client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
logger.addHandler(handler)


last_received = "Nothing received yet."

HTML = """
<!doctype html>
<html>
<body>
<h2>POST Monitor</h2>

<p><b>Last received POST data:</b></p>
<pre>{{ data }}</pre>

</body>
</html>
"""

# Page for testing connection
@app.route("/", methods=["GET"])
def view():
    return render_template_string(HTML, data=last_received)

@app.route("/test", methods=["POST"])
def receive():
    global last_received
    last_received = request.get_data(as_text=True)

    ip = request.remote_addr
    logger.info("POST to /test from %s | Data: %s", ip, last_received)

    return "OK", 200

# Data received from card reader
# Returns access True/False
@app.route("/card-scan", methods=["POST"])
def cardScan():
    try:
        payload = request.get_json()
        uid = payload.get("uid")

        ip = request.remote_addr
        logger.info("POST to /card-scan from %s | Data: %s", ip, payload)

        if not payload or "uid" not in payload:
            logger.error("Invalid payload from %s | Data: %s", ip, payload)
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Send data to x for authorization logic
        response = requests.post("http://receiver-service:8000/authorize", json=payload, timeout=2)
        data = response.json()

        logger.info("POST to / from gateway | Data: %s", payload)
        logger.info("POST response from x | Data: %s", data)

        # Return response to card reader
        return jsonify({
            "access": data.get("access"),
            "uid": uid
        }), 200

    except Exception as e:
        logger.error("Error during scan: %s", str(e))
        print("CARD SCAN ERROR:", repr(e))
        return jsonify({
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)