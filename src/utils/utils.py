#!/usr/bin/env python3
import os
from random import shuffle


def get_all_files(directory):
    """
    Get a list of all files in a directory, including symbolic links.
    If it is a symbolic link, return the absolute path to where it points.
    """
    all_files = []

    # Walk through the directory
    for root, _, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            if os.path.islink(file_path):
                # If it is a symbolic link, add the absolute target path
                real_path = os.path.realpath(file_path)
                all_files.append(real_path)
            else:
                # If it is a regular file, add the absolute file path
                absolute_path = os.path.abspath(file_path)
                all_files.append(absolute_path)

    return all_files


def get_instances_from_set(inst_dir: str, sets: str) -> list[str]:
    """
    Given a set ("easy") or a combination of sets ("easy+hard"),
    return a list of names of all instances in the set(s).
    """
    all = []
    for inst_set in sets.split("+"):
        inst = get_all_files(f"{inst_dir}/{inst_set}")
        inst = [i.split("/")[-1] for i in inst]
        all.extend(inst)
    shuffle(all)
    return all


def get_n_jobs():
    """
    Get the number of jobs to run in parallel. This is the number of physical
    cores on the machine.

    If the machine is a x86, os.cpu_count() will return the number of logical
    cores, which is not what we want.

    If the machine is a arm64, os.cpu_count() will return the number of physical.
    """
    cores = os.cpu_count()
    if cores is None:
        return

    cores -= 1  # spare one for the OS
    if os.uname().machine == "arm64":
        return cores

    return cores // 2
