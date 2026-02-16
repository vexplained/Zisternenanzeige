from flask import Flask
from flask import render_template, request, jsonify

from hw_bridge import ZisterneHW

app = Flask(__name__)


@app.route("/", methods=["GET"])
def route_index():
    hw_bridge = app.config['HW_BRIDGE']
    if not isinstance(hw_bridge, ZisterneHW):
        # render dummy
        return render_template("error_hw.html")

    # if request.method == "POST":
    #     hw_bridge.read_sensors_and_cache()

    sensors = hw_bridge.get_readings()
    return render_template("ampel.html", title="Füllstand",
                           lamp5=sensors[3],
                           lamp4=sensors[2],
                           lamp3=sensors[1],
                           lamp2=sensors[0],
                           lamp1blinking=not any(sensors))


@app.route("/read", methods=["GET", "POST"])
def route_read():
    hw_bridge = app.config['HW_BRIDGE']
    if not isinstance(hw_bridge, ZisterneHW):
        # render dummy
        return render_template("error_hw.html")

    if request.method == "POST" and request.json.get("refreshReadings") == "true":
        hw_bridge.read_sensors_and_cache()

    return {
        "sensors": hw_bridge.get_readings_as_str(),
        "timeOfReading": hw_bridge.get_cache_time().strftime("%d.%m.%Y (%H:%M:%S)")
    }


@app.route("/history")
def route_history():
    return "WIP"


@app.route("/settings")
def route_settings():
    return "WIP"
