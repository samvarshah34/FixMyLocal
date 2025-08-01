from flask import Flask, request, render_template, redirect, jsonify
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
DATA_FILE = "data.json"

otp_store = {}

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
        if report.get("lat") == lat and report.get("lng") == lng and report.get("timestamp") == timestamp:
            report["status"] = new_status
            updated = True
            break

    if not updated:
        return jsonify({"success": False, "error": "Report not found"})

    save_data(data)
    return jsonify({"success": True})

@app.route("/api/send_otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")
    if not email or "@" not in email:
        return jsonify(success=False, error="Invalid email"), 400

    otp = f"{random.randint(100000, 999999)}"
    otp_store[email] = otp

    print(f"[OTP] Sending OTP {otp} to email {email}")

    return jsonify(success=True)

@app.route("/api/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify(success=False, error="Missing email or OTP"), 400

    if otp_store.get(email) == otp:
        otp_store.pop(email)
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Invalid OTP"), 400

@app.route("/reports")
def reports():
    data = load_data()

    types = ["Food Assistance", "Medical Help", "Education Support", "Shelter or Clothing"]
    statuses = ["resolved", "unresolved"]

    by_type = {t: 0 for t in types}
    by_status = {s: 0 for s in statuses}
    time_series = {}
    heatmap_points = []

    for r in data:
        # Count by type and status
        if r["type"] in by_type:
            by_type[r["type"]] += 1
        if r["status"] in by_status:
            by_status[r["status"]] += 1

        # Time series
        day = r["timestamp"][:10]
        time_series[day] = time_series.get(day, 0) + 1

        # Heatmap
        try:
            heatmap_points.append([
                float(r["lat"]),
                float(r["lng"]),
                0.5  # weight
            ])
        except:
            continue

    sorted_dates = sorted(time_series.keys())
    time_counts = [time_series[d] for d in sorted_dates]

    return render_template("reports.html", stats={
        "by_type": by_type,
        "by_status": by_status,
        "dates": sorted_dates,
        "time_counts": time_counts,
        "heatmap_points": heatmap_points,
        "total": len(data)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=True)
