#!/usr/bin/env python3
"""
Script responsible for doing my testing.
"""
import conf
import argparse
from utils.checker import check
from utils.ssh import spock, beam, vulcan

parser = argparse.ArgumentParser(description="Help testing my code.")
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
    "-p",
    "--primal",
    action="store_true",
    default=False,
    help="Only test the primal.e build.",
)
parser.add_argument(
    "-d",
    "--debug",
    action="store_true",
    default=False,
    help="Only test the debug.e build.",
)
parser.add_argument(
    "-c",
    "--clean",
    action="store_true",
    default=False,
    help="Clean the tmp folder",
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


def send_code():
    print("⏳ Sending code to Spock...")

    vulcan(conf.macos_code)
    spock(
        f"cmake -B {conf.spock_code}/build -S {conf.spock_code}"
    )  # generate build files
    print("\033[F✅")


def compile_code(build=conf.default_build):
    print(f"⏳ Spock is compiling {build}...")
    spock(f"cmake --build {conf.spock_code}/build -- -j --silent -k {build}")
    print("\033[F✅")


def run(build=conf.default_build, instance=conf.default_instances, tl=conf.time_limit):
    print(
        f"⏳ Spock is running {build} on {instance} instances with time limit of {tl}s..."
    )
    cmd = f"python3 {conf.spock_script}/src/runner.py {build} {instance} -tl {tl}"

    spock(cmd, supp=False)

    print("\033[F✅")


def check_wrapper():
    print("⏳ Checking the results...")
    if not check(conf.macos_hist, "tmp.csv"):
        exit(1)
    print("\033[F✅")


def clean_tmp():
    print("⏳ Cleaning the tmp folder...")
    spock(f"rm -rf {conf.spock_logs}/tmp")
    print("\033[F✅")


def parse_tmp():
    print("⏳ Parsing the tmp folder...")
    spock(
        f"python3 {conf.spock_script}/src/parser.py {conf.spock_logs}/tmp {conf.spock_logs}/tmp.csv",
        supp=False,
    )
    # print("\033[F✅")


if __name__ == "__main__":
    args = parser.parse_args()

    if args.parse:
        parse_tmp()
        beam(f"{conf.spock_logs}/tmp.csv")  # only the last run is saved
        check(conf.macos_hist, "tmp.csv")
        exit(0)

    send_code()

    if not args.primal:
        compile_code("debug.e")
        run("debug.e", instance=args.instance, tl=args.time_limit)
        parse_tmp()
        if not (args.keep and args.debug):
            clean_tmp()

    if not args.debug:
        compile_code("primal.e")
        run("primal.e", instance=args.instance, tl=args.time_limit)
        parse_tmp()
        if not args.keep:
            clean_tmp()

    beam(f"{conf.spock_logs}/tmp.csv")  # only the last run is saved
    check(conf.macos_hist, "tmp.csv")

    print("Done!")
