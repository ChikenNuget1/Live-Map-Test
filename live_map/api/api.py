from flask import Blueprint, jsonify
import threading
import time
import serial

api_bp = Blueprint("api", __name__)

latest_location = {
    "lat": None,
    "lon": None,
    "alt": None,
    "timestamp": None,
}


def serial_reader(port="COM5", baudrate=9600):
    # Background thread to read serial GPS from LoRa receiver.
    global latest_location

    while True:
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                print(f"[serial_reader] Listening on {port}")
                while True:
                    # Decode line
                    line = ser.readline().decode(errors="ignore").strip()

                    # Print line for debugging
                    print(line)
                    if not line:
                        continue

                    # --- FIX START ---

                    # 1. Skip the log prefix "Received (XX bytes): "
                    # Find the position of the first ':', and slice everything after it.
                    if "Lat:" in line:
                        data_string = line.split(":", 1)[-1].strip()
                    else:
                        # Handle cases where the prefix might be missing (e.g., direct output)
                        data_string = line

                    # Expected format of data_string: "Lat: -36.853775, Lon: 174.769957, Sats: 5"

                    # 2. Split the string by comma and space, and extract values
                    # Example: ["Lat:", "-36.853775", "Lon:", "174.769957", "Sats:", "5"]

                    # Replace comma/colon separators with a single delimiter (e.g., '|') for easy splitting
                    normalized_string = data_string.replace(", Lon:", "|").replace(", Sats:", "|").replace("Lat:", "")

                    # Split into parts: [Lat_val, Lon_val, Sats_val]
                    value_parts = [p.strip() for p in normalized_string.split("|")]

                    # If expected string is less than expected, incomplete data
                    if len(value_parts) < 2:
                        print(f"[serial_reader] Incomplete GPS data: {data_string}")
                        continue

                    try:
                        # Extract latitude and longitude data
                        lat = float(value_parts[0])
                        lon = float(value_parts[1])
                        # Alt is not in the string, set to None unless your ESP32 code is updated
                        alt = None
                    except ValueError:
                        print(f"[serial_reader] Bad number format: {normalized_string}")
                        continue

                    # --- FIX END ---

                    # Store data in dictionary
                    latest_location.update({
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,  # Alt will be None for now
                        "timestamp": time.time()
                    })

                    # Print extracted data for debugging
                    print(f"[serial_reader] Updated: {latest_location}")

        # If no serial is detected, print error message, try again in 5s
        except serial.SerialException as e:
            print(f"[serial_reader] Serial error: {e}. Retrying in 5s...")
            time.sleep(5)

# Blueprint for the web-app
@api_bp.route("/location")
def api_location():
    """Return the latest known GPS location as JSON."""
    if latest_location["lat"] is None:
        return jsonify({"error": "No location data yet"}), 503

    # Returan data to html page
    return jsonify(lat=latest_location["lat"],
                   lon=latest_location["lon"],
                   alt=latest_location["alt"],
                   timestamp=latest_location["timestamp"])
