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
import utils.checker


logs = conf.macos_logs if os.uname().sysname == "Darwin" else conf.linux_logs


def parse_inst(log_file) -> pd.DataFrame:
    # Create new dataframe, those are the minimum columns
    df = pd.DataFrame(columns=["instance", "lb", "ub", "time", "errors", "warnings"])
    inst_name = log_file.split("/")[-1].replace(".log", "")
    df["instance"] = [inst_name]

    for name, func in inspect.getmembers(pf, inspect.isfunction):
        if inspect.isfunction(func) and name.startswith("get"):
            try:
                d = func(log_file)
            except Exception as e:
                print(f"Error in {name} for {inst_name}: {e}")
                continue

            for key in d:
                if type(d[key]) is list and len(d[key]) > 1:
                    df[key] = [d[key]]
                else:
                    df[key] = d[key]

    if df["errors"][0] and len(df["errors"][0][0]) > 20:
        print(f"\n❌ {inst_name + ' ' * (14 - len(inst_name))}: {df['errors'][0][0]}")
        df["errors"] = len(df["errors"])
    else:
        df["errors"] = None

    # TODO treat warnings
    df["warnings"] = len(df["warnings"]) - 1

    for i in df.iterrows():
        s = utils.checker.check(dict(i[1]))
        if s:
            print(*s, sep="\n")

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
