from flask import Flask, request, render_template_string

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)