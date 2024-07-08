#!/usr/bin/env python3
"""
Script to generate a Performance Profile.
"""
import numpy as np
import matplotlib.pyplot as plt
import argparse

from utils.io import read_csv


def get_solved_instances(file):
    results = read_csv(file)
    solved = {
        r["instance"]: {"time": r["time"], "value": r["lb"]}
        for r in results
        if r["lb"] == r["ub"] and float(r["lb"]) > 0.0
    }
    return solved


def plot_cumulative_times(times, label, n_instances):
    times = np.array(times)
    times.sort()
    y = np.arange(len(times)) / n_instances
    plt.plot(times, y, label=label)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Performance Profile")
    parser.add_argument(
        "files", metavar="files", type=str, nargs="+", help="Files to compare"
    )
    # if to only use common instances or not
    parser.add_argument(
        "-c",
        "--common",
        action="store_true",
        help="Use only common instances between files.",
    )
    args = parser.parse_args()

    p = []
    for f in args.files:
        solved = get_solved_instances(f)
        print(f"File {f} has {len(solved)} solved instances.")
        p.append(solved)

    times = []
    if args.common:
        common = set(p[0].keys())
        for i in p[1:]:
            common = common.intersection(i.keys())
        print(f"Common instances: {len(common)}")
        for i in p:
            times.append([float(i[instance]["time"]) for instance in common])
    else:
        for i in p:
            times.append([float(v["time"]) for _, v in i.items()])

    # find max time and n_instance
    max_time = 0.0
    n_instances = 0
    for t in times:
        max_time = max(max_time, max(t))
        n_instances = max(n_instances, len(t))

    plt.figure(figsize=(16, 9))
    plt.xscale("log")
    plt.xlabel("Time (s)")
    plt.xlim(0.001, max_time)

    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)
    plt.grid(True)

    for t in times:
        plot_cumulative_times(
            t, label=f"File {args.files[times.index(t)]}", n_instances=n_instances
        )

    plt.legend()
    plt.show()
