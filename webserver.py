from flask import Flask
from flask import render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def route_index():
    if request.method == "POST":
        # TODO: Füllstand neu messen
        pass

    return render_template("ampel.html", title="Füllstand", lamp5=False, lamp4=True, lamp3=True, lamp2=True, lamp1blinking=False)


@app.route("/history")
def route_history():
    return "WIP"


@app.route("/settings")
def route_settings():
    return "WIP"
