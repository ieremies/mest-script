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


def spock(cmd, supp=conf.debug):
    ssh(f"spock '{cmd}'", supp=supp)


def beam(cmd, supp=conf.debug):
    ssh(f"beam '{cmd}'", supp=supp)


def vulcan(path, supp=conf.debug):
    ssh(f"vulcan {path}", supp=supp)
