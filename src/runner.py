#!/usr/bin/env python3
"""
Script to run a build in a instance set.
"""
import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from parser import parse_inst

import pandas as pd
from tqdm import tqdm

import conf
from utils.utils import get_instances_from_set, get_n_jobs
import utils.checker

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
arg_parser.add_argument(
    "--clean",
    action="store_true",
    default=False,
    help="Clean the logs directory.",
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


def clean_logs(build):
    cmd = f"rm -rf {logs}/tmp/{build}"
    subprocess.run(cmd.split())


def clean_timeouts(build):
    cmd = f"grep -L 'atexit' {logs}/tmp/{build}/*.log | xargs rm"
    subprocess.run(cmd, shell=True)


def clean_errors(build):
    cmd = f"grep -E 'ERR|FATL' {logs}/tmp/{build}/*.log | xargs rm"
    subprocess.run(cmd, shell=True)


def run_instance(build, instance, tl=conf.time_limit, force=False):
    """
    Run a single instance with the given build.
    """
    cmd = conf.cmd.format(
        code=code, build=build, inst_set=f"{inst}/all", instance=instance
    )
    log_file = f"{logs}/tmp/{build}/{instance}.log"

    # if log_file exists
    if force or not os.path.exists(log_file):
        with open(log_file, "w") as fd:
            try:
                subprocess.run(cmd.split(), timeout=tl, stdout=fd, stderr=fd, text=True)
            except subprocess.TimeoutExpired:
                pass
            except Exception as _:
                print(f"❌ {instance}")
                return

    try:
        df = parse_inst(log_file)
    except:
        print(f"Error while parsing {instance}")
        return
    return df


def run(build, inst_set, tl=conf.time_limit, force=False, output_csv="tmp.csv"):
    if not os.path.exists(f"{logs}/tmp"):
        os.makedirs(f"{logs}/tmp")

    if not os.path.exists(f"{logs}/tmp/{build}"):
        os.makedirs(f"{logs}/tmp/{build}")

    # get instances from the given set
    instances = get_instances_from_set(inst, inst_set)
    print(len(instances))

    results = []
    workers = get_n_jobs() if not "debug" in build else os.cpu_count()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        f2e = {ex.submit(run_instance, build, i, tl, force): i for i in instances}
        for future in tqdm(as_completed(f2e), total=len(f2e), smoothing=0.0):
            results.append(future.result())

    df = pd.concat(results, ignore_index=True)
    df = df.drop(columns=["errors", "warnings"])
    if output_csv:
        df.to_csv(output_csv, index=False)

    # cmd = f"tar -czf {logs}/{build}.tar.gz {logs}/tmp/{build}"
    # subprocess.run(cmd.split())

    for i in df.iterrows():
        s = utils.checker.check(dict(i[1]))
        if s:
            print(*s, sep="\n")

    print("-" * 18)
    no_lb = df[df["lb"] == ""].shape[0]
    solved = df[df["lb"] == df["ub"]].shape[0]
    total_time = df["time"].sum()
    print(f"Without LB : {no_lb}")
    print(f"Solved     : {solved}")
    print(f"Total time : {total_time:.2f}s")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    if args.clean:
        clean_logs(args.build)
    else:
        run(
            args.build,
            args.inst_set,
            args.time_limit,
            args.force,
            output_csv=args.build.replace(".e", ".csv"),
        )
