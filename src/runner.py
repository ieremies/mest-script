#!/usr/bin/env python3
import argparse, subprocess, os
import concurrent.futures
from tqdm import tqdm

import conf
from utils.parser import parse
from utils.io import write_csv, get_all_files


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
    "-k",
    "--keep",
    action="store_true",
    default=False,
    help="Keep the individual logs under tmp, default is to remove it.",
)
arg_parser.add_argument(
    "-tl",
    dest="time_limit",
    type=int,
    default=conf.time_limit,
    help="Time limit for the execution of each command.",
)

# check if on MacOS or Linux:
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


def run_instance(build, instance, tl=conf.time_limit):
    cmd = conf.cmd.format(code=code, build=build, inst=f"{inst}/all", instance=instance)
    log_file = f"{logs}/tmp/{instance}_{build}.log"

    if conf.debug:
        print(cmd, log_file)

    if os.path.exists(log_file):
        print(f"⚠️ {instance} already solved.")
        return parse(log_file, instance.replace(".col", ""))

    with open(log_file, "w") as fd:
        try:
            subprocess.run(cmd.split(), timeout=tl, stdout=fd, stderr=fd, text=True)
        except subprocess.TimeoutExpired:
            pass

    return parse(log_file, instance.replace(".col", ""))


def run(build, inst_set, tl=conf.time_limit):
    if not os.path.exists(f"{logs}/tmp"):
        os.makedirs(f"{logs}/tmp")

    instances = os.listdir(f"{inst}/{inst_set}")

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_element = {
            executor.submit(run_instance, build, instance, tl): instance
            for instance in instances
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_element),
            total=len(future_to_element),
            desc=f"⏳ Running {build} on {inst_set} instances on Spock...",
        ):
            result = future.result()
            results.append(result)

    write_csv(results, f"{logs}/tmp.csv")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    run(args.build, args.inst_set, args.time_limit)
    if not args.keep:
        os.system(f"rm -rf {logs}/tmp")
