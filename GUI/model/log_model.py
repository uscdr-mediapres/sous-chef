import os
from PyQt5.QtCore import QObject, pyqtSignal


def tail_new_content(file, file_position):
    """Reads new lines from the file since the last read position."""
    if not file:
        return "", file_position

    file.seek(file_position)  # Start from the last position
    new_content = file.read()  # Read any new content
    file_position = file.tell()  # Update position for the next read
    return new_content, file_position


class LogModel(QObject):
    """
    A model for managing log files and reading new content dynamically.

    Attributes
    ----------
    filepath : str
        Path to the info log file.
    file : file object or None
        The open file object for the log file, or None if no file is open.
    file_position : int
        Tracks the position in the file for reading new content.

    Signals
    -------
    log_error(str)
        Emitted when an error occurs (e.g., file not found).
    """

    log_error = pyqtSignal(str)
    """
    :signal log_error: Emitted when an error occurs, with a message.
    """

    def __init__(self, filepath=None):
        """
        Initialize the LogModel instance.

        Parameters
        ----------
        filepath : str, optional
            Path to the log file. Defaults to None.
        """
        super().__init__()
        self.filepath = filepath
        self.file = None
        self.file_position = 0  # Keep track of where we are in the file
        try:
            self.set_filepath(self.filepath)
        except FileNotFoundError:
            error_message = f"Error: File '{self.filepath}' not found."
            self.log_error.emit(error_message)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            self.log_error.emit(error_message)

    def set_filepath(self, filepath, start_from_end=False):
        """
        Set the log file path and open it.

        Parameters
        ----------
        filepath : str
            The path to the log file.
        start_from_end : bool, optional
            If True, start reading from the end of the file. Defaults to False.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        self.filepath = filepath
        self.file_position = 0  # Reset position for the new file
        self.open_file(start_from_end)

    def open_file(self, start_from_end=False):
        """
        Opens the log file for reading.

        Parameters
        ----------
        start_from_end : bool, optional
            If True, position the file pointer at the end of the file.
            Defaults to False.

        Raises
        ------
        FileNotFoundError
            If the specified file does not exist.
        """
        if self.filepath:
            self.file = open(self.filepath, 'r')
            if start_from_end:
                self.file.seek(0, os.SEEK_END)  # Start reading from the end
                self.file_position = self.file.tell()
            else:
                self.file.seek(0)  # Start reading from the beginning
                self.file_position = 0

    def read_new_content(self):
        """
        Reads new lines from the log file since the last read.

        Returns
        -------
        str
            New content read from the log file.

        Emits
        -----
        log_error
            If the file is not found or an error occurs.
        """
        if not self.file:
            self.log_error.emit("Error: Info Log File Not Found\n")
            return ""

        new_content, self.file_position = tail_new_content(self.file, self.file_position)
        return new_content

    def close(self):
        """
        Closes the log file.

        This method ensures that the file object is closed properly and the
        associated resources are released.
        """
        if self.file:
            self.file.close()
            self.file = None
