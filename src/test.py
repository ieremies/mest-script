#!/usr/bin/env python3
"""
Script responsible for doing my testing.
"""
import conf
import argparse
from utils.checker import check
from utils.ssh import beam_to, beam_from, command

parser = argparse.ArgumentParser(description="Help testing my code.")
parser.add_argument(
    "-m",
    "--machine",
    type=str,
    default=conf.default_machine,
    help=f"Which machine to run the code, default is {conf.default_machine}",
)
parser.add_argument(
    "-i",
    "--instance",
    type=str,
    default=conf.default_instances,
    help=f"Which instance set to run, default is {conf.default_instances}",
)
parser.add_argument(
    "-tl",
    "--time_limit",
    type=int,
    default=conf.time_limit,
    help="Time limit for the execution of each command.",
)
parser.add_argument(
    "-k",
    "--keep",
    action="store_true",
    default=False,
    help="Keep the individual logs under tmp, default is to remove it.",
)
parser.add_argument(
    "-b",
    "--build",
    type=str,
    default=conf.default_build,
    help=f"Which build to run, default is {conf.default_build}",
)
parser.add_argument(
    "-c",
    "--clean",
    action="store_true",
    default=False,
    help="Clean the tmp folder",
)
parser.add_argument(
    "-cto",
    "--check_time_out",
    action="store_true",
    default=False,
    help="Clean the results that have timed out",
)
parser.add_argument(
    "--send",
    action="store_true",
    default=False,
    help="Only send the code to Spock",
)
parser.add_argument(
    "--parse",
    action="store_true",
    default=False,
    help="Only parse the tmp folder",
)


def send_code(machine=conf.default_machine):
    if machine == "mac":
        return

    print(f"⏳ Sending code to {machine}...")

    beam_to(machine, conf.macos_code)
    command(machine, f"cmake -B {conf.linux_code}/build -S {conf.linux_code}")
    print("\033[F✅")


def compile_code(machine=conf.default_machine, build=conf.default_build):
    code_path = conf.macos_code if machine == "mac" else conf.linux_code
    print(f"⏳ {machine} is compiling {build}...")
    command(machine, f"cmake --build {code_path}/build -- -j --silent -k {build}")
    print("\033[F✅")


def run(
    machine=conf.default_machine,
    build=conf.default_build,
    instance=conf.default_instances,
    tl=conf.time_limit,
):
    script_path = conf.macos_script if machine == "mac" else conf.linux_script
    print(f"⏳ {machine} is running {build} on {instance} with time limit of {tl}s...")
    cmd = f"python3 {script_path}/src/runner.py {build} {instance} -tl {tl}"

    command(machine, cmd, supp=False)

    print("\033[F✅")


def check_wrapper():
    print("⏳ Checking the results...")
    if not check(conf.macos_hist, "tmp.csv"):
        exit(1)
    print("\033[F✅")


def clean_tmp(machine=conf.default_machine):
    logs_path = conf.macos_logs if machine == "mac" else conf.linux_logs
    print("⏳ Cleaning the tmp folder...")
    command(machine, f"rm -rf {logs_path}/tmp")
    print("\033[F✅")


def parse(machine, build):
    logs_path = conf.macos_logs if machine == "mac" else conf.linux_logs
    script_path = conf.macos_script if machine == "mac" else conf.linux_script
    print("⏳ Parsing the tmp folder...")
    command(
        machine,
        f"python3 {script_path}/src/parser.py {logs_path}/tmp/{build} {logs_path}/tmp.csv",
        supp=False,
    )
    # print("\033[F✅")


def script(machine, build, inst, tl, keep, debug):
    compile_code(machine, build)
    run(machine, build, instance=inst, tl=tl)
    parse(machine, build)
    beam_from(machine, f"{conf.linux_logs}/tmp.csv")  # only the last run is saved
    check(conf.macos_hist, "tmp.csv")


if __name__ == "__main__":
    args = parser.parse_args()

    if args.parse:
        parse(args.machine, args.build)
        beam_from(args.machine, f"{conf.linux_logs}/tmp.csv")
        check(conf.macos_hist, "tmp.csv")
        exit(0)

    if args.clean:
        clean_tmp(args.machine)
        exit(0)

    if not args.parse:
        script(
            args.machine,
            args.build,
            args.instance,
            args.time_limit,
            args.keep,
            conf.debug,
        )

    print("Done!")
