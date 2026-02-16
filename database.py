import yaml
import pickle
from collections import deque
from datetime import datetime
from pathlib import Path


class Config:
    """Config controller. Use inside with statements:
    >>> with Config(config_filepath) as config:
    >>>    ...
    This way, config updates are automatically written to disk upon releasing this object.
    """

    def __init__(self, config_filepath: str):
        self.config_filepath = config_filepath
        self.load_from_disk()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.write_to_disk()

    def load_from_disk(self):
        with open(self.config_filepath, "r") as file:
            self.config = yaml.safe_load(file)

    def write_to_disk(self):
        with open(self.config_filepath, "w", encoding="utf8") as file:
            yaml.dump(self.config, file, default_flow_style=False,
                      allow_unicode=True)


class AppStorage:
    """Internal app database controller. Use inside with statements:
    >>> with AppStorage(filepath) as storage:
    >>>    ...
    This way, updates are automatically written to disk upon releasing this object.
    """

    def __init__(self, filepath: str, config: Config):
        self.config = config
        self.filepath = filepath
        # youngest entry last; list of (level: int, timestamp: datetime)
        self.history = deque([(0, datetime.now())], maxlen=config.config.get(
            "history_length"))
        self.history.pop()  # remove only element; this element is only added for linting purposes
        self.storage = {
            # filllevel and timestamp of last mail sent
            "last_mail_level": 5,
            "last_mail_timestamp": datetime.now()
        }
        self.load_from_disk()

    def update_storage_params(self):
        """Updates parameters of storage objects such as the maximum history size.
        """
        if self.config.config.get("history_length") != self.history.maxlen:
            self.history = deque(
                self.history, maxlen=self.config.config.get("history_length"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.write_to_disk()

    def load_from_disk(self):
        if not Path(self.filepath).is_file():
            return
        with open(self.filepath, "rb") as file:
            (self.storage, self.history) = pickle.load(file)

    def write_to_disk(self):
        with open(self.filepath, "wb") as file:
            pickle.dump((self.storage, self.history), file)
