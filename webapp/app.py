from flask import Flask, request, send_from_directory, jsonify
import json

app = Flask(__name__)
DATA_FILE = "data.json"

@app.route("/")
def serve_html():
    return send_from_directory(".", "index.html")

@app.route("/load")
def load():
    try:
        with open(DATA_FILE) as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"title": "Dashboard", "content": "Welcome!", "links": []})

@app.route("/save", methods=["POST"])
def save():
    with open(DATA_FILE, "w") as f:
        json.dump(request.json, f, indent=2)
    return "Saved", 200

if __name__ == "__main__":
    app.run(debug=True)
