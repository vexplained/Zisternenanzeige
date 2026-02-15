"""Threadsafe recorder. "Inspired" by https://github.com/davewsmith/lapse/blob/main/control.py
"""

import threading
from datetime import datetime

# ! UNFINISHED, WITHOUT FUNCTIONALITY


class Recorder:
    def __init__(self, history_filename="history.csv") -> None:
        self.control_lock = threading.Lock()
        self.history_filename = history_filename
        self.last_stored_hist_entry = 0
        self.history = []

    def load_from_file(self):
        with open(self.history_filename, "rt+") as file:
            for line in file:
                (timestr, level) = line.split(',')
                self.history.append(
                    (datetime.strptime(timestr, "%Y-%m-%d (%H:%M:%S.%f)"), int(level)))
        self.last_stored_hist_entry = len(self.history) - 1

    def write_to_file(self, incremental=True):
        """Writes the history to file.

        Args:
            incremental (bool, optional): If true, only appends new history entries. Defaults to True.
        """

        with open(self.history_filename, "r+") as file:
            # check for empty newline at the end of file, compensate if necessary (see https://stackoverflow.com/a/11245718)
            file.seek(-2, 2)  # second to last character in file
            if file.read(2) == "\n\n":
                file.seek(-1, 1)  # go one character back

            array_string = ""
            begin_index = self.last_stored_hist_entry
            for i in range(begin_index, len(self.history)):
                (date, level) = self.history[i]
                f"{date.strftime("%Y-%m-%d (%H:%M:%S.%f)")},{level}"

        self.last_stored_hist_entry = len(self.history) - 1
