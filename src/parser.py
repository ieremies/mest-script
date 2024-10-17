#!/usr/bin/env python3
import inspect
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

from loguru import logger
from tqdm import tqdm

import conf
import utils.parse_functions as pf
from utils.read_write import write_dict_to_csv
from utils.utils import get_all_files

# === Argument parsing ========================================================
parser = argparse.ArgumentParser(description="Help parsing the logs.")
parser.add_argument("directory", type=str, help="Directory with the logs to parse.")
parser.add_argument(
    "output_csv", type=str, help="Output CSV file with the parsed logs."
)
# =============================================================================
# === Check if on MacOS or Linux ==============================================
if os.uname().sysname == "Darwin":
    logs = conf.macos_logs
else:
    logs = conf.linux_logs
# =============================================================================
# === Logger configuration ====================================================
logger.remove()
fmt = "{time:DD MMM YY (ddd) at HH:mm:ss} | {level} | {message}"
logger.add(sys.stderr, format=fmt, level="ERROR")
logger.add(f"{logs}/parser.log", format=fmt, level="INFO", rotation="10 MB")
# =============================================================================


@logger.catch
def parse_inst(log_file, inst_name):
    d = {"lb": "", "ub": "", "time": ""}

    for name, func in inspect.getmembers(pf, inspect.isfunction):
        if inspect.isfunction(func) and name.startswith("get"):
            key, value = func(log_file)
            d[key] = value

    for error in d["errors"]:
        logger.error(f"❌ {inst_name}: {error}")
    d["errors"] = len(d["errors"])

    for warn in d["warnings"]:
        logger.warning(f"⚠️ {inst_name}: {warn}")
    d["warnings"] = len(d["warnings"])

    if d["solved"] != "":
        d["lb"] = d["solved"]
        d["ub"] = d["solved"]

    return d


def parse_inst_wrapper(log_file):
    inst_name = os.path.basename(log_file.replace(".log", ""))
    # with open(log_file, "r") as f:
    #     log_file = f.readlines()
    return inst_name, parse_inst(log_file, inst_name)


def parse(directory, output_csv):
    all_files = get_all_files(directory)
    results = {}

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {
            executor.submit(parse_inst_wrapper, log_file): log_file
            for log_file in all_files
        }

        print(f"🔍 Parsing {len(all_files)} log files with {os.cpu_count()} workers")

        for future in tqdm(as_completed(futures), total=len(futures), smoothing=0.0):
            inst_name, result = future.result()
            results[inst_name] = result

    write_dict_to_csv(results, output_csv)


if __name__ == "__main__":
    parse(sys.argv[1], sys.argv[2])
