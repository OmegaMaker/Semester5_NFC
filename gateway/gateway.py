from flask import Flask, request, render_template_string, jsonify
import requests
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

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
    logger.info("POST /test from %s | Data: %s", ip, last_received)

    return "OK", 200

@app.route("/card-scan", methods=["POST"])
def cardScan():
    try:
        payload = request.get_json()
        uid = payload.get("uid")

        ip = request.remote_addr
        logger.info("POST /card-scan from %s | Data: %s", ip, payload)

        if not payload or "uid" not in payload:
            logger.info("Invalid JSON data")
            return jsonify({"error": "Invalid JSON payload"}), 400

        response = requests.post("http://receiver-service:8000/authorize", json=payload, timeout=2)
        data = response.json()

        logger.info("POST /authorize to http://receiver-service:8000 | Data: %s | Response: %s", payload, data)

        return jsonify({
            "access": data.get("access"),
            "uid": uid
        }), 200

    except Exception as e:
        logger.info("Error with card scan")
        print("CARD SCAN ERROR:", repr(e))
        return jsonify({
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)