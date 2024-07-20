#!/usr/bin/env python3
"""
Script to run Held's code.
"""
import subprocess
import os
import argparse
import conf
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from utils.read_write import get_all_files, write_dict_to_csv

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
    help="Parse the logs.",
)
# =============================================================================
# === Held's code only works on Linux =========================================
logs = "/home/ieremies/logs"
color = "/home/ieremies/exactcolors/color"
inst = "/home/ieremies/inst"
# =============================================================================


def run_instance(instance, tl):
    cmd = f"timeout --kill-after={0.001*tl}s {1.1*tl}s {color} -l {tl} {inst}/all/{instance}"
    log_file = f"{logs}/held/{instance}.log"

    with open(log_file, "w") as fd:
        try:
            subprocess.run(
                cmd.split(), timeout=1.2 * tl, stdout=fd, stderr=fd, text=True
            )
        except subprocess.TimeoutExpired:
            pass


def run(inst_set, tl):
    if not os.path.exists(f"{logs}/held"):
        os.makedirs(f"{logs}/held")

    # get instances from the given set
    instances = [i.split("/")[-1] for i in get_all_files(f"{inst}/{inst_set}")]

    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_element = {executor.submit(run_instance, i, tl): i for i in instances}
        for future in tqdm(
            as_completed(future_to_element),
            total=len(future_to_element),
        ):
            results.append(future.result())


def grep(pattern, path):
    try:
        result = subprocess.run(
            ["grep", "-r", pattern, path], capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as _:
        return []


def parse_inst(log_file):
    d = {"lb": "", "ub": "", "time": ""}
    inst_name = os.path.basename(log_file).replace(".log", "")

    time = grep("Computing coloring took", log_file)
    if time:
        d["time"] = float(time[0].split()[-2])

    bounds = grep("Compute coloring finished:", log_file)
    if bounds:
        d["lb"] = float(bounds[0].split()[-4])
        d["ub"] = float(bounds[0].split()[-1])

    return inst_name, d


def parse(directory, output_csv):
    all_files = get_all_files(directory)
    results = {}

    # Use ThreadPoolExecutor to parallelize the processing
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Create a future for each file processing
        futures = {
            executor.submit(parse_inst, log_file): log_file for log_file in all_files
        }

        for future in tqdm(as_completed(futures), total=len(futures)):
            inst_name, result = future.result()
            results[inst_name] = result

    write_dict_to_csv(results, output_csv)


if __name__ == "__main__":
    args = arg_parser.parse_args()
    if not args.parse:
        run(args.inst_set, args.time_limit)
    parse(f"{logs}/held", f"{logs}/held.csv")
