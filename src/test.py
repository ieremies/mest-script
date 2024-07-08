#!/usr/bin/env python3
import subprocess
import conf


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
    send_code()
    compile_code()
    run()
    compile_code("primal.e")
    run("primal.e")
    beam(f"{conf.spock_logs}/tmp.csv")  # only the last run is saved
    print("Done!")
