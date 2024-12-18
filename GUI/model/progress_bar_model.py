import re
import os

from PyQt5.QtCore import QObject, pyqtSignal


def tail_new_content(file, file_position):
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
    pattern: str = (
        r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(?P<function>[^\]]+)\]:(?P<process_id>\d+) ("
        r"?P<level>\w+) - (?P<message>.*)"
    )
    match = re.match(pattern, message)
    result = {}
    if match:
        result = match.groupdict()
        components: dict = {
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
        number = match.group(1)  # Extract the number from the capturing group
        return "Analyzing files", number
    else:
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
        frame_number = match.group(1)  # Extract the frame number
        # bitrate = match.group(2)  # Extract the bitrate
        return "Processing Frames", frame_number
    else:
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
        percentage = match.group(1)  # Extract the percentage number
        return "Checking Reversibility", percentage
    else:
        return ()


def get_sequence_length(message: str) -> (str, float):
    """
    Extracts the sequence length from a log message.

    :param message: The log message as a string.
    :return: A tuple with the description and sequence length, or an empty tuple.
    """
    match = re.search(r'sequence length:\s*(\d+)', message)
    if match:
        sequence_length = int(match.group(1))
        print("Sequence Length", sequence_length)
        return "Sequence Length:", sequence_length
    else:
        return ()


def parse_debug(message: str) -> (str, float):
    """
    Parses the log message for specific debug information such as analysis percentage, frames processed, or reversibility checks.

    :param message: A log message string.
    :return: A tuple containing a label and a value (e.g., progress percentage or frame count),
             or a default tuple ("-", 0.0) if no patterns match.
    """
    result = (
            search_analysis(message)
            or search_rawcooked(message)
            or search_reversibility(message)
    )
    if not result:
        return "-", 0.0
    return result


def get_section_status(section):
    """
    Maps a section identifier to its corresponding status description.

    :param section: The section identifier as a string (e.g., "---starting setup---").
    :return: A human-readable status description corresponding to the section identifier.
            If the section is not recognized, the original section identifier is returned.
    """
    section = section.strip()
    status = {
        "---starting setup---": "Running Setup",
        "---setup complete---": "Completed Setup",
        "---starting dpx assessment---": "Assessing DPX Files",
        "---dpx assessment complete---": "Completed Assessment of DPX Files",
        "---starting dpx rawcook---": "Running RAWCooked",
        "---dpx rawcook complete---": "Finished Transcoding with RAWCooked",
        "---starting dpx post rawcook---": "Running Post Processing Checks",
        "---dpx post rawcook complete----": "Completed Post Processing Checks",
        "---starting clean up---": "Running Clean Up",
        "---clean up complete---": "Completed Clean Up",
        "---success---": "Successfully Completed",

    }

    return status.get(section, section)


class ProgressBarModel(QObject):
    """
    A model to update progress bar's state based on log file updates.

    Attributes
    ----------
    component: dict
        Tracks the current log components being read
    filepath: str
        Path to the debug log file
    progress_value: float
        Current progress value of the progress bar
    file: file object or None
        The open file object for the log file, or None if no file is open.
    file_position: int
        Tracks the position in the file for reading new content.
    total_frames:int
        Total number of frames being processed for this sequence

    Signals
    -------
    log_error(str)
        Emitted when an error occurs (e.g., file not found).
    """
    progress_error = pyqtSignal(str, int)
    """
    :signal progress_error: Emitted when an error occurs, with a message and value.
    """

    def __init__(self, filepath):
        """
        Initializes the ProgressBarModel.

        :param filepath: Path to the log file being monitored.
        """
        super().__init__()
        self.component = {}
        self.filepath = filepath
        self.progress_value = 0.0  # Initialize dummy progress value at 0.0
        self.file = None
        self.file_position = 0  # Keep track of the current read position in the file
        try:
            self.open_file()
        except FileNotFoundError:
            error_message = f"Error: File '{self.filepath}' not found."
            self.progress_error.emit(error_message, 100)  # Emit the error signal
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            self.progress_error.emit(error_message, 100)
        self.total_frames = 0

    def open_file(self, start_from_end=False):
        """
        Opens the log file for reading.

        :param start_from_end: Whether to start reading from the end of the file.
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
        Reads new lines from the log file.

        :return: The new content read from the file.
        """
        if not self.file:
            self.progress_error.emit("Error: Debug Log File Not Found", 100)
            return ""

        new_content, self.file_position = tail_new_content(self.file, self.file_position)
        return new_content

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
            section: str = component["message"]["INFO"]
            if "sequence length" in section:
                self.total_frames = int(re.search(r'sequence length:\s*(\d+)', section).group(1))
            report["section"] = get_section_status(section) if section.startswith("---") else report["section"]
            if component["level"] == "DEBUG" and component["function"] in ("run_rawcooked", "check_v2"):
                name, value = parse_debug(component["message"]["DEBUG"])
                if name == "Processing Frames":
                    value = int(value) / self.total_frames * 100
                report["progress"]["name"] = name
                report["progress"]["value"] = value
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
        component = split_message(message + " ")  # space to account for empty logs
        if not component:
            print(f"parse fail: {message}")
            return component

        try:
            if component != " ":
                report = self.get_report(component, report)
        except RuntimeError as e:
            print(f"Parse Fail due to RegEx mismatch: {e} component: ---{component}---")
        return component, report

    def read_component(self, line, report: dict = None) -> dict:
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

        # Parse each line
        component, report = self.get_component(line, report)
        component["report"] = report

        return component

    def fetch_data(self, line):
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