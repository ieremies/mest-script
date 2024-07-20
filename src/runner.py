#!/usr/bin/env python3
"""
Script to run a build in a instance set.
"""
import argparse, subprocess, os
import concurrent.futures
from tqdm import tqdm

import conf
from utils.read_write import get_all_files


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
    path = conf.spock_path
    code = conf.spock_code
    inst = conf.spock_instances
    logs = conf.spock_logs
    script = conf.spock_script
# =============================================================================


def run_instance(build, instance, tl=conf.time_limit, force=False):
    """
    Run a single instance with the given build.
    """
    cmd = conf.cmd.format(code=code, build=build, inst=f"{inst}/all", instance=instance)
    log_file = f"{logs}/tmp/{build}/{instance}.log"

    if os.path.exists(log_file) and not force:
        print(f"⚠️ {instance} already solved.")

    with open(log_file, "w") as fd:
        try:
            subprocess.run(cmd.split(), timeout=tl, stdout=fd, stderr=fd, text=True)
        except subprocess.TimeoutExpired:
            pass


def run(build, inst_set, tl=conf.time_limit, force=False):
    if not os.path.exists(f"{logs}/tmp"):
        os.makedirs(f"{logs}/tmp")

    if not os.path.exists(f"{logs}/tmp/{build}"):
        os.makedirs(f"{logs}/tmp/{build}")

    # get instances from the given set
    instances = [i.split("/")[-1] for i in get_all_files(f"{inst}/{inst_set}")]

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        future_to_element = {
            executor.submit(run_instance, build, instance, tl, force): instance
            for instance in instances
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_element),
            total=len(future_to_element),
        ):
            results.append(future.result())


if __name__ == "__main__":
    args = arg_parser.parse_args()
    run(args.build, args.inst_set, args.time_limit, args.force)
