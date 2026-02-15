from flask import Flask
from flask import render_template, request

from hw_bridge import ZisterneHW

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def route_index():
    hw_bridge = app.config['HW_BRIDGE']

    print(hw_bridge)
    if not isinstance(hw_bridge, ZisterneHW):
        # render dummy
        return render_template("error_hw.html")

    if request.method == "POST":
        hw_bridge.read_sensors_and_cache()

    sensors = hw_bridge.get_readings()
    return render_template("ampel.html", title="Füllstand",
                           lamp5=sensors[3],
                           lamp4=sensors[2],
                           lamp3=sensors[1],
                           lamp2=sensors[0],
                           lamp1blinking=not any(sensors))


@app.route("/history")
def route_history():
    return "WIP"


@app.route("/settings")
def route_settings():
    return "WIP"
