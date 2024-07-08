#!/usr/bin/env python3
"""
Script responsible for doing my testing.

Flags:
-k, --keep: do not delete the logs of the last instance set tested.
-p, --primal: only test the primal.e build.
-d, --debug: only test the debug.e build.
"""
import subprocess
import conf
import argparse

parser = argparse.ArgumentParser(description="Help testing my code.")
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


def ssh(cmd, supp=conf.debug):
    cmd = f"source {conf.macos_script}/src/functions.sh && {cmd}"
    if conf.debug:
        print(cmd)
    if supp:
        if (
            subprocess.call(
                cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            != 0
        ):
            print("❌")
            exit()
        return

    try:
        subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("❌")
        # print encoded output
        print(e.output.decode("utf-8"))
        exit(1)


def spock(cmd, supp=conf.debug):
    ssh(f"spock '{cmd}'", supp=supp)


def beam(cmd, supp=conf.debug):
    ssh(f"beam '{cmd}'", supp=supp)


def vulcan(path, supp=conf.debug):
    ssh(f"vulcan {path}", supp=supp)


def send_code():
    print("⏳ Sending code to Spock...")

    vulcan(conf.macos_code)
    spock(
        f"cmake -B {conf.spock_code}/build -S {conf.spock_code}"
    )  # generate build files
    print("\033[F✅")


def compile_code(build=conf.default_build):
    print(f"⏳ Compiling {build} in Spock...")
    spock(f"cmake --build {conf.spock_code}/build -- -j --silent -k {build}")
    print("\033[F✅")


def run(build=conf.default_build, instance=conf.default_instances, keep=False):
    cmd = f"python3 {conf.spock_script}/src/runner.py {build} {instance}"

    if keep:
        cmd += " -k"

    spock(cmd, supp=False)

    print("\033[F✅")


if __name__ == "__main__":
    args = parser.parse_args()

    send_code()

    if not args.primal:
        compile_code("debug.e")
        run("debug.e", keep=args.keep and args.debug)

    if not args.debug:
        compile_code("primal.e")
        run("primal.e", keep=args.keep)

    beam(f"{conf.spock_logs}/tmp.csv")  # only the last run is saved
    print("Done!")
