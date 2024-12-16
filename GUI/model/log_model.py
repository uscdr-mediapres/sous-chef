import os
from scripts.utils import read_new_content


class LogModel:
    def __init__(self, filepath=None):
        self.filepath = filepath
        self.file = None
        self.file_position = 0  # Keep track of where we are in the file
        self.set_filepath(self.filepath)

    def set_filepath(self, filepath, start_from_end=False):
        """Set the log file path and open it."""
        self.filepath = filepath
        self.file_position = 0  # Reset position for the new file
        self.open_file(start_from_end)

    def open_file(self, start_from_end=False):
        """Opens the log file for reading."""
        if self.filepath:
            self.file = open(self.filepath, 'r')
            if start_from_end:
                self.file.seek(0, os.SEEK_END)  # Start reading from the end
                self.file_position = self.file.tell()
            else:
                self.file.seek(0)  # Start reading from the beginning
                self.file_position = 0

    def read_new_content(self):
        """Reads new lines from the log file since the last read."""
        if not self.file:
            return ""

        new_content, self.file_position = read_new_content(self.file, self.file_position)
        return new_content

    def close(self):
        """Closes the log file."""
        if self.file:
            self.file.close()
            self.file = None
