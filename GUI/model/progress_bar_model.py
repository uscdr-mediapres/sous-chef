import re
from PyQt5.QtCore import QObject, pyqtSignal


def read_new_content(file, file_position):
    """
    Reads new lines from the file since the last read position.

    :param file: The file object to read from.
    :param file_position: The position in the file to start reading from.
    :return: A tuple containing the new content and the updated file position.
    """
    if not file:
        return "", file_position

    file.seek(file_position)  # Start from the last position
    new_content = file.read()  # Read any new content
    file_position = file.tell()  # Update position for the next read
    return new_content, file_position


def split_message(message: str) -> dict:
    """
    Splits a log message into its components.

    :param message: The log message as a string.
    :return: A dictionary containing components of the log message.
    """
    pattern = (
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) "
        r"\[(?P<function>[^\]]+)\]:(?P<process_id>\d+) "
        r"(?P<level>\w+) - (?P<message>.*)"
    )
    match = re.match(pattern, message)
    result = {}
    if match:
        result = match.groupdict()
        components = {
            "INFO": "",
            "DEBUG": "",
            "ERROR": "",
            result["level"]: result["message"],
        }
        result["message"] = components

    return result


def search_analysis(message: str) -> (str, float):
    """
    Searches for analysis progress in a log message.

    :param message: The log message as a string.
    :return: A tuple with the description and progress percentage, or an empty tuple.
    """
    pattern = r"Analyzing files \((\d+(\.\d+)?)%\)"
    match = re.search(pattern, message)
    if match:
        number = match.group(1)
        return "Analyzing files", number
    return ()


def search_rawcooked(message: str) -> (str, float):
    """
    Searches for RAWCooked frame processing information.

    :param message: The log message as a string.
    :return: A tuple with the description and frame number, or an empty tuple.
    """
    pattern = r"frame=\s*(\d+).*bitrate=([\d.]+)kbits/s"
    match = re.search(pattern, message)
    if match:
        frame_number = match.group(1)
        return "Processing Frames", frame_number
    return ()


def search_reversibility(message: str) -> (str, float):
    """
    Searches for reversibility check progress in a log message.

    :param message: The log message as a string.
    :return: A tuple with the description and progress percentage, or an empty tuple.
    """
    pattern = r"\bTime=\d{2}:\d{2}:\d{2} \((\d+(\.\d+)?)%\)"
    match = re.search(pattern, message)
    if match:
        percentage = match.group(1)
        return "Checking Reversibility", percentage
    return ()


def get_sequence_length(message: str) -> (str, float):
    """
    Extracts the sequence length from a log message.

    :param message: The log message as a string.
    :return: A tuple with the description and sequence length, or an empty tuple.
    """
    match = re.search(r"sequence length:\s*(\d+)", message)
    if match:
        sequence_length = int(match.group(1))
        return "Sequence Length:", sequence_length
    return ()


class ProgressBarModel(QObject):
    """
    Manages the progress bar's state based on log file updates.

    """

    progress_error = pyqtSignal(str, int)
    """
    :signal progress_error: Emitted when an error occurs, with a message and code.
    
    """

    def __init__(self, filepath):
        """
        Initializes the ProgressBarModel.

        :param filepath: Path to the log file being monitored.
        """
        super().__init__()
        self.component = {}
        self.filepath = filepath
        self.progress_value = 0.0
        self.file = None
        self.file_position = 0
        self.total_frames = 0

        try:
            self.open_file()
        except FileNotFoundError:
            error_message = f"Error: File '{self.filepath}' not found."
            self.progress_error.emit(error_message, 100)
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            self.progress_error.emit(error_message, 100)

    def open_file(self, start_from_end=False):
        """
        Opens the log file for reading.

        :param start_from_end: Whether to start reading from the end of the file.
        """
        if self.filepath:
            self.file = open(self.filepath, "r")
            self.file_position = self.file.tell() if start_from_end else 0

    def read_new_content(self):
        """
        Reads new lines from the log file.

        :return: The new content read from the file.
        """
        if not self.file:
            self.progress_error.emit("Error: Debug Log File Not Found", 100)
            return ""

        return read_new_content(self.file, self.file_position)

    def close_file(self):
        """
        Closes the log file.
        """
        if self.file:
            self.file.close()
            self.file = None

    def get_report(self, component: dict, report: dict) -> dict:
        """
        Updates the progress report based on the parsed log component.

        :param component: The parsed log component.
        :param report: The current progress report.
        :return: The updated progress report.
        """
        try:
            section = component["message"]["INFO"]
            if "sequence length" in section:
                self.total_frames = int(re.search(r"sequence length:\s*(\d+)", section).group(1))
            report["section"] = section
        except Exception as e:
            raise RuntimeError from e
        return report

    def get_component(self, message: str, report: dict) -> (dict, dict):
        """
        Parses a log message and updates the progress report.

        :param message: The log message as a string.
        :param report: The current progress report as a dictionary.
        :return: A tuple containing the parsed log component and the updated report.
        """
        component = split_message(message + " ")  # Add space to account for empty logs
        if not component:
            print(f"Parse fail: {message}")
            return component, report

        try:
            if component != " ":
                report = self.get_report(component, report)
        except RuntimeError as e:
            print(f"Parse Fail due to RegEx mismatch: {e} component: ---{component}---")
        return component, report

    def read_component(self, line: str, report: dict = None) -> dict:
        """
        Processes a log line and updates the report.

        :param line: A line from the log file.
        :param report: The current progress report as a dictionary (optional).
        :return: An updated progress report or status dictionary.
        """
        report = (
            {"section": "", "progress": {"name": "", "value": 0}}
            if report is None
            else report
        )

        if not line.strip():  # No new content
            return {"level": "NO_UPDATE"}

        if "clean up complete" in line:
            return {"level": "FINISHED_PROCESSING"}

        # Parse the line
        component, report = self.get_component(line, report)
        component["report"] = report

        return component

    def fetch_data(self, line: str) -> dict:
        """
        Updates the model's state based on new log file data.

        :param line: A line from the log file.
        :return: A dictionary representing the progress and state of the process.
        """
        if not self.file:
            return {"section": "ERROR", "progress": {"name": "File Not Open", "value": 0}}

        # Process the log content and determine progress
        if not self.component:
            self.component = self.read_component(line)
        else:
            self.component = self.read_component(line, report=self.component["report"])
        if self.component["level"] == "ERROR":
            return {"section": "ERROR", "progress": {"name": "Failed", "value": 0}}
        elif self.component["level"] == "FINISHED_PROCESSING":
            return {"section": "COMPLETED", "progress": {"name": "Success", "value": 100}}
        return self.component.get("report", {})
