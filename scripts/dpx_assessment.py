import os
import subprocess
from typing import List

import utils
import logging.config
from logging import Logger
from pathlib import Path
import re


def check_v2(sequence_path: Path, rc_license: str) -> bool:
    """
    Checks if the reversibility file for a dpx sequence is too big, indicating that version 2 of rawcooked is required.

    :param sequence_path: path to the dpx sequence
    :type sequence_path: Path
    :param rc_license: license to run rawcooked
    :type rc_license: str
    :raises RuntimeError: if the rawcooked command fails to run
    :return: True if version 2 of rawcooked is required, False otherwise
    :rtype: bool
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("checking version")

    try:
        # rawcooked parameters
        command: List[str] = [
            "rawcooked",
            "--license",
            rc_license,
            "--check",
            "--no-encode",
            str(sequence_path),
        ]
        worker.debug(f"running subprocess {command=}")
        fail: bool = False
        error_message: str = "Error: the reversibility file is becoming big"

        #  subprocess call
        with subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ) as p:
            for line in p.stderr:
                worker.debug(line)
                if error_message in line:
                    fail = True
            for line in p.stdout:
                worker.debug(line)
                if error_message in line:
                    fail = True

        # checks for sequences with large reversibility file
        if fail:
            worker.warning("reversibility file is too big, using version 2")
            return True

    except (subprocess.CalledProcessError, Exception) as e:
        raise RuntimeError(f"error during version check: {e}") from e
    return False


def check_gap(sequence_path: Path) -> bool:
    """
    Checks for gaps and missing frames in a dpx sequence.

    :param sequence_path: sequence path
    :type sequence_path: Path
    :raises RuntimeError: if the check fails for any reason
    :return: True if the sequence has no gaps, False otherwise
    :rtype: bool
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("checking if gaps are present in sequence")

    # extract frame number from dpx file name
    search_pattern: str = r"\d+\.(?:dpx|DPX)$"
    regex: re.Pattern = re.compile(search_pattern)

    try:
        sequence: List[str] = os.listdir(sequence_path)
        numbers: List[int] = [
            int(regex.search(x).group().split(".")[0]) for x in sequence
        ]
        n: int = min(numbers)
        m: int = max(numbers)

        min_sum: int = (n * (n + 1)) // 2
        max_sum: int = (m * (m + 1)) // 2
        expected_sum: int = max_sum - min_sum + n
        total_sum: int = sum(numbers)

        if total_sum != expected_sum:
            worker.warning(f"there are gaps in the sequence")
            worker.debug(f"total: {total_sum} expected: {expected_sum} ")
        else:
            worker.debug(f"no gaps in sequence, total: {total_sum}")
            return True
    except Exception as e:
        raise RuntimeError(f"error while checking for gaps: {e}") from e

    return False


def execute(params: dict) -> bool:
    """
    Performs all assessment functions on a dpx sequence based on preferences specified by the user.
    They are listed here in order: check if sequence exists, check for gaps in the sequence, check if v2 flag is required, check dpx policy

    :param params: a dictionary of parameters -> (sequence_path, policy path, rawcooked license, gap check flag, policy check flag)
    :type params: dict
    :returns: True if v2 required, False otherwise
    :rtype: bool
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("---starting dpx assessment---")
    worker.debug(f"{params = }")
    try:
        # unpack params
        parent_path: Path = params[
            "sequence_path"
        ]  # parent path: execute/wd/seq/parent.name
        policy_path: Path = params["policy_path"]
        rc_license: str = params["license"]
        gap_check: bool = params["gap_check"]
        policy_check: bool = params["policy_check"]
        sequence_path: Path = utils.find_sequence_path(parent_path)

        # check if sequence exists
        n: int = utils.sequence_count(sequence_path)
        if n == 0:
            raise RuntimeError(f"sequence folder is empty: {sequence_path}")
        else:
            worker.info(f"sequence length: {n}")

        # check for gaps in the sequence if gap check is true
        if gap_check:
            result = check_gap(sequence_path)
            if not result:
                raise RuntimeError(
                    f"sequence has gaps, verify logs for {sequence_path=}"
                )
            worker.info("no gaps in sequence")

        # check for large reversibility and assign v2_flag
        try:
            v2_flag = check_v2(parent_path, rc_license)
            worker.info(f"version check: {'v2' if v2_flag else 'v1'}")
            worker.debug(f"{v2_flag=}")
        except RuntimeError as e:
            raise RuntimeError(f"version check failure, ending execution: {e}")

        # check dpx policy
        if policy_check and not v2_flag:
            dpx_path: Path = next(sequence_path.iterdir())
            result: bool = utils.check_mediaconch_policy(policy_path, dpx_path)
            if not result:
                raise RuntimeError(f"dpx policy check failed: {policy_path.name}")
            worker.info(f"verified {policy_path.name}")

    except Exception as e:
        worker.error(f"error occurred during dpx assessment: {e}")
        raise RuntimeError("halting dpx_assessment") from e

    # closing logs
    worker.info("---dpx assessment complete---\n")
    return v2_flag


if __name__ == "__main__":
    print("dpx assessment")
