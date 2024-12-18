import subprocess
import os
import datetime
import json
from logging import Logger
from shutil import copy as shutil_copy
import logging.config
from pathlib import Path
from typing import List


def create_execution_dir(output_dir: Path) -> Path:
    """
    Creates an execution directory that acts as a buffer during processing to store the results of each run. The output directory within is
    created with the format (execution_year_month_day_hour_second) along with a working directory that is deleted post execution.

    :param output_dir: output directory path specified by user, where the execution directory will be created
    :type output_dir: Path
    :raise RuntimeError: if execution directory already exists, or unexpected errors
    :returns: path to the output directory within the execution directory
    :rtype: Path
    """

    setup: Logger = logging.getLogger("setup")
    setup.info("creating execution directory")
    now: datetime.datetime = datetime.datetime.now()
    now_format: str = f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.second}"

    working_directory: Path = output_dir / "working_directory"
    outputs: Path = output_dir / f"execution_{now_format}"
    logs: Path = outputs / "logs"
    setup.debug(f"{output_dir=} {working_directory=} {outputs=} {logs=}")
    try:
        if not output_dir.exists() or not output_dir.is_dir():
            setup.error(
                f"filepath {output_dir} does not exist or is not a valid directory"
            )
            raise RuntimeError(
                f"verify that {output_dir} exists and is a valid directory"
            )

        working_directory.mkdir(exist_ok=False)
        outputs.mkdir(exist_ok=True)
        logs.mkdir(exist_ok=True)
    except FileExistsError as e:
        setup.error(
            "working directory already exists at this location, verify that a process is not running already"
        )
        raise RuntimeError(e)
    except Exception as e:
        setup.error(f"unexpected exception occurred while creating execution directory")
        raise RuntimeError(e)
    return outputs


def create_working_dir(execution_dir: Path) -> Path:
    """
    Creates the working directory structure in the specified execution directory.
    The working directory contains subdirectories for policies, logs and the dpx sequence.

    :param execution_dir: execution directory path specified by user, where the working directory will be created
    :type execution_dir: Path
    :raise RuntimeError: if execution fails for any reason
    :returns: path to the dpx sequence directory within the execution directory
    :rtype: Path
    """

    current_process: int = os.getpid()
    working_directory: Path = execution_dir / f"wd_{current_process}"
    policies: Path = working_directory / "policies"
    sequence: Path = working_directory / "sequence"
    logs: Path = working_directory / "logs"

    try:
        if not execution_dir.exists() or not execution_dir.is_dir():
            raise RuntimeError(f"verify that {execution_dir} exists and is a folder")
        working_directory.mkdir(exist_ok=False)
        policies.mkdir(exist_ok=True)
        logs.mkdir(exist_ok=True)
        sequence.mkdir(exist_ok=True)
    except FileExistsError as e:
        raise RuntimeError(
            f"could not create working directory due to existing structure: {e}"
        )
    except Exception as e:
        raise RuntimeError(f"unexpected error during working directory creation: {e}")
    return sequence


def get_log_config(log_directory: Path) -> dict:
    """
    Generates a logging configuration file based on the specified log directory. The console handler is turned off by default.

    :param log_directory: logging directory path specified by user, where the logs will be created
    :type log_directory: Path
    :returns: dictionary containing the logging configuration
    :rtype: dict
    """

    log_directory.mkdir(parents=True, exist_ok=True)

    debug_file: Path = log_directory / "debug.log"
    error_file: Path = log_directory / "error.log"
    info_file: Path = log_directory / f"info.log"

    log_config: dict = {
        "version": 1,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s [%(funcName)s]:%(process)d %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "[%(asctime)s] %(funcName)s.%(levelname)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "short": {
                "format": "%(funcName)s | %(levelname)s: %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": logging.INFO,
                "formatter": "short",
            },
            "debug_file": {
                "class": "logging.FileHandler",
                "level": logging.DEBUG,
                "filename": str(debug_file),
                "mode": "w",
                "formatter": "detailed",
            },
            "error_file": {
                "class": "logging.FileHandler",
                "level": logging.WARNING,
                "filename": str(error_file),
                "mode": "w",
                "formatter": "detailed",
            },
            "info_file": {
                "class": "logging.FileHandler",
                "level": logging.INFO,
                "filename": str(info_file),
                "mode": "w",
                "formatter": "simple",
            },
        },
        "loggers": {
            "": {
                "handlers": ["debug_file", "info_file", "error_file"],
                "level": "DEBUG",
            },
        },
    }
    return log_config


def move_logs(wd: Path, output_path: Path, sequence_destination: Path) -> None:
    """
    Aggregates logs generated during an execution to the specified output directory and sequence.

    :param wd: working directory path containing data from every worker
    :type wd: Path
    :param output_path: output directory path where results are stored
    :type output_path: Path
    :param sequence_destination: the sequence for which the logs will be moved
    :type sequence_destination: Path
    :raises: None
    :returns: None
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("aggregating logs to output folder")
    log_names: List[str] = ["debug", "error", "info"]
    log_source: List[Path] = [wd / "logs" / f"{name}.log" for name in log_names]
    log_destination: List[Path] = [
        output_path / "logs" / sequence_destination.stem / f"{name}.log"
        for name in log_names
    ]

    worker.debug(f"{log_source=}")
    worker.debug(f"{log_destination=}")

    try:
        # move info logs
        worker.info("moving info logs")
        move(log_source[2], log_destination[2])

        # # move debug and error if error is non-zero
        # if log_source[1].stat().st_size:
        worker.info("moving error and debug logs")
        move(log_source[0], log_destination[0])
        move(log_source[1], log_destination[1])
    except RuntimeError as e:
        worker.error(f"failure during move operation: {e}")
    except Exception as e:
        worker.error(f"unexpected error occurred while moving logs: {e}")


def write_log_config(
        write_path: Path,
        driver_path: Path,
        final_path: Path,
        count: int,
        sequence_paths: List[Path],
) -> None:
    """
    Creates a JSON file containing log paths to be read by the GUI.

    :param write_path: path where this config will be written to
    :type write_path: Path
    :param driver_path: location of driver logs
    :type driver_path: Path
    :param final_path: location where logs need to be moved
    :type final_path: Path
    :param count: number of sequences processed
    :type count: int
    :param sequence_paths: list of sequence paths containing worker logs
    :type sequence_paths: List[Path]
    :raises: None
    :returns: None
    """
    log_config: dict = {
        "sequences": {"count": count},
        "driver": {
            "debug": str(driver_path / "debug.log"),
            "error": str(driver_path / "error.log"),
            "info": str(driver_path / "info.log"),
        },
        "workers": {
            f"{i}": {
                "debug": str(sequence_paths[i] / "debug.log"),
                "error": str(sequence_paths[i] / "error.log"),
                "info": str(sequence_paths[i] / "info.log"),
            }
            for i in range(count)
        },
        "output": {
            "driver": {
                "debug": str(final_path / "debug.log"),
                "error": str(final_path / "error.log"),
                "info": str(final_path / "info.log"),
            },
            "workers": str(final_path / "logs"),
        },
    }
    with open(write_path, "w") as f:
        json.dump(log_config, f, indent=4)


def find_sequence_path(parent_path: Path) -> Path:
    """
    Finds the dpx sequence directory within the parent directory

    :param parent_path: parent directory path
    :type parent_path: Path
    :raises RuntimeError: if no sequence folder is found
    :returns: path to sequence folder
    :rtype: Path
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.debug(f"finding sequence folder for: {parent_path}")
    result: Path = Path()

    for root, directory, file in os.walk(parent_path):
        if len(file) > 0 and len(directory) == 0:
            dpx_check: bool = file[0].endswith(".dpx") or file[0].endswith(".DPX")
            if not dpx_check:
                worker.warning(f"{root} contains files that are not .dpx")
            else:
                result = Path(root)
                worker.debug(f"found sequence folder: {result}")
                break

    if result == Path():
        worker.error(f"could not locate sequence within parent: {parent_path}")
        raise RuntimeError(f"error while finding sequence within parent")

    return result


def check_mediaconch_policy(policy_path: Path, filename: Path) -> bool:
    """
    Verifies a policy for a sequence by validating a single frame of the sequence against the policy via
    the mediaconch command

    :param policy_path: path to policy file
    :type policy_path: Path
    :param filename: path to a dpx frame
    :type filename: Path
    :raises RuntimeError: if policy check cannot be performed for any reason
    :returns: True if frame is verified, False otherwise
    :rtype: bool
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.debug(f"verifying {policy_path=} against {filename=}")
    try:
        command: List[str] = [
            "mediaconch",
            "--force",
            "-p",
            str(policy_path),
            str(filename),
        ]
        worker.debug(f"{command=}")
        check: subprocess.CompletedProcess = subprocess.run(
            command, capture_output=True
        )
        check_str: str = check.stdout.decode()
        worker.debug(f"{check_str=}")
        if check_str.startswith("pass!"):
            return True
    except Exception as e:
        worker.error(f"failed to verify {policy_path=} against {filename}")
        raise RuntimeError(f"failure during policy check: {e}")
    return False


def check_general_errors(mkv_txt_path: Path) -> str:
    """
    Checks for error messages in the .mkv.txt file and returns them if they exist

    :param mkv_txt_path: path to .mkv.txt file
    :type mkv_txt_path: Path
    :raises RuntimeError: if an error occurs for any reason
    :returns: error message if it exists, an empty string otherwise
    :rtype: str
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.debug(f"checking {mkv_txt_path.name} for errors")
    result: str = ""
    error_messages: List[str] = [
        "Reversibility was checked, issues detected, see below.",
        "Error:",
        "Conversion failed!",
        "Please contact info@mediaarea.net if you want support of such content.",
    ]

    for error in error_messages:
        try:
            match = subprocess.run(
                ["grep", error, str(mkv_txt_path)],
                stdout=subprocess.PIPE,
                text=True,
                check=False,
            )
            if match.stdout:
                worker.debug(f"found error: {match.stdout}")
                result = match.stdout
        except Exception as e:
            raise RuntimeError(f"an error occurred during general error grep") from e

    return result


def move(source_path: Path, destination_path: Path) -> None:
    """
    Moves a file/directory from source_path to destination_path

    :param source_path: file/directory source path
    :type source_path: Path
    :param destination_path: file/directory destination path
    :type destination_path: Path
    :raises RuntimeError: if source is not found or if it already exists at the destination
    :returns: None
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    try:
        if source_path.resolve() == destination_path.resolve():
            worker.debug(f"working in place: {source_path.resolve()}")
            return
        if destination_path.exists():
            (
                destination_path.rmdir()
                if destination_path.is_dir()
                else destination_path.unlink()
            )

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(destination_path)
        worker.debug(f"moved: {source_path} to {destination_path}")
    except FileNotFoundError as e:
        raise RuntimeError(f"failed during move, could not locate file: {e}") from e
    except FileExistsError as e:
        raise RuntimeError(f"failed during move, file already exists: {e}") from e
    except Exception as e:
        raise RuntimeError(f"unexpected failure during move: {e}") from e


def copy(source_path: Path, destination_path: Path) -> None:
    """
    Copies a file/directory from source_path to destination_path

    :param source_path: file/directory source path
    :type source_path: Path
    :param destination_path: file/directory destination path
    :type destination_path: Path
    :raises RuntimeError: if source is not found or if it already exists at the destination
    :returns: None
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    try:
        if destination_path.exists():
            (
                destination_path.rmdir()
                if destination_path.is_dir()
                else destination_path.unlink()
            )

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil_copy(source_path, destination_path)
        worker.debug(f"copied: {source_path} to {destination_path}")
    except FileNotFoundError as e:
        raise RuntimeError(f"failed during copy, could not locate file: {e}") from e
    except FileExistsError as e:
        raise RuntimeError(f"failed during copy, file already exists: {e}") from e
    except Exception as e:
        raise RuntimeError(f"unexpected failure during copy: {e}") from e


def sequence_count(sequence_path: Path) -> int:
    """
    Counts the number of dpx frames in a sequence.

    :param sequence_path: path to sequence
    :type sequence_path: Path
    :returns: number of frames in sequence
    :rtype: int
    """
    n: int = len(
        [
            x
            for x in os.listdir(sequence_path)
            if (x.endswith(".dpx") or x.endswith(".DPX"))
        ]
    )
    return n


if __name__ == "__main__":
    log_location = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    print(log_location)
