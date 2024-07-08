#!/usr/bin/env python3
import subprocess


def grep(pattern, path):
    try:
        result = subprocess.run(
            ["grep", "-r", pattern, path], capture_output=True, text=True, check=True
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as _:
        return []


def parse(log_file, inst_name):
    d = {"instance": inst_name, "lb": -1.0, "ub": -1.0, "time": -1.0}

    # Error handling
    fatal_or_error = grep("FATL|ERR", log_file)
    if fatal_or_error:
        inst = log_file.split("/")[-1].split("_")[0]
        for line in fatal_or_error:
            print(f"❌ {inst}: {line.split(' | ')[-1]}")
        return d

    # Get time
    time = grep("atexit", log_file)
    if time:
        d["time"] = float(time[0].split("s)")[0][1:])

    # Try to recover LB and UB
    final = grep("Coloring: SOL", log_file)
    if final:
        d["lb"] = float(final[0].split("SOL")[-1].split()[0])
        d["ub"] = d["lb"]
    elif grep("has 1 component", log_file):
        root = grep("Root with value ", log_file)
        if root:
            d["lb"] = float(root[0].split()[-1])

        dsatur = grep("DSATUR: ", log_file)
        if dsatur:
            d["ub"] = float(dsatur[0].split()[-1])

        upper = grep("New upper bound", log_file)
        if upper:
            d["ub"] = float(upper[0].split()[-1])
    # TODO more than one component:
    # - add to main: LOG_F(INFO, "Lower bound %d", asn->get_lb()); and get the last one
    #    - this is a shitty way to do
    # - run dsatur for the hole graph and get the first one

    # TODO warnings

    return d
