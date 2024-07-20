#!/usr/bin/env python3
import subprocess
import sys
from utils.read_write import get_all_files, write_dict_to_csv
import inspect
from tqdm import tqdm
import utils.parse_functions as pf
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


def grep(pattern, path):
    try:
        result = subprocess.run(
            ["grep", "-r", pattern, path], capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as _:
        return []


def parse_inst(log_file, inst_name):
    d = {"lb": "", "ub": "", "time": ""}

    for name, func in inspect.getmembers(pf, inspect.isfunction):
        if inspect.isfunction(func) and name.startswith("get"):
            key, value = func(log_file)
            d[key] = value

    # TODO more than one component:
    # - add to main: LOG_F(INFO, "Lower bound %d", asn->get_lb()); and get the last one
    #    - this is a shitty way to do
    # - run dsatur for the hole graph and get the first one

    for error in d["errors"]:
        print(f"❌ {inst_name}: {error}")
    d["errors"] = len(d["errors"])

    # for warn in d["warnings"]:
    #     print(f"⚠️ {inst_name}: {warn}")
    d["warnings"] = len(d["warnings"])

    if d["solved"] != "":
        d["lb"] = d["solved"]
        d["ub"] = d["solved"]

    return d


def parse_inst_wrapper(log_file):
    inst_name = (
        os.path.basename(log_file)
        .replace("_debug.e.log", "")
        .replace("_primal.e.log", "")
    )
    return inst_name, parse_inst(log_file, inst_name)


def parse(directory, output_csv):
    all_files = get_all_files(directory)
    results = {}

    # Use ThreadPoolExecutor to parallelize the processing
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Create a future for each file processing
        futures = {
            executor.submit(parse_inst_wrapper, log_file): log_file
            for log_file in all_files
        }

        # Use tqdm to track the progress of futures as they complete
        for future in tqdm(as_completed(futures), total=len(futures)):
            inst_name, result = future.result()
            results[inst_name] = result

    write_dict_to_csv(results, output_csv)


if __name__ == "__main__":
    parse(sys.argv[1], sys.argv[2])
