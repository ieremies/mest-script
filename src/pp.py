#!/usr/bin/env python3
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

plt.style.use("science")

import conf
from utils.utils import get_instances_from_set

# Determine instance directory based on OS
if os.uname().sysname == "Darwin":
    inst_dir = conf.macos_instances
else:
    inst_dir = conf.linux_instances

# Argument parsing
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
    return df[
        (df["time"] != "")
        & (df["lb"] != "")
        & (df["lb"].astype(float) > 0)
        & (df["lb"] == df["ub"])
    ]["time"].astype(float)


# Get intersection of instances across all files
def get_common_instances(results):
    instance_sets = [set(df["instance"]) for df in results.values()]
    return set.intersection(*instance_sets)


# Plot cumulative distribution using pandas
def plot_cumulative(data, axis, n_instances, label=None):
    data = np.sort(data)
    y = np.arange(len(data)) / n_instances
    axis.plot(data, y, label=label)


if __name__ == "__main__":
    # Load instance set based on configuration
    inst = get_instances_from_set(inst_dir, args.instance_set)
    n_inst = len(inst)

    results = {}  # Store results as {filename: DataFrame}
    max_time = 0.0

    # Process each file
    for f in args.files:
        file_name = os.path.splitext(os.path.basename(f))[0]
        print(f"Reading {f:^15}...", end=" ")

        # Load and filter data
        df = load_and_filter_results(f, inst)
        results[file_name] = df

        # Calculate maximum time
        tl = df["time"].apply(pd.to_numeric, errors="coerce").max()
        print(f"TL ~{tl:.2f} | {len(df)} instances")
        max_time = max(max_time, tl)

    # Get common instances across all files
    inst = get_common_instances(results)
    n_inst = len(inst)
    results = {name: df[df["instance"].isin(inst)] for name, df in results.items()}

    print("Common instances:", n_inst)

    # Plotting
    fig, ax1 = plt.subplots(figsize=(16, 9))
    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)

    ax1.set_xscale("log")
    ax1.set_xlabel("Time (s)")
    ax1.set_xlim(0.001, max_time)

    # Plot solved instances cumulative distribution
    for name, df in results.items():
        solved_times = get_solved_times(df)
        print(
            f"File {name} has {len(solved_times)} solved instances in {solved_times.sum():.2f}s."
        )
        label = "Held" if "held" in name else "Ours"
        plot_cumulative(solved_times, axis=ax1, label=label, n_instances=n_inst)

    ax1.legend(loc="lower right")
    plt.show()
