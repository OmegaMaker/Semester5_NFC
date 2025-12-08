from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/receive_uid", methods=["POST"])
def receive_uid():
    data = request.get_json()
    uid = data.get("uid")
    print(f"[RECEIVER] UID received: {uid}")
    return {"status": "ok"}

@app.route("/authorize", methods=["POST"])
def authorize():
    uid = request.get_json().get("uid")
    if uid == "E9F4687E":
        return jsonify({
            "access": True
        }), 200
    else:
        return jsonify({
            "access": False
        }), 200

@app.route("/")
def index():
    return "NFC UID Receiver is running. Cloud Build works!"


if __name__ == "__main__":
    print("[RECEIVER] Listening on http://localhost:8000/")
    app.run(host="0.0.0.0", port=8000)
