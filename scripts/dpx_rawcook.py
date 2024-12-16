import os
import subprocess
import logging.config
from logging import FileHandler
from logging import Logger
from typing import List

import utils
from pathlib import Path


def grep_with_redirect(pattern: str, source: Path, destination: Path) -> None:
    """
    Redirects data from rawcook logs to a destination based on a grep search pattern.

    :param pattern: grep pattern to search
    :type pattern: str
    :param source: path to source file
    :type source: Path
    :param destination: path to destination file
    :type destination: Path
    :raises RuntimeError: if the subprocess call to grep fails for any reason
    :return: None
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info(f"redirecting rawcook log data to {destination.name}")
    worker.debug(f"{source=} {destination=}")
    try:
        command: str = f'grep "{pattern}" "{str(source)}" > "{str(destination)}"'

        result = subprocess.run(
            args=command,
            shell=True,
            text=True,
            check=True,
        )
        worker.debug(f"transfer complete {result=}")
    except (subprocess.CalledProcessError, Exception) as e:
        raise RuntimeError(f"error occurred during grep and redirect call: {e}") from e


def run_rawcooked(
    sequence_path: Path,
    output_path: Path,
    v2_flag: bool,
    frame_md5: bool,
    rc_license: str,
) -> Path:
    """
    Runs the rawcooked command for the sequence using the preferences specified by the user. After the rawcooked subprocess,
    the function also generates a .mkv.txt to assess for errors.

    :param sequence_path: path to dpx sequence
    :type sequence_path: Path
    :param output_path: path to output directory
    :type output_path: Path
    :param v2_flag: flag to indicate if the sequence requires rawcooked v2 or not
    :type v2_flag: bool
    :param frame_md5: flag to indicate if rawcooked generates a frame md5 file
    :type frame_md5: bool
    :param rc_license: license to run rawcooked command
    :type rc_license: str
    :raises RuntimeError: if the subprocess call to rawcooked fails for any reason
    :return: path to mkv file
    :rtype: Path
    """

    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.debug(f"initiating rawcook operation: {sequence_path.name}")
    mkv_path: Path = (output_path / sequence_path.name).with_suffix(".mkv")

    try:
        # generate run command
        string_command: str = (
            f"rawcooked --license {rc_license} "
            f"-y --all --no-accept-gaps {'--output-version 2' if v2_flag else ''} "
            f"-s 5281680 {'--framemd5' if frame_md5 else ''} "
            f"{sequence_path} -o {mkv_path}"
        )
        worker.debug(f"{mkv_path=}")
        # worker.debug(f"{string_command=}")

        command: List[str] = [c for c in string_command.split(" ") if len(c) > 0]
        # worker.debug(f"{command=}")

        # call subprocess using run command
        worker.info("calling rawcook subprocess")

        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as p:
            for line in p.stderr:
                worker.debug(line)
            for line in p.stdout:
                worker.debug(line)

        # check for success
        if p.returncode != 0:
            worker.error("failure during rawcook subprocess")
            raise RuntimeError(
                f"rawcooked command failed with error code: {p.returncode}"
            )
        worker.info("rawcook subprocess completed successfully")

        # grep run_rawcooked to mkv_txt file
        worker.info("generating mkv_txt")
        try:
            mkv_txt_path: Path = (output_path / sequence_path.stem).with_suffix(
                ".mkv.txt"
            )
            debug_file = ""
            for handler in worker.parent.handlers:
                if isinstance(handler, FileHandler) and handler.name == "debug_file":
                    debug_file: str = handler.baseFilename
            grep_with_redirect("run_rawcooked", Path(debug_file), mkv_txt_path)
        except Exception as e:
            raise RuntimeError(f"mkv_txt generation failed: {e}") from e
        worker.info(f"mkv_txt generated: {mkv_txt_path.name=}")
        worker.info(f"mkv_path generated: {mkv_path.name=}")

    except Exception as e:
        raise RuntimeError(
            f"dpx rawcook execution failure during subprocess call: {e}"
        ) from e

    return mkv_path


def execute(params: dict) -> Path:
    """
    Parses user preferences and executes the rawcooked command for a dpx sequence.

    :param params: dictionary of parameters -> (sequence path, output path, rawcooked license, v2 flag, frame md5 flag)
    :type params: dict
    :raises RuntimeError: if the subprocess call to rawcooked fails for any reason
    :return: path to mkv file
    :rtype: Path
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("---starting dpx rawcook---")
    worker.debug(f"{params = }")

    try:
        # unpack params
        parent_path: Path = params["sequence_path"]
        output_path: Path = params["output_path"]
        rc_license: str = params["license"]
        v2_flag: bool = params["v2_flag"]
        frame_md5: bool = params["frame_md5"]
        sequence_path: Path = utils.find_sequence_path(parent_path)

        # check if sequence exists
        n: int = utils.sequence_count(sequence_path)
        if n == 0:
            raise RuntimeError(f"sequence folder is empty: {sequence_path}")
        else:
            worker.info(f"sequence length: {n}")

        try:
            mkv_path = run_rawcooked(
                parent_path, output_path, v2_flag, frame_md5, rc_license
            )
        except Exception as e:
            raise RuntimeError(f"run rawcooked failed: {e}") from e

    except Exception as e:
        worker.error(f"error occurred during dpx_rawcook: {e}")
        raise RuntimeError(f"halting dpx_rawcook: {e}") from e

    # closing logs
    worker.info("---dpx rawcook complete---\n")
    return mkv_path


if __name__ == "__main__":
    print("dpx rawcook")
