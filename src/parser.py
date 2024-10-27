#!/usr/bin/env python3
import inspect
import sys, os
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm
import warnings
import pandas as pd

# Suppress FutureWarning messages
warnings.simplefilter(action="ignore", category=FutureWarning)

import conf
import utils.parse_functions as pf
from utils.utils import get_all_files

logs = conf.macos_logs if os.uname().sysname == "Darwin" else conf.linux_logs


def parse_inst(log_file) -> pd.DataFrame:
    # Create new dataframe, those are the minimum columns
    df = pd.DataFrame(columns=["instance", "lb", "ub", "time", "errors", "warnings"])
    inst_name = log_file.split("/")[-1].replace(".log", "")
    df["instance"] = [inst_name]

    for name, func in inspect.getmembers(pf, inspect.isfunction):
        if inspect.isfunction(func) and name.startswith("get"):
            dict = func(log_file)
            for key in dict:
                if type(dict[key]) == list and len(dict[key]) > 1:
                    df[key] = [dict[key]]
                else:
                    df[key] = dict[key]

    if df["errors"][0]:
        for e in df["errors"][0]:
            print(f"❌ {inst_name + ' ' * (14 - len(inst_name))}: {e}")
    df["errors"] = len(df["errors"])

    # TODO treat warnings
    df["warnings"] = len(df["warnings"])

    if df["solved"][0] != "":
        df["lb"] = df["solved"]
        df["ub"] = df["solved"]

    return df


def parse_all(directory, output_csv: str = "") -> pd.DataFrame:
    all_files = get_all_files(directory)
    results = []

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(parse_inst, f): f for f in all_files}
        for future in tqdm(as_completed(futures), total=len(futures), smoothing=0.0):
            results.append(future.result())

    df = pd.concat(results, ignore_index=True)
    if output_csv:
        df.to_csv(output_csv, index=False)

    return df


if __name__ == "__main__":
    parse_all(sys.argv[1], sys.argv[2])
