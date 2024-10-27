#!/usr/bin/env python3
"""
Script to run Held's code.
"""
import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import shuffle

from tqdm import tqdm

import conf
from utils.utils import get_n_jobs, get_instances_from_set, get_n_jobs

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
# =============================================================================
# === Held's code only works on Linux =========================================
logs = "/home/ieremies/logs"
color = "/home/ieremies/exactcolors/color"
inst = "/home/ieremies/inst"
# =============================================================================


def run_instance(instance, tl, force=False):
    cmd = f"timeout --kill-after={0.01*tl}s {1.1*tl}s {color} -l {tl} -s 0 {inst}/all/{instance}"
    log_file = f"{logs}/held/{instance}.log"

    if os.path.exists(log_file) and not force:
        return

    with open(log_file, "w") as fd:
        try:
            subprocess.run(
                cmd.split(), timeout=1.2 * tl, stdout=fd, stderr=fd, text=True
            )
        except subprocess.TimeoutExpired:
            pass
        except Exception as _:
            return


def run(inst_set, tl, force=False):
    if not os.path.exists(f"{logs}/held"):
        os.makedirs(f"{logs}/held")

    # get instances from the given set
    instances = get_instances_from_set(inst, inst_set)
    shuffle(instances)

    results = []
    with ThreadPoolExecutor(max_workers=get_n_jobs()) as ex:
        f2e = {ex.submit(run_instance, i, tl, force): i for i in instances}
        for future in tqdm(as_completed(f2e), total=len(f2e)):
            results.append(future.result())


if __name__ == "__main__":
    args = arg_parser.parse_args()
    run(args.inst_set, args.time_limit)
