from datetime import datetime, timedelta
import RPi.GPIO as GPIO
from typing import List


class ZisterneHW:
    def __init__(self, max_cache_age=3600) -> None:
        """Set up new hardware instance.

        Args:
            max_cache_age (int, optional): Max cache age, in seconds. Defaults to 3600.
        """
        # lowest (200L) to highest (5000L)
        self.SENSORS = [6, 13, 19, 26]
        self.cache = [False] * len(self.SENSORS)
        self.cached_time = datetime.now()
        self.max_cache_age = max_cache_age

    def __setup(self):
        GPIO.setmode(GPIO.BCM)
        for sensor in self.SENSORS:
            GPIO.setup(sensor, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __read_sensor_state(self) -> List[bool]:
        readings = [False] * len(self.SENSORS)
        for i in range(len(self.SENSORS)):
            readings[i] = GPIO.input(self.SENSORS[i])
        return readings

    def read_sensors_and_cache(self) -> List[bool]:
        """Reads out the sensors and refreshes the cache.

        Returns:
            List[bool]: List of sensor states
        """
        self.__setup()
        readings = self.__read_sensor_state()
        GPIO.cleanup()
        self.cache = readings
        self.cached_time = datetime.now()
        return readings

    def get_cache_age(self) -> timedelta:
        return datetime.now() - self.cached_time

    def get_readings(self) -> List[bool]:
        """Returns the cached sensor readings or, if the cache age is too high, the newly read values.

        Returns:
            List[bool]: List of sensor states
        """
        if self.get_cache_age().total_seconds() > self.max_cache_age:
            self.read_sensors_and_cache()
        return self.cache
