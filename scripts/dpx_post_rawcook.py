import os
import utils
import logging.config
from logging import Logger
from pathlib import Path


def execute(params: dict) -> None:
    """
    Performs checks based on user preferences after the rawcook process.

    :param params: dictionary of params -> (mkv path, policy path, policy check flag)
    :type params: dict
    :raises RuntimeError: if there are any missing files, failed policy checks, or other unexpected errors
    :return: None
    """
    worker: Logger = logging.getLogger(f"worker_{os.getpid()}")
    worker.info("---starting dpx post rawcook---")
    worker.debug(f"{params = }")

    try:
        # unpack params
        mkv_path: Path = params["mkv_path"]
        policy_path: Path = params["policy_path"]
        policy_check: bool = params["policy_check"]
        mkv_txt_path: Path = mkv_path.with_suffix(mkv_path.suffix + ".txt")

        # check that mkv exists
        if not mkv_path.exists():
            raise FileNotFoundError(f"MKV file does not exist: {mkv_path=}")

        # check mkv policy
        if policy_check:
            result: bool = utils.check_mediaconch_policy(policy_path, mkv_path)
            if not result:
                raise RuntimeError(f"mkv policy check failed: {policy_path.name}")
            worker.info(f"verified {policy_path.name}")

        # check that mkv_txt exists
        if not mkv_txt_path.exists():
            raise FileNotFoundError(f"MKV txt file does not exist: {mkv_txt_path}")

        # check if error messages exist in mkv txt
        errors: str = utils.check_general_errors(mkv_txt_path)
        if errors:
            raise RuntimeError(f"errors found in mkv_txt: {errors}")

    except RuntimeError as e:
        raise RuntimeError(f"halting dpx_post_rawcook: {e}") from e
    except FileNotFoundError as e:
        raise RuntimeError(
            f"file missing: {e}, skipping checks, halting dpx_post_rawcook"
        ) from e
    except Exception as e:
        worker.error(f"unexpected error occurred: {e}")
        raise RuntimeError("halting dpx_post_rawcook") from e

    # closing logs
    worker.info("---dpx post rawcook complete---\n")


if __name__ == "__main__":
    print("dpx post rawcook")
