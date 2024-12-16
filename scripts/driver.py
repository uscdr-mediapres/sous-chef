import os
import argparse
import json
import logging.config
import datetime
from logging import Logger
from multiprocessing import Process, Queue
from pathlib import Path
from typing import List, Tuple

import psutil

import dpx_assessment
import dpx_rawcook
import dpx_post_rawcook
import utils
import shutil


def get_parser() -> argparse.ArgumentParser:
    """
    arguments: None
    returns: parser with one argument: config folder path
    """
    parser = argparse.ArgumentParser(
        prog="driver.py",
        description="Driver script that sets up and initiates rawcook process",
    )
    parser.add_argument(
        "--config",
        dest="config_folder_path",
        required=True,
        help="path to config folder",
    )
    return parser


def get_run_params(config_folder_path: Path) -> dict:
    """
    arguments: config folder path that contains driver, sequence configs
    returns: dictionary with driver configuration
    reads driver configuration, verifies number of sequences, returns driver configuration

    """

    setup: Logger = logging.getLogger("setup")
    setup.info("reading driver configuration")

    try:
        with open(config_folder_path / "driver_config.json") as f:
            driver_config: dict = json.load(f)
    except FileNotFoundError as e:
        setup.error(f"driver_config.json not found in {config_folder_path}")
        raise RuntimeError(e)
    except Exception as e:
        setup.error(f"unexpected error while reading driver configuration")
        raise RuntimeError(e)

    if driver_config["sequence_count"] != (len(os.listdir(config_folder_path)) - 1):
        raise RuntimeError(
            f"sequence count provided to driver does not match with number of files in {config_folder_path}"
        )

    return driver_config


def get_worker_params(config_file_path: Path) -> dict:
    """
    arguments: config folder path that contains driver, sequence configs
    returns: dictionary with driver configuration
    reads driver configuration, verifies number of sequences, returns driver configuration
    returns empty dictionary in case of error
    """

    current_process: int = os.getpid()
    worker: Logger = logging.getLogger(f"worker_{current_process}")
    worker.info("reading sequence configuration")

    try:
        with open(config_file_path) as f:
            worker_config: dict = json.load(f)
    except FileNotFoundError as e:
        worker.error(f"sequence configuration not found at {config_file_path}")
        raise RuntimeError(e)
    except Exception as e:
        worker.error(f"unexpected error while reading sequence configuration")
        raise RuntimeError(e)

    return worker_config


def worker_process(params: dict, q: Queue) -> Queue:
    """
    This is like "main" for each worker, it will execute the whole workflow
        - create working directory and setup logging
        - copy sequence and sample_policy files
        - run dpx scripts
        - restore sequence and delete working directory structure

    :param params: a dictionary of parameters with the worker configuration -> (execution directory, config file, output directory)
    :type params: dict
    :param q: multiprocessing queue to communicate with main
    :type q: multiprocessing.Queue
    :raises RuntimeError: if there is an error while running any part of the pipeline
    :return: multiprocessing queue containing execution info from each worker
    :rtype: multiprocessing.Queue

    """

    # each worker creates its own working directory
    current_process: int = os.getpid()
    try:
        sequence_path: Path = utils.create_working_dir(
            params["execution_folder"]
        )  # execution/wd/seq
    except RuntimeError as e:
        q.put((current_process, False, e))
        return q

    wd: Path = params["execution_folder"] / f"wd_{current_process}"  # execution/wd

    # each worker sets up logging to its own directory
    logging.config.dictConfig(utils.get_log_config(log_directory=wd / "logs"))
    worker: Logger = logging.getLogger(f"worker_{current_process}")
    worker.info("---starting setup---")
    worker.info("created working directory")
    worker.debug(f"{wd=} {sequence_path=}")

    # load sequence config file
    try:
        sequence_config: dict = get_worker_params(
            config_file_path=params["config_file"]
        )
        worker.debug(sequence_config)
    except RuntimeError as e:
        worker.error(f"could not load worker configuration: {e}")
        q.put((current_process, False, "could not load worker configuration"))
        return q

    # copy sequence, policies to folder
    sequence_parent: Path = Path(
        sequence_config["sequence_folder_path"]
    )  # sequence location specified by user
    sequence_destination: Path = (
        sequence_path / sequence_parent.name
    )  # execution/wd/seq/parent.name
    worker.debug(f"{sequence_parent=}")
    worker.debug(f"{sequence_destination=}")
    if sequence_config["in_place"]:
        worker.warning(f"processing sequence in place")
        sequence_destination = sequence_parent

    try:
        utils.move(sequence_parent, sequence_destination)
        utils.copy(
            Path(sequence_config["dpx_policy_path"]),
            (wd / "policies" / "dpx_policy.xml"),
        )
        utils.copy(
            Path(sequence_config["mkv_policy_path"]),
            (wd / "policies" / "mkv_policy.xml"),
        )
    except RuntimeError as e:
        worker.error(f"halting process due to move/copy failure: {e}")
        q.put((current_process, False, "failure during move/copy"))
        utils.move(
            sequence_destination, sequence_parent
        )  # restore sequence in event of failure
        utils.move_logs(wd, params["output_folder_path"], sequence_destination)
        return q
    worker.info("required files present in wd, ready for dpx calls\n")
    worker.info(f"---setup complete---\n")

    # each worker call dpx_assessment, dpx_rawcook and dpx_post_rawcook
    try:
        # call dpx assessment
        assessment_params = {
            "sequence_path": sequence_destination,
            "policy_path": wd / "policies" / "dpx_policy.xml",
            "gap_check": sequence_config["gap_check"],
            "policy_check": sequence_config["dpx_policy_check"],
            "license": sequence_config["license"],
        }
        v2_flag: bool = dpx_assessment.execute(params=assessment_params)

        # call dpx rawcook
        rawcook_params = {
            "sequence_path": sequence_destination,
            "v2_flag": v2_flag,
            "license": sequence_config["license"],
            "frame_md5": sequence_config["frame_md5"],
            "output_path": params["output_folder_path"],
        }
        mkv_path: Path = dpx_rawcook.execute(params=rawcook_params)

        # call dpx post rawcook
        post_params = {
            "mkv_path": mkv_path,
            "policy_path": wd / "policies" / "mkv_policy.xml",
            "policy_check": sequence_config["mkv_policy_check"],
        }
        dpx_post_rawcook.execute(params=post_params)
    except RuntimeError as e:
        worker.error(f"failure during dpx calls: {e}")
        q.put((current_process, False, f"failure during dpx calls: {e}"))
        utils.move(
            sequence_destination, sequence_parent
        )  # restore sequence in event of failure
        utils.move_logs(wd, params["output_folder_path"], sequence_destination)
        return q
    except Exception as e:
        worker.error(f"unexpected failure during dpx calls: {e}")
        q.put((current_process, False, f"unexpected failure during dpx calls: {e}"))
        utils.move(
            sequence_destination, sequence_parent
        )  # restore sequence in event of failure
        utils.move_logs(wd, params["output_folder_path"], sequence_destination)
        return q

    # on success move sequence back to source
    worker.info("---starting clean up---")
    worker.info("restoring sequence to source")
    utils.move(sequence_destination, sequence_parent)

    # on completion move logs
    utils.move_logs(wd, params["output_folder_path"], sequence_destination)

    # move framemd5 from sequence path if it exists
    try:
        if sequence_config["frame_md5"]:
            worker.info(f"moving framemd5 to output folder")
            if sequence_config["in_place"]:
                frame_md5 = sequence_parent.with_suffix(".framemd5")
            else:
                frame_md5 = sequence_path / f"{sequence_parent.name}.framemd5"
            utils.move(
                frame_md5,
                params["output_folder_path"] / f"{frame_md5.name}",
            )
    except RuntimeError as e:
        worker.error(f"failed to move framemd5 to output folder: {e}")
    worker.info("aggregation complete")

    # verify sequence directory has no sequence files and then delete working directory
    worker.info("deleting working directory")
    if list((wd / "sequence").glob("*.dpx")):
        worker.error(
            f"sequence directory still contains dpx files, working directory cannot be deleted"
        )
        q.put((current_process, False, f"working directory could not be deleted"))
        return q
    try:
        shutil.rmtree(wd)
    except Exception as e:
        worker.error(f"unexpected failure during deletion: {e}")
        q.put(
            (
                current_process,
                False,
                f"unexpected failure during working directory deletion",
            )
        )
        return q

    worker.info("---clean up complete---\n")

    # on success, the worker exits
    worker.info("---success---")
    q.put((current_process, True, "successful execution"))
    return q


def main() -> None:

    # setup logging
    now: datetime.datetime = datetime.datetime.now()
    now_format: str = f"{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}"
    default: Path = (
        Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        / "logs"
        / now_format
    )
    logging.config.dictConfig(utils.get_log_config(log_directory=default))
    setup: Logger = logging.getLogger("setup")
    setup.info("starting driver")

    # parse argument to get driver config
    parser = get_parser()
    args = parser.parse_args()
    setup.debug(f"config_folder_path: {args.config_folder_path}")

    # read driver configuration
    try:
        run_params: dict = get_run_params(
            config_folder_path=Path(args.config_folder_path)
        )
    except RuntimeError as e:
        setup.error("failure in reading driver parameters...ending execution")
        setup.error(e)
        return

    # output_folder_path: location specified by user
    output_folder_path: Path = Path(run_params["output_folder_path"])
    sequence_count: int = run_params["sequence_count"]  # number of sequences (workers)
    cpu_affinity: List[int] = [
        _ for _ in range(run_params.get("cpu_affinity", psutil.cpu_count()))
    ]  # available cpus for this execution
    setup.debug(f"output_folder_path: {output_folder_path}")
    setup.info(f"sequence_count: {sequence_count}")

    # setup working directory in specified output path
    try:
        # outputs: final location of results, each thread moves results here
        outputs: Path = utils.create_execution_dir(output_folder_path)
        setup.debug(f"print output folder path to stdout: {outputs}")
        print(str(outputs))
    except RuntimeError as e:
        setup.error("failure in creating working directory...ending execution")
        setup.error(e)
        return

    # initialize workers and start worker process
    setup.info("----------------------------------------")
    setup.info(f"initializing {sequence_count} processes")
    workers: List[Process] = []
    q: Queue = Queue()  # message queue for workers to communicate with driver
    for i in range(sequence_count):
        params = {
            "execution_folder": output_folder_path / "working_directory",
            "config_file": Path(args.config_folder_path) / f"sequence_{i}.json",
            "output_folder_path": outputs,
        }
        setup.debug(f"params {i}: {params}")
        wp = Process(target=worker_process, args=(params, q))
        psutil.Process(wp.pid).cpu_affinity(cpu_affinity)
        workers.append(wp)
        wp.start()
        setup.info(f"init worker: {wp.pid}")

    # write all log locations to config file
    setup.info("writing log config (read by gui)")
    params = {
        "write_path": Path(args.config_folder_path) / "log_config.json",
        "driver_path": default,
        "final_path": outputs,
        "count": sequence_count,
        "sequence_paths": [
            output_folder_path / "working_directory" / f"wd_{x.pid}" / "logs"
            for x in workers
        ],
    }
    utils.write_log_config(**params)

    # wait for processes to end
    for wp in workers:
        wp.join()

    # check message queue and log errors
    while not q.empty():
        result: Tuple[int, bool, str] = q.get()  # (worker id, status , message)
        if not result[1]:
            setup.error(f" worker {result[0]} execution halted: {result[2]}")
            setup.error(f" worker {result[0]} check error logs")

        else:
            setup.info(f" worker {result[0]} completed successfully")

    # delete working directory
    setup.info("deleting working directory")
    wd: Path = output_folder_path / "working_directory"
    try:
        shutil.rmtree(wd)
    except Exception as e:
        setup.error(f"unexpected failure during deletion: {e}")
        return

    # closing messages
    setup.info("----------------------------------------")
    setup.info("all worker execution complete")
    setup.info("driver execution complete")

    try:
        for f in default.iterdir():
            utils.copy(f, outputs / f.name)
    except Exception as e:
        print(f"unexpected failure during driver log copy: {e}")


if __name__ == "__main__":
    main()
