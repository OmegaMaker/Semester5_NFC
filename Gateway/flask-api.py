from flask import Flask, request

app = Flask(__name__)

@app.route("/receive_uid", methods=["POST"])
def receive_uid():
    data = request.get_json()
    uid = data.get("uid")
    print(f"[RECEIVER] UID received: {uid}")
    return {"status": "ok"}

@app.route("/")
def index():
    return "NFC UID Receiver is running. Cloud Build works!"


if __name__ == "__main__":
    print("[RECEIVER] Listening on http://localhost:8080/")
    app.run(host="0.0.0.0", port=8080)