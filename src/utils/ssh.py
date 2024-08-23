#!/usr/bin/env python3
import conf
import subprocess


def ssh(cmd, supp=conf.debug):
    cmd = f"source {conf.macos_script}/src/functions.sh && {cmd}"
    if conf.debug:
        print(cmd, supp)
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
        # redirect the cmd stdout to this stdout
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print("❌")
        # print encoded output
        print(e.output.decode("utf-8"))
        exit(1)


def command(machine, cmd, supp=conf.debug):
    if machine == "mac":
        ssh(cmd, supp=supp)
        return
    ssh(f"{machine} '{cmd}'", supp=supp)


def beam_to(machine, cmd, supp=conf.debug):
    if machine == "mac":
        return
    cmd.replace("/home/ieremies/", "")
    ssh(f"beam to {machine} '{cmd}'", supp=supp)


def beam_from(machine, cmd, supp=conf.debug):
    if machine == "mac":
        return
    cmd.replace("/home/ieremies/", "")
    print(cmd)
    ssh(f"beam from {machine} '{cmd}'", supp=supp)
