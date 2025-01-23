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
import pandas as pd

import conf
from utils.utils import get_n_jobs, get_instances_from_set, get_n_jobs, get_all_files
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
# =============================================================================
# === Held's code only works on Linux =========================================
logs = "/home/ieremies/logs"
color = "/home/ieremies/exactcolors/color"
inst = "/home/ieremies/inst"
# =============================================================================


def run_instance(instance, tl, force=False):
    cmd = f"timeout --kill-after={0.01*tl}s {1.1*tl}s {color} -l {tl} {inst}/all/{instance}"
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


def parse_inst(log_file) -> pd.DataFrame:
    df = pd.DataFrame(
        columns=["instance", "lb", "ub", "time", "root_lb", "root_ub", "root_time"]
    )
    inst_name = log_file.split("/")[-1].replace(".log", "")
    df["instance"] = [inst_name]

    root = grep("Finished initial bounds: LB", log_file)
    if not root:
        dsatur = grep("Greedy Colors:", log_file)
        if dsatur:
            df["ub"] = int(dsatur[0].split("Greedy Colors: ")[1].split(" in")[0])
            df["root_ub"] = df["ub"]
        return df

    df["root_lb"] = int(root[0].split("LB ")[1].split(" and UB")[0])
    df["root_ub"] = int(root[0].split("and UB ")[1].split(" in")[0])
    df["root_time"] = float(root[0].split("in ")[1].split(" seconds")[0])

    opt = grep("Compute coloring finished: LB", log_file)
    if not opt:
        # Upper bound improved: LB %d and UB %d
        all_ub = grep("Upper bound improved:", log_file)
        if not all_ub:
            df["ub"] = df["root_ub"]
        else:
            df["ub"] = int(all_ub[-1].split("and UB ")[1])

        # Lower bound improved: LB %d and UB %d
        all_lb = grep("Lower bound improved:", log_file)
        if not all_lb:
            df["lb"] = df["root_lb"]
        else:
            df["lb"] = int(all_lb[-1].split("LB ")[1])
        return df

    df["lb"] = int(opt[0].split("LB ")[1].split(" and UB")[0])
    df["ub"] = int(opt[0].split("and UB ")[1])

    compute = grep("Computing coloring took", log_file)
    if not compute:
        dsatur = grep("Greedy Colors:", log_file)
        df["ub"] = int(dsatur[0].split("Greedy Colors: ")[1].split(" in")[0])
        return df

    df["time"] = float(compute[0].split("took ")[1].split(" seconds")[0])

    return df


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


def parse_all(directory, output_csv: str = "") -> pd.DataFrame:
    all_files = get_all_files(directory)
    results = []

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(parse_inst, f): f for f in all_files}
        for future in tqdm(as_completed(futures), total=len(futures), smoothing=0.0):
            results.append(future.result())

    df = pd.concat(results, ignore_index=True)
    if output_csv:
        df = df.sort_values(by="instance")
        df.to_csv(output_csv, index=False)

    return df


if __name__ == "__main__":
    args = arg_parser.parse_args()
    run(args.inst_set, args.time_limit)
    parse_all(f"{logs}/held", "held.csv")
