#!/usr/bin/env python3
"""
Script to generate the Performance Profile.
"""
# TODO PP do gap
# TODO histograma da variação do tempo entre dois dados
# https://github.com/garrettj403/SciencePlots

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import scienceplots


from utils.read_write import read_csv
from utils.utils import get_instances_from_set
import conf

if os.uname().sysname == "Darwin":
    inst_dir = conf.macos_instances
else:
    inst_dir = conf.linux_instances

# === Argument parsing ========================================================
parser = argparse.ArgumentParser(description="Performance Profile")
parser.add_argument(
    "files", metavar="files", type=str, nargs="+", help="Files to compare"
)
parser.add_argument(
    "-i",
    "--instance_set",
    type=str,
    default="all",
    help="Instance set to filter the results. Default is all.",
)
# =============================================================================


# === Functions ===============================================================
def filter_instance_set(results, instances) -> list:
    """
    Filter the results to only have the instances in the set.
    """
    inst = instances.copy()
    ret = []
    for r in results:
        if r["instance"] in inst:
            ret.append(r)
            inst.remove(r["instance"])
    return ret


def get_solved_times(results) -> list[float]:
    """
    Filter the results to only have the solved instances.
    """

    return [
        float(r["time"])
        for r in results
        if r["lb"] == r["ub"]
        and r["lb"] != ""
        and float(r["lb"]) > 0.0
        and r["time"] != ""
    ]


def get_gaps(results) -> list[float]:
    """
    Filter the results to only have the solved instances.
    """

    return [
        (
            float(r["ub"]) / float(r["lb"])
            if r["lb"] != ""
            and r["ub"] != ""
            and float(r["lb"]) > 0.0
            and float(r["ub"]) > 0.0
            else np.inf
        )
        for r in results
    ]


def get_intersection_of_instances(results):
    """
    Get the intersection of instances in all files.
    """
    all_inst = [[i["instance"] for i in results[r]] for r in results]

    inst = set(all_inst[0])
    for i in all_inst[1:]:
        inst = inst.intersection(i)

    return list(inst)


def plot_cumulative(data, axis, n_instances, label=None):
    """
    Plot the cumulative probability of the data.
    """
    data = np.array(data)
    data.sort()
    y = np.arange(len(data)) / n_instances
    axis.plot(data, y, label=label)

    # add a horizontal doted line with the same color as the last plot
    # where the series end.
    if y[-1] < 0.95:
        axis.axhline(y[-1], color=axis.get_lines()[-1].get_color(), linestyle="--")


# =============================================================================


def my_float(s: str):
    try:
        return float(s)
    except:
        return -1


if __name__ == "__main__":
    args = parser.parse_args()

    inst = get_instances_from_set(inst_dir, args.instance_set)
    n_inst = len(inst)

    results = {}  # {file: {instance: str, time: float, lb: float, ub: float}}
    max_time = 0.0
    for f in args.files:
        print(f"Reading file {f}...")
        r = read_csv(f)
        print(f"\tRead {len(r)} instances.")

        r = filter_instance_set(r, inst)
        print(f"\tFiltered to {len(r)} instances in {args.instance_set}.")

        file_name = f.split("/")[-1].replace(".csv", "")
        results[file_name] = r

        tl = max([my_float(i["time"]) for i in r])
        print(f"\tTime limit for {file_name} seems to have been {tl:.2f}")
        max_time = max(max_time, tl)

        print()

    print("Now getting the intersection of instances in all files.")
    inst = get_intersection_of_instances(results)
    print(f"\tFound {len(inst)} common instances in files.\n")

    print("Filtering to common instances...")
    results = {r: filter_instance_set(results[r], inst) for r in results}
    n_inst = len(inst)

    # ========================================================================
    fig, ax1 = plt.subplots(figsize=(16, 9))
    # plt.style.use("science")
    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)

    # === Axis 1 - Time =====================================================
    ax1.set_xscale("log")
    ax1.set_xlabel("Time (s)")
    ax1.set_xlim(0.001, max_time)

    # Plotting solved instances
    solved = {r: get_solved_times(results[r]) for r in results}
    for r in solved:
        print(f"File {r} has {len(solved[r])} solved in {sum(solved[r]):.2f}s.")
        plot_cumulative(solved[r], axis=ax1, label=f"File {r}", n_instances=n_inst)

    # === Axis 2 - Gap ======================================================
    ax2 = ax1.twiny()
    ax2.set_xscale("log")
    ax2.set_xlabel("Gap")
    ax2.set_xlim(1.0, 101.0)

    # Plotting gap
    gaps = {r: get_gaps(results[r]) for r in results}
    for r in gaps:
        plot_cumulative(gaps[r], axis=ax2, n_instances=n_inst)

    # === Legend =================================================
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    # set legend position to bottom right
    ax1.legend(loc="lower right")
    plt.show()
