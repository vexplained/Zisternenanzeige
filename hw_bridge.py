from datetime import datetime, timedelta
import RPi.GPIO as GPIO
from typing import List
import logging


class ZisterneHW:
    def __init__(self, max_cache_age=3600) -> None:
        """Set up new hardware instance.

        Args:
            max_cache_age (int, optional): Max cache age, in seconds. Defaults to 3600.
        """
        # lowest (200L) to highest (5000L)
        self.SENSORS = [6, 13, 19, 26]
        self.cache = [0] * len(self.SENSORS)
        self.cached_time = datetime.fromtimestamp(0)
        self.max_cache_age = max_cache_age

    def __setup(self):
        GPIO.setmode(GPIO.BCM)
        for sensor in self.SENSORS:
            GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __read_sensor_state(self) -> List[int]:
        readings = [0] * len(self.SENSORS)  # 0 or 1
        for i in range(len(self.SENSORS)):
            readings[i] = int(GPIO.input(self.SENSORS[i]))
        return readings

    def read_sensors_and_cache(self) -> List[int]:
        """Reads out the sensors and refreshes the cache.

        Returns:
            List[int]: List of sensor states
        """
        logging.info("Reading new sensor values.")
        self.__setup()
        readings = self.__read_sensor_state()
        GPIO.cleanup()
        self.cache = readings
        self.cached_time = datetime.now()
        return readings

    def get_cache_time(self) -> datetime:
        return self.cached_time

    def get_cache_age(self) -> timedelta:
        return datetime.now() - self.cached_time

    def get_readings(self) -> List[int]:
        """Returns the cached sensor readings or, if the cache age is too high, the newly read values.

        Returns:
            List[int]: List of sensor states
        """
        logging.debug("Sensor readings requested. useCached={}, cacheAge={}s".format(
            self.get_cache_age().total_seconds() < self.max_cache_age, self.get_cache_age().total_seconds()))
        if self.get_cache_age().total_seconds() > self.max_cache_age:
            self.read_sensors_and_cache()
        logging.debug("Sensors: {}".format(self.cache))
        return self.cache
