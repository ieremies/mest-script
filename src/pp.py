#!/usr/bin/env python3.12
"""
Script to generate the Performance Profile.
"""
# TODO PP do gap
# TODO histograma da variação do tempo entre dois dados
# https://github.com/garrettj403/SciencePlots

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import scienceplots
import seaborn as sns

plt.style.use("science")
plt.style.use("~/mest/script/src/dis.mplstyle")

import conf
from utils.utils import get_instances_from_set

# Determine instance directory based on OS
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
args = parser.parse_args()


# Function to load instances from files
def load_and_filter_results(file_path, instances):
    df = pd.read_csv(file_path)
    df = df[df["instance"].isin(instances)]
    return df


# Function to get solved times from results
def get_solved_times(df):
    # for each line, return time if lb == ub and lb > 0
    # otherwise, return NaN
    return df.apply(
        lambda x: (
            min(x["time"], 3600) if x["lb"] == x["ub"] and x["lb"] > 0 else 4000
        ),
        axis=1,
    )


def get_gap(df):
    # if df["lb"].astype(float) > 0: gap = (ub - lb) / lb
    # else: gap = ub / 2
    # set as float64
    return df.apply(
        lambda x: (
            (x["ub"] - x["lb"]) / x["lb"]
            if x["lb"] != "" and x["ub"] != "" and x["lb"] > 0
            else x["ub"] / 2 if x["ub"] != "" else 200
        ),
        axis=1,
    )


# Get intersection of instances across all files
def get_common_instances(results):
    instance_sets = [set(df["instance"]) for df in results.values()]
    return set.intersection(*instance_sets)


# Plot cumulative distribution using pandas
def plot_cumulative(data, axis, n_instances, label=None, max=None, min=None):
    # sns.ecdfplot(data, ax=axis, label=label)
    data = np.sort(data)
    # if max:
    #     data = np.insert(data, len(data), max)
    #     n_instances += 1
    # if min:
    #     data = np.insert(data, 0, min)
    #     n_instances += 1
    y = np.arange(len(data)) / n_instances
    axis.plot(data, y, label=label, drawstyle="steps-post")


if __name__ == "__main__":
    # Load instance set based on configuration
    inst = get_instances_from_set(inst_dir, args.instance_set)
    n_inst = len(inst)

    results = {}  # Store results as {filename: DataFrame}
    max_time = 0.0

    # Process each file
    for f in args.files:
        file_name = os.path.splitext(os.path.basename(f))[0]
        print(f"{f.split("/")[-1].replace(".csv", ""):^25}...", end=" ")

        # Load and filter data
        df = load_and_filter_results(f, inst)
        # filter to those that have ub > 3
        results[file_name] = df

        # Calculate maximum time
        tl = df["time"].apply(pd.to_numeric, errors="coerce").max()
        print(f"TL ~{tl:4.0f} | {len(df)} instances")
        max_time = max(max_time, tl)

    # Get common instances across all files
    # inst = get_common_instances(results)
    # n_inst = len(inst)
    # results = {name: df[df["instance"].isin(inst)] for name, df in results.items()}

    # print("Common instances:", n_inst)

    fig, axs = plt.subplots(1, 2, gridspec_kw={"width_ratios": [7, 4]})
    # Set size as width 16cm and height 9cm
    fig.set_size_inches(6.3, 3.54)

    # === Plotting time x cumulative probability ===============================
    axs[0].set_ylim(0.0, 1.0)

    axs[0].grid(axis="y", linestyle="--", alpha=0.7)
    axs[0].spines["right"].set_visible(False)

    axs[0].set_xscale("log")
    axs[0].set_xlabel("Time (s)")
    axs[0].set_xlim(0.001, 3600)  # or max_time
    axs[0].grid(axis="x", linestyle="--", alpha=0.7)

    # Plot solved instances cumulative distribution
    for name, df in results.items():
        time = get_solved_times(df)
        print(len(time[time <= 3600]), len(time))
        print(f"File {name} has {len(time[time < 3600])} instances with time < 3600.")
        print(f"{name:^25}... {len(time)} solved in {time.sum():.2f}s.")
        plot_cumulative(time, axis=axs[0], label=name, n_instances=n_inst, max=3600)

    # === Plotting gap x cumulative probability ================================
    axs[1].set_ylim(0.0, 1.0)

    axs[1].grid(axis="y", linestyle="--", alpha=0.7)
    # axs[1].yaxis.set_visible(False)
    axs[1].tick_params(axis="y", which="both", left=False, right=True, labelsize=False)

    axs[1].spines["left"].set_visible(False)

    axs[1].set_xscale("log")
    axs[1].set_xlabel("Gap")
    gap_xlim_min = 0.004
    gap_xlim_max = 200
    axs[1].set_xlim(gap_xlim_min, gap_xlim_max)
    axs[1].grid(axis="x", linestyle="--", alpha=0.7)

    # Plot solved instances cumulative distribution
    for name, df in results.items():
        # print quantity of gap < 0.0036
        gap = get_gap(df)
        print(len(gap[gap <= 0.0036]), len(gap))
        # if exists a 0 < gap < 0.0036:
        if len(gap[(0 < gap) & (gap < gap_xlim_min)]) > 0:
            print(
                f"File {name} has {len(gap[gap < 0.0036])} instances with gap < {gap_xlim_min}."
            )
        if len(gap[gap > gap_xlim_max]) > 0:
            print(
                f"File {name} has {len(gap[gap > 10.0])} instances with gap > {gap_xlim_max}."
            )
            print(max(gap))
        if "held" in name:
            name = "Held et al."
        else:
            name = "Ours"
        plot_cumulative(
            gap, axis=axs[1], label=name, n_instances=n_inst, min=gap_xlim_min
        )

    axs[1].legend(loc="lower right")
    plt.subplots_adjust(wspace=0)
    # plt.show()

    plt.savefig(f"/Users/ieremies/mest/write/dis/img/accu-{args.instance_set}.svg")
    print(f"Saved to /Users/ieremies/mest/write/dis/img/accu-{args.instance_set}.svg.")
