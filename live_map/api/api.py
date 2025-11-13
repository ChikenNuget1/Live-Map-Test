from flask import Blueprint, jsonify
import threading
import time
import serial

api_bp = Blueprint("api", __name__)

# Shared location state
latest_location = {
    "lat": None,
    "lon": None,
    "alt": None,
    "timestamp": None,
}


"""def serial_reader(port="COM5", baudrate=9600):
    # Background thread to read serial GPS from LoRa receiver.
    global latest_location

    while True:
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                print(f"[serial_reader] Listening on {port}")
                while True:
                    line = ser.readline().decode(errors="ignore").strip()
                    if not line:
                        continue

                    parts = line.split(",")
                    try:
                        lat = float(parts[0])
                        lon = float(parts[1])
                        alt = float(parts[2]) if len(parts) > 2 else None
                    except (ValueError, IndexError):
                        print(f"[serial_reader] Bad line: {line}")
                        continue

                    latest_location.update({
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "timestamp": time.time()
                    })

                    print(f"[serial_reader] Updated: {latest_location}")

        except serial.SerialException as e:
            print(f"[serial_reader] Serial error: {e}. Retrying in 5s...")
            time.sleep(5)"""

def serial_reader(port=None, baudrate=None):
    """Simulate reading from a serial file instead of hardware."""
    while True:
        with open("fake_serial.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 2:
                    continue

                lat = float(parts[0])
                lon = float(parts[1])
                alt = float(parts[2]) if len(parts) > 2 else None

                latest_location.update({
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "timestamp": time.time()
                })

                print("[file] Updated:", latest_location)
                time.sleep(2)


@api_bp.route("/location")
def api_location():
    """Return the latest known GPS location as JSON."""
    if latest_location["lat"] is None:
        return jsonify({"error": "No location data yet"}), 503

    return jsonify(lat=latest_location["lat"],
                   lon=latest_location["lon"],
                   alt=latest_location["alt"],
                   timestamp=latest_location["timestamp"])
