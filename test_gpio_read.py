from hw_bridge import ZisterneHW
from time import sleep

def test():
    hw = ZisterneHW()
    hw.__setup__()
    for i in range(1000):
        r = hw.read_sensors_and_cache()
        # print(r)
        if r != [1, 1, 1, 1]: print("ERRRRRRRRRRRRRRRRRRRR")
        sleep(0.01)
    hw.__cleanup__()

if __name__ == "__main__":
    test()