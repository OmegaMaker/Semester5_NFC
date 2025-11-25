from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# Default address (user can change this manually in the HTML form)
DEFAULT_POST_URL = "http://receiver-service/receive_uid"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sender UI</title>
</head>
<body>
    <h1>Send UID</h1>
    <form method="POST" action="/send">
        <label>POST Address:</label><br>
        <input type="text" name="address" value="{{ default_url }}" style="width:400px;"><br><br>
        <button type="submit">Send UID 12345</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_PAGE, default_url=DEFAULT_POST_URL)

@app.route("/send", methods=["POST"])
def send():
    post_url = request.form.get("address")

    payload = {"uid": "12345"}

    try:
        response = requests.post(post_url, json=payload, timeout=5)
        return f"Sent UID to {post_url}. Response status: {response.status_code}" 
    except Exception as e:
        return f"Error sending UID: {e}", 500

if __name__ == "__main__":
    print("[SENDER] Running on http://localhost:5000/")
    app.run(host="0.0.0.0", port=8000)
