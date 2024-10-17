#!/usr/bin/env python3
"""
Script to run a build in a instance set.
"""
import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

from loguru import logger
from tqdm import tqdm

import conf
from utils.utils import get_n_jobs, get_instances_from_set

# === Argument parsing ========================================================
arg_parser = argparse.ArgumentParser(description="Help running my code.")
arg_parser.add_argument(
    "build",
    type=str,
    default=conf.default_build,
    help=f"Which build to run, default is {conf.default_build}",
)
arg_parser.add_argument(
    "inst_set",
    type=str,
    default=conf.default_instances,
    help=f"Which instance set to run, default is {conf.default_instances}",
)
arg_parser.add_argument(
    "-tl",
    dest="time_limit",
    type=int,
    default=conf.time_limit,
    help="Time limit for the execution of each command.",
)
arg_parser.add_argument(
    "--force",
    action="store_true",
    default=False,
    help="Force the execution of the build.",
)
# =============================================================================
# === Check if on MacOS or Linux ==============================================
if os.uname().sysname == "Darwin":
    path = conf.macos_path
    code = conf.macos_code
    inst = conf.macos_instances
    logs = conf.macos_logs
    script = conf.macos_script
else:
    path = conf.linux_path
    code = conf.linux_code
    inst = conf.linux_instances
    logs = conf.linux_logs
    script = conf.linux_script
# =============================================================================
# === Logger configuration ====================================================
logger.remove()
fmt = "{time:DD MMM YY (ddd) at HH:mm:ss} | {level} | {message}"
logger.add(
    f"{logs}/runner.log",
    format=fmt,
    level="INFO",
    rotation="10 MB",
)
logger.add(
    f"{logs}/runner_warning.log",
    format=fmt,
    level="WARNING",
    rotation="10 MB",
)
# =============================================================================


@logger.catch
def run_instance(build, instance, tl=conf.time_limit, force=False):
    """
    Run a single instance with the given build.
    """
    cmd = conf.cmd.format(
        code=code, build=build, inst_set=f"{inst}/all", instance=instance
    )
    log_file = f"{logs}/tmp/{build}/{instance}.log"

    if os.path.exists(log_file) and not force:
        logger.warning(f"{build}/{instance}: Skipping")
        return

    logger.info(f"{build}/{instance}: Started...")
    timeout = False
    with open(log_file, "w") as fd:
        try:
            subprocess.run(cmd.split(), timeout=tl, stdout=fd, stderr=fd, text=True)
        except subprocess.TimeoutExpired:
            logger.error(f"{build}/{instance}: Timeout")
            timeout = True
        except Exception as e:
            logger.error(f"{build}/{instance}: {e}")
            return

    if not os.path.exists(log_file):
        logger.error(f"{build}/{instance}: Log file not found.")
        return

    with open(log_file, "r") as fd:
        lines = fd.readlines()
        if len(lines) > 1 and not timeout:
            logger.info(
                f"{build}/{instance}: Done -> {lines[-2].strip()[:80].replace(' '*10, ' ')}"
            )


def is_file_newer_than_1_minute(directory):
    current_time = time.time()
    one_minute_ago = current_time - 60

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) > one_minute_ago:
                return True
    return False


@logger.catch
def run(build, inst_set, tl=conf.time_limit, force=False):
    if not os.path.exists(f"{logs}/tmp"):
        os.makedirs(f"{logs}/tmp")

    if not os.path.exists(f"{logs}/tmp/{build}"):
        os.makedirs(f"{logs}/tmp/{build}")

    # get instances from the given set
    instances = get_instances_from_set(inst, inst_set)
    start = datetime.now()

    logger.info(f"Running {len(instances)} instances whith {get_n_jobs()} workers.")

    results = []
    workers = get_n_jobs() if not "debug" in build else os.cpu_count()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        f2e = {ex.submit(run_instance, build, i, tl, force): i for i in instances}
        # tqdm with ellapsed time as prefix
        for future in tqdm(
            as_completed(f2e),
            total=len(f2e),
            desc="Instances",
            unit=" inst",
            smoothing=0.0,
        ):
            results.append(future.result())

            logger.info(f"Done {len(results)} | Total {len(instances)}.")

            # Average time per instance
            elap = datetime.now() - start
            avg = elap / len(results)
            remain = avg * (len(instances) - len(results))
            max_time = (len(instances) - len(results)) * tl
            logger.info(
                f"Elap: {elap} | Avg: {avg} | Remain: {remain} | Max: {max_time}"
            )

    # compress the logs
    # if not is_file_newer_than_1_minute(f"{logs}/tmp/{build}"):
    #     return
    logger.info("Compressing logs...")
    cmd = f"tar -czf {logs}/{build}.tar.gz {logs}/tmp/{build}"
    subprocess.run(cmd.split())
    logger.info("Done compressing logs.")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    run(args.build, args.inst_set, args.time_limit, args.force)
