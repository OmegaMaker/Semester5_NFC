from flask import Flask, request, render_template_string, jsonify
import requests

app = Flask(__name__)

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
    return "OK", 200

@app.route("/card-scan", methods=["POST"])
def cardScan():
    try:
        payload = request.get_json()
        uid = payload.get("uid")

        response = requests.post("http://receiver-service/authorize", json=payload, timeout=2)
        data = response.json()

        access = data.get("access")

        return jsonify({
            "access": "granted" if access else "denied",
            "uid": uid
        }), 200

    except Exception as e:
        print("CARD SCAN ERROR:", repr(e))
        return jsonify({
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)