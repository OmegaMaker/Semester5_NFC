from flask import Flask, request, render_template_string, jsonify
import requests
import logging
import google.cloud.logging 
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging


app = Flask(__name__)

""" # Console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
setup_logging(logger)

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

@app.route("/", methods=["GET"])
def view():
    return render_template_string(HTML, data=last_received)

@app.route("/test", methods=["POST"])
def receive():
    global last_received
    last_received = request.get_data(as_text=True)

    ip = request.remote_addr
    logger.info(
        "POST /test request received",
        extra={
            "remote_ip": ip,
            "received_data": last_received,
            "endpoint": "/test"
        }
    )

    return "OK", 200

@app.route("/card-scan", methods=["POST"])
def cardScan():
    try:
        payload = request.get_json()
        uid = payload.get("uid")

        ip = request.remote_addr
        logger.info(
            "POST /card-scan request received",
            extra={
                "remote_ip": ip,
                "payload": payload,
                "endpoint": "/card-scan"
            }
        )

        if not payload or "uid" not in payload:
            logger.error(
                "Invalid JSON data for card scan",
                extra={
                    "remote_ip": ip,
                    "received_payload": payload,
                    "error_reason": "Missing UID or invalid payload"
                }
            )
            return jsonify({"error": "Invalid JSON payload"}), 400

        response = requests.post("http://receiver-service:8000/authorize", json=payload, timeout=2)
        data = response.json()

        logger.info(
            "POST /authorize request received",
            extra={
                "authorization_request_data": payload,
                "authorization_response": data,
                "target_service": "receiver-service",
                "endpoint": "/authorize"
            }
        )

        return jsonify({
            "access": data.get("access"),
            "uid": uid
        }), 200

    except Exception as e:
        logger.error(
            "Error during card scan process",
            extra={
                "error_message": str(e),
                "error_type": type(e).__name__,
                "remote_ip": request.remote_addr,
                "endpoint": "/card-scan"
            }
        )
        print("CARD SCAN ERROR:", repr(e))
        return jsonify({
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)