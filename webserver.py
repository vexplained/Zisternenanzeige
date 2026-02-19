from datetime import datetime
import os
import typing
from flask import Flask, url_for
from flask import render_template, request, jsonify, abort
from flask.json.provider import DefaultJSONProvider
import yaml
from openapi_spec_validator import validate_spec

from database import AppStorage, Config
from hw_bridge import ZisterneHW


# class CustomDateFmtJSONProvider(DefaultJSONProvider):
#     def dumps(self, obj: typing.Any, **kwargs: typing.Any) -> str:
#         kwargs.setdefault("default", self.default)
#         kwargs.setdefault("ensure_ascii", self.ensure_ascii)
#         kwargs.setdefault("sort_keys", self.sort_keys)
#         if isinstance(obj, datetime):
#             return obj.strftime(config_dateformat())
#         elif isinstance(obj, list):
#             # need to implement this as well
#             return ""
#         else:
#             return DefaultJSONProvider.dumps(self, obj, **kwargs)


app = Flask(__name__)
# app.json_provider_class = CustomDateFmtJSONProvider
# app.json = CustomDateFmtJSONProvider(app)


@app.route("/", methods=["GET"])
def route_index():
    hw_bridge = get_hw_bridge()
    if not isinstance(hw_bridge, ZisterneHW):
        # render dummy
        return render_template("error_hw.html")

    # if request.method == "POST":
    #     hw_bridge.read_sensors_and_cache()

    sensors = hw_bridge.get_readings()
    return render_template("ampel.html", title="Füllstand", navbar_filllevel_selected=True,
                           lamp5=sensors[3],
                           lamp4=sensors[2],
                           lamp3=sensors[1],
                           lamp2=sensors[0],
                           lamp1blinking=not any(sensors))


@app.route("/api/sensors", methods=["GET", "POST"])
def route_read():
    hw_bridge = get_hw_bridge()
    if not isinstance(hw_bridge, ZisterneHW):
        abort(500)

    if request.method == "POST" and request.json.get("refreshReadings") == "true":
        hw_bridge.read_sensors_and_cache()

    return {
        "filllevel": hw_bridge.get_filllevel(),
        "timeOfReading": hw_bridge.get_cache_time().strftime(config_dateformat())
    }


@app.route("/history")
def route_history():
    appstorage = get_appstorage()
    if not isinstance(appstorage, AppStorage):
        abort(500)  # Only required here to show 500 if something went fatally wrong

    return render_template("history.html", title="Historie", navbar_history_selected=True)


@app.route("/api/history")
def get_history():
    app_storage = get_appstorage()
    if not isinstance(app_storage, AppStorage):
        abort(500)

    out = [[level, date.strftime(config_dateformat())]
           for (level, date) in list(app_storage.history)]
    return out


@app.route("/settings")
def route_settings():
    return render_template("settings.html", title="Einstellungen", navbar_settings_selected=True)


@app.route('/api/config', methods=['GET'])
def get_yaml():

    with open(get_config().config_filepath, 'r') as file:
        yaml_content = file.read()
    return yaml_content


@app.route('/api/config', methods=['POST'])
def save_yaml():
    yaml_data = request.data.decode('utf-8')
    try:
        parsed_yaml = yaml.safe_load(yaml_data)

        with open(app.config['YAML_SPEC_FILE'], 'r') as file:
            openapi_yaml = yaml.safe_load(file)

        validate_spec(openapi_yaml)

        with open(get_config().config_filepath, 'w') as file:
            file.write(yaml_data)

        # reload config from file
        get_config().load_from_disk()
        get_appstorage().update_storage_params()

        return jsonify(status="success", message="Einstellungen erfolgreich gespeichert.")
    except Exception as e:
        return jsonify(status="error", message=f"Fehler: {str(e)}"), 400


def get_config() -> Config:
    config = app.config['CONFIG']
    if not isinstance(config, Config):
        raise RuntimeError("Webserver could not access config object.")
    return config


def get_hw_bridge() -> ZisterneHW:
    hw_bridge = app.config['HW_BRIDGE']
    if not isinstance(hw_bridge, ZisterneHW):
        raise RuntimeError(
            "Webserver could not access hardware bridge object.")
    return hw_bridge


def get_appstorage() -> AppStorage:
    appstorage = app.config['APP_STORAGE']
    if not isinstance(appstorage, AppStorage):
        raise RuntimeError(
            "Webserver could not access app storage object.")
    return appstorage


def config_dateformat() -> str:
    return get_config().config.get("date_format")
