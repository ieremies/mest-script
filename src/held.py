#!/usr/bin/env python3
"""
Script to run Held's code.
"""
import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import shuffle
from datetime import datetime

from loguru import logger
from tqdm import tqdm

import conf
from utils.read_write import get_all_files, write_dict_to_csv
from utils.jobs import get_n_jobs
from utils.parse_functions import grep

# === Argument parsing ========================================================
arg_parser = argparse.ArgumentParser(description="Help running Held's code.")
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
arg_parser.add_argument(
    "--parse",
    action="store_true",
    default=False,
    help="Only parse the logs.",
)
# =============================================================================
# === Held's code only works on Linux =========================================
logs = "/home/ieremies/logs"
color = "/home/ieremies/exactcolors/color"
inst = "/home/ieremies/inst"
# =============================================================================
# === Logger configuration ====================================================
logger.remove()
fmt = "{time:DD MMM YY (ddd) at HH:mm:ss} | {level} | {message}"
logger.add(
    f"{logs}/held.log",
    format=fmt,
    level="INFO",
    rotation="10 MB",
)
logger.add(
    f"{logs}/held_warning.log",
    format=fmt,
    level="WARNING",
    rotation="10 MB",
)
# =============================================================================


def remove_timedout():
    # grep -rL "Opt Colors:" . | xargs rm -f
    pass


@logger.catch
def run_instance(instance, tl, force=False):
    cmd = f"timeout --kill-after={0.01*tl}s {1.1*tl}s {color} -l {tl} {inst}/all/{instance}"
    log_file = f"{logs}/held/{instance}.log"

    if os.path.exists(log_file) and not force:
        logger.warning(f"{instance}: Skipping")
        return

    logger.info(f"{instance}: Running")
    with open(log_file, "w") as fd:
        try:
            subprocess.run(
                cmd.split(), timeout=1.2 * tl, stdout=fd, stderr=fd, text=True
            )
        except subprocess.TimeoutExpired:
            logger.warning(f"{instance}: Timeout")
        except Exception as e:
            logger.error(f"{instance}: {e}")
            return

    if not os.path.exists(log_file):
        logger.error(f"{instance}: No log file")
        return


@logger.catch
def run(inst_set, tl, force=False):
    if not os.path.exists(f"{logs}/held"):
        os.makedirs(f"{logs}/held")

    # get instances from the given set
    instances = [i.split("/")[-1] for i in get_all_files(f"{inst}/{inst_set}")]
    shuffle(instances)

    start = datetime.now()

    logger.info(f"Running {len(instances)} instances whith {get_n_jobs()} workers.")

    results = []
    with ThreadPoolExecutor(max_workers=get_n_jobs()) as ex:
        f2e = {ex.submit(run_instance, i, tl, force): i for i in instances}
        for future in tqdm(as_completed(f2e), total=len(f2e)):
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


@logger.catch
def parse_inst(log_file):
    d = {"lb": "", "ub": "", "time": ""}
    inst_name = os.path.basename(log_file).replace(".log", "")

    time = grep("Computing coloring took", log_file)
    if time:
        d["time"] = float(time[0].split()[-2])
    else:
        logger.error(f"{inst_name}: No time found")

    bounds = grep("Compute coloring finished:", log_file)
    if bounds:
        d["lb"] = float(bounds[0].split()[-4])
        d["ub"] = float(bounds[0].split()[-1])
    else:
        logger.error(f"{inst_name}: No bounds found")

    return inst_name, d


@logger.catch
def parse(directory, output_csv):
    all_files = get_all_files(directory)
    results = {}

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        futures = {ex.submit(parse_inst, f): f for f in all_files}

        for future in tqdm(as_completed(futures), total=len(futures)):
            inst_name, result = future.result()
            results[inst_name] = result

    write_dict_to_csv(results, output_csv)

    # compress the logs
    logger.info("Compressing logs...")
    cmd = f"tar -czf {logs}/held.tar.gz {logs}/held"
    subprocess.run(cmd.split())
    logger.info("Done compressing logs")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    if not args.parse:
        run(args.inst_set, args.time_limit, force=args.force)
    parse(f"{logs}/held", f"{logs}/held.csv")
