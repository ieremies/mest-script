#!/usr/bin/env python3
"""
Script to generate a Performance Profile.
"""
import numpy as np
import matplotlib.pyplot as plt
import argparse

from utils.read_write import read_csv

# TODO fazer o PP do gap
# TODO fazer o histograma da variação do tempo e do gap entre os resultados da mesma instância
# TODO fazer um filtro para as instâncias de um conjunto de instâncias


def get_solved_instances(file):
    results = read_csv(file)
    total = len(results)
    solved = {
        r["instance"]: {"time": r["time"], "value": r["lb"]}
        for r in results
        if r["lb"] == r["ub"] and r["lb"] != "" and float(r["lb"]) > 0.0
    }
    return solved, total


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
    args = parser.parse_args()

    times = []
    max_time = 0.0
    n_instances = 0
    for f in args.files:
        solved, total = get_solved_instances(f)
        n_instances = max(n_instances, total)

        times.append([float(v["time"]) for _, v in solved.items()])
        max_time = max(max_time, max(times[-1]))
        print(
            f"File {f.split('/')[-1]} has {len(solved)} solved in {sum(times[-1]):.2f}s."
        )

    plt.figure(figsize=(16, 9))
    plt.xscale("log")
    plt.xlabel("Time (s)")
    plt.xlim(0.001, max_time)

    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)
    plt.grid(True)

    for t in times:
        plot_cumulative_times(
            t,
            label=f"File {args.files[times.index(t)].split('/')[-1]}",
            n_instances=n_instances,
        )

    plt.legend()
    plt.show()
