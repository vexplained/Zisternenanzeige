import threading
from webserver import app
from hw_bridge import ZisterneHW


def run_webserver(hw_bridge):
    app.config['HW_BRIDGE'] = hw_bridge


def main():
    hw_bridge = ZisterneHW()
    webserver_thread = threading.Thread(
        target=run_webserver, args=(hw_bridge,))
    webserver_thread.start()


if __name__ == "__main__":
    main()
