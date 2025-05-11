from flask import Flask, request, render_template, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data.json"

# Ensure the data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    issue_type = request.form.get("type")
    description = request.form.get("desc")
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    status = request.form.get("status")  # 'resolved' or 'unresolved'

    new_report = {
        "type": issue_type,
        "description": description,
        "lat": lat,
        "lng": lng,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(DATA_FILE, "r+") as f:
        data = json.load(f)
        data.append(new_report)
        f.seek(0)
        json.dump(data, f, indent=2)

    return redirect("/")

@app.route("/map")
def show_map():
    return render_template("map.html")

@app.route("/data")
def get_data():
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=False)