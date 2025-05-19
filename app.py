from flask import Flask, request, render_template, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    issue_type = request.form.get("type")
    description = request.form.get("desc")
    lat = request.form.get("lat")
    lng = request.form.get("lng")
    status = request.form.get("status", "unresolved")

    new_report = {
        "type": issue_type,
        "description": description,
        "lat": lat,
        "lng": lng,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    data = load_data()
    data.append(new_report)
    save_data(data)

    return redirect("/")

@app.route("/map")
def show_map():
    return render_template("map.html")

@app.route("/data")
def get_data():
    data = load_data()
    return jsonify(data)

@app.route("/api/update_status", methods=["POST"])
def update_status():
    req = request.get_json()
    lat = req.get("lat")
    lng = req.get("lng")
    timestamp = req.get("timestamp")
    new_status = req.get("status")

    if not lat or not lng or not timestamp or not new_status:
        return jsonify({"success": False, "error": "Missing lat, lng, timestamp or status"})

    data = load_data()
    updated = False
    for report in data:
        # Match report by lat, lng, and timestamp
        if report.get("lat") == lat and report.get("lng") == lng and report.get("timestamp") == timestamp:
            report["status"] = new_status
            updated = True
            break

    if not updated:
        return jsonify({"success": False, "error": "Report not found"})

    save_data(data)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
