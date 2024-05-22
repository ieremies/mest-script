#!/usr/bin/env python3
"""
Script to help execute the tests in my master's code.
"""

# === Check of we are in MacOS or Linux ================================
import os

linux_path = "/home/ieremies"
macos_path = "/Users/ieremies/mest"

if os.uname().sysname == "Darwin":
    path = macos_path
else:
    path = linux_path

# === Create the parser for command line arguments =====================
import argparse

parser = argparse.ArgumentParser(description="Help testing my code.")

# The first is a positional one, where to run the tests. By default is here
parser.add_argument(
    "machine", type=str, default="here", help="Which machine to run the tests."
)
# The second one is which build to test, using -b or --build. By default is "debug.e"
parser.add_argument(
    "-b",
    "--build",
    type=str,
    default="debug.e",
    help="Which build to test, default is debug.e",
)
# The thirs is which instance set to test, using -i or --instance. By default is "easy". Can be "easy" or "all".
parser.add_argument(
    "-i",
    "--instance",
    type=str,
    default="easy",
    help="Which instance set to test, default is easy",
)
# Wheter to keep or not the individual logs. By default, we don't keep it.
parser.add_argument(
    "-k",
    "--keep",
    action="store_true",
    default=False,
    help="Keep the individual logs under tmp, default is to remove it.",
)


def ssh(cmd):
    os.system(f"source {macos_path}/script/src/functions.sh && {cmd}")


if __name__ == "__main__":
    # Parse the arguments
    args = parser.parse_args()

    if args.machine == "spock":
        print("Running on spock")
        os.system(f"source {macos_path}/script/src/functions.sh")
        path = "/home/ieremies"

    print(f"Running {args.build} on {args.instance} instances on {args.machine}:{path}")

    code_path = f"{path}/code"
    logs_path = f"{path}/logs"
    script_path = f"{path}/script"

    cmds = []

    if args.machine == "spock":
        cmds.append("source ~/.zshrc")
        # send the files
        ssh(f"vulcan {macos_path}/code")

    cmds.append(f"cmake -B {code_path}/build -S {code_path}")
    cmds.append(f"cmake --build {code_path}/build -- -j --silent -k {args.build}")
    if args.instance == "all":
        tl = 3600
    else:
        tl = 150

    cmds.append(
        f'python3 {script_path}/src/runner.py "{code_path}/build/{args.build} [from_file:{script_path}/{args.instance}]" -i {code_path}/inst/all -l {logs_path}/tmp -tl {tl}'
    )
    cmds.append(
        f"python3 {script_path}/src/parser.py {logs_path}/tmp {logs_path}/tmp.yaml"
    )

    if not args.keep is None:
        print("Do not removing individual files!")
    else:
        cmds.append(f"rm -rf {logs_path}/tmp")

    if args.machine == "spock":
        ssh(f"spock '{ '; '.join(cmds) }'")
        ssh(f"beam {logs_path}/tmp.yaml")
    else:
        os.system(f"{ '; '.join(cmds) }")
