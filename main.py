import os
import threading
from webserver import app
from hw_bridge import ZisterneHW
import logging
from database import Config, AppStorage
import mailcontroller
from datetime import datetime


class RepeatTimer(threading.Timer):
    """Repeating timer object. Usage:
    >>> timer = RepeatTimer(period_seconds: int, method)
    >>> timer.start()
    >>> ...
    >>> timer.cancel()
    Canceled timers cannot be started again.
    """

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

# Threaded approach inspired by https://github.com/davewsmith/lapse/blob/main/lapse.py


DATA_DIR = "data"
CONFIG_FILE = os.path.join(DATA_DIR, "config.yml")
YAML_SPEC_FILE = os.path.join(DATA_DIR, "openapi.yml")
DB_FILE = os.path.join(DATA_DIR, "database.pkl")


logger = logging.getLogger("main")


def run_webserver(hw_bridge, config, storage, yaml_spec_file):
    app.config['HW_BRIDGE'] = hw_bridge
    app.config['CONFIG'] = config
    app.config['APP_STORAGE'] = storage
    app.config['YAML_SPEC_FILE'] = yaml_spec_file
    # It isn't safe to use the reloader in a thread
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)


def update(hw_bridge: ZisterneHW, config: Config, storage: AppStorage):
    # reload config from disk
    # don't do that; config is reloaded upon saving config changes in the web interface
    # config.load_from_disk()

    old_vals = hw_bridge.cache
    if hw_bridge.get_cache_age().total_seconds() > config.config.get("max_cache_age", 3600):
        logger.info("Refreshing cache.")
        hw_bridge.read_sensors_and_cache()

    # invoke mail send routine (outside "if old_vals != hw_bridge.cache", because otherwise reminders mails would not be sent)
    mailcontroller.check_level_and_send(
        hw_bridge.get_filllevel(), config, storage)

    if old_vals != hw_bridge.cache:
        # sensor readings changed
        logger.info("Sensor readings changed.")
        storage.history.append((hw_bridge.get_filllevel(), datetime.now()))
        storage.write_to_disk()


def run_measure_daemon(hw_bridge: ZisterneHW, config: Config, storage: AppStorage):
    # read sensors to set hw_bridge cache (otherwise ::update adds history entry every time the app is started)
    hw_bridge.read_sensors_and_cache()
    # check every x seconds if max cache age is exceeded (in case a refresh was manually initiated)
    timer = RepeatTimer(config.config.get(
        "measure_daemon_interval"), update, args=(hw_bridge, config, storage))
    timer.start()


def main():
    logging.basicConfig(
        level=logging.DEBUG, style="{", datefmt="%H:%M:%S", format="{asctime}.{msecs:03.0f} [{levelname:^10}] [{threadName} | {name}] {message}")

    with Config(CONFIG_FILE) as config:
        with AppStorage(DB_FILE, config) as storage:
            hw_bridge = ZisterneHW(config.config.get("max_cache_age", 3600))

            run_measure_daemon(hw_bridge, config, storage)

            webserver_thread = threading.Thread(
                target=run_webserver, args=(hw_bridge, config, storage, YAML_SPEC_FILE))
            webserver_thread.start()


if __name__ == "__main__":
    main()
