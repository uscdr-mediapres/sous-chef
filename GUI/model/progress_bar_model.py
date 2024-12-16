import re
import os
from scripts.utils import read_new_content


def split_message(message: str) -> dict:
    """
    components in order: (timestamp, function, pid, level, message)
    :param message: str log message
    :return: tuple containing components of message
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
    pattern = r"Analyzing files \((\d+(\.\d+)?)%\)"
    match = re.search(pattern, message)

    if match:
        number = match.group(1)  # Extract the number from the capturing group
        return "Analyzing files", number
    else:
        return ()


def search_rawcooked(message: str) -> (str, float):
    pattern = r"frame=\s*(\d+).*bitrate=([\d.]+)kbits/s"
    match = re.search(pattern, message)

    if match:
        frame_number = match.group(1)  # Extract the frame number
        # bitrate = match.group(2)  # Extract the bitrate
        return "Processing Frames", frame_number
    else:
        return ()


def search_reversibility(message: str) -> (str, float):
    pattern = r"\bTime=\d{2}:\d{2}:\d{2} \((\d+(\.\d+)?)%\)"
    match = re.search(pattern, message)

    if match:
        percentage = match.group(1)  # Extract the percentage number
        return "Checking Reversibility", percentage
    else:
        return ()


def get_sequence_length(message: str) -> (str, float):
    match = re.search(r'sequence length:\s*(\d+)', message)
    if match:
        sequence_length = int(match.group(1))
        print("Sequence Length", sequence_length)
        return "Sequence Length:", sequence_length
    else:
        return ()


def parse_debug(message: str) -> (str, float):
    result = (
            search_analysis(message)
            or search_rawcooked(message)
            or search_reversibility(message)
    )
    if not result:
        return "-", 0.0
    return result


def get_section_status(section):
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


class ProgressBarModel:
    def __init__(self, filepath):
        self.component = {}
        self.filepath = filepath
        self.progress_value = 0.0  # Initialize dummy progress value at 0.0
        self.file = None
        self.file_position = 0  # Keep track of the current read position in the file
        self.open_file()
        self.total_frames = 0

    def open_file(self, start_from_end=False):
        if self.filepath:
            self.file = open(self.filepath, 'r')
            if start_from_end:
                self.file.seek(0, os.SEEK_END)  # Start reading from the end
                self.file_position = self.file.tell()
            else:
                self.file.seek(0)  # Start reading from the beginning
                self.file_position = 0

    def read_new_content(self):
        """Reads new lines from the log file using the utility function."""
        new_content, self.file_position = read_new_content(self.file, self.file_position)
        return new_content

    def close_file(self):
        """Closes the log file."""
        if self.file:
            self.file.close()
            self.file = None

    def get_report(self, component: dict, report: dict) -> dict:
        try:
            section: str = component["message"]["INFO"]
            if "sequence length" in section:
                self.total_frames = int(re.search(r'sequence length:\s*(\d+)', section).group(1))
            report["section"] = get_section_status(section) if section.startswith("---") else report["section"]
            if component["level"] == "DEBUG" and component["function"] in ("run_rawcooked", "check_v2"):
                name, value = parse_debug(component["message"]["DEBUG"])
                if name == "Processing Frames":
                    value = int(value)/self.total_frames * 100
                report["progress"]["name"] = name
                report["progress"]["value"] = value
        except Exception as e:
            raise RuntimeError from e
        return report

    def get_component(self, message: str, report: dict) -> (dict, dict):
        """
        component keys: (timestamp, function, pid, level, message)
        :param message: str log message
        :param report: running reports as a dictionary
        :return: components of message with parsed result
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
        """Processes new log content line by line and updates the report."""
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
        """Fetches component data and updates state based on the latest data."""
        if not self.file:
            return {"section": "ERROR", "progress": {"name": "File Not Open", "value": 0}}

        # Process the log content and determine progress
        if not self.component:
            self.component = self.read_component(line)
        else:
            self.component = self.read_component(line, report=self.component["report"])
        if self.component["level"] == "ERROR":
            print("here error")
            return {"section": "ERROR", "progress": {"name": "Failed", "value": 0}}
        elif self.component["level"] == "FINISHED_PROCESSING":
            return {"section": "COMPLETED", "progress": {"name": "Success", "value": 100}}
        return self.component.get("report", {})