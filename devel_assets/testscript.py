import RPi.GPIO as GPIO
from time import sleep
from typing import List

# VOLTAGE_SUPPLY = 20
SENSORS = [20, 21]


def setup():
    GPIO.setmode(GPIO.BCM)
    # GPIO.setup(VOLTAGE_SUPPLY, GPIO.OUT)
    # GPIO.output(VOLTAGE_SUPPLY, GPIO.LOW)
    for sensor in SENSORS:
        GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# def OLD_read_sensor_state() -> List[bool]:
#     # create supply voltage
#     GPIO.output(VOLTAGE_SUPPLY, GPIO.HIGH)
#     sleep(0.1)
#     # read sensor values
#     readings = [False] * len(SENSORS)
#     for i in range(len(SENSORS)):
#         readings[i] = GPIO.input(SENSORS[i])
#     # turn off voltage supply
#     GPIO.output(VOLTAGE_SUPPLY, GPIO.LOW)
#     return readings

def read_sensor_state() -> List[bool]:
    readings = [False] * len(SENSORS)
    for i in range(len(SENSORS)):
        readings[i] = GPIO.input(SENSORS[i])
    return readings


if __name__ == "__main__":
    setup()
    print(read_sensor_state())

    GPIO.cleanup()
