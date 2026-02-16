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

# Inspired by https://github.com/davewsmith/lapse/blob/main/lapse.py


def run_webserver(hw_bridge, config):
    app.config['HW_BRIDGE'] = hw_bridge
    app.config['CONFIG'] = config
    # It isn't safe to use the reloader in a thread
    app.run(host="0.0.0.0", debug=True, use_reloader=False)


def update(hw_bridge: ZisterneHW, config: Config, storage: AppStorage):
    # reload config from disk
    config.load_from_disk()

    old_vals = hw_bridge.cache
    if hw_bridge.get_cache_age().total_seconds() > config.config.get("max_cache_age", 3600):
        logging.info("Refreshing cache.")
        hw_bridge.read_sensors_and_cache()

    # invoke mail send routine (outside "if old_vals != hw_bridge.cache", because otherwise reminders mails would not be sent)
    mailcontroller.check_level_and_send(
        hw_bridge.get_filllevel(), config, storage)

    if old_vals != hw_bridge.cache:
        # sensor readings changed
        logging.info("Sensor readings changed.")
        storage.history.append((hw_bridge.get_filllevel(), datetime.now()))
        storage.write_to_disk()


def run_measure_daemon(hw_bridge: ZisterneHW, config: Config, storage: AppStorage):
    # check every 10s if max cache age is exceeded (in case a refresh was manually initiated)
    timer = RepeatTimer(3, update, args=(hw_bridge, config, storage))
    timer.start()


def main():
    logging.basicConfig(
        level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    with Config("config.yml") as config:
        with AppStorage("database.pkl", config) as storage:
            hw_bridge = ZisterneHW(config.config.get("max_cache_age", 3600))

            run_measure_daemon(hw_bridge, config, storage)

            webserver_thread = threading.Thread(
                target=run_webserver, args=(hw_bridge, config))
            webserver_thread.start()


if __name__ == "__main__":
    main()
