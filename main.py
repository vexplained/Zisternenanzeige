import threading
from webserver import app
from hw_bridge import ZisterneHW
import logging

# Inspired by https://github.com/davewsmith/lapse/blob/main/lapse.py


def run_webserver(hw_bridge):
    app.config['HW_BRIDGE'] = hw_bridge
    # It isn't safe to use the reloader in a thread
    app.run(host="0.0.0.0", debug=True, use_reloader=False)


def main():
    logging.basicConfig(
        level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

    hw_bridge = ZisterneHW()
    webserver_thread = threading.Thread(
        target=run_webserver, args=(hw_bridge,))
    webserver_thread.start()


if __name__ == "__main__":
    main()
