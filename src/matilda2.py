#!/usr/bin/env python3.12

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import scienceplots
import seaborn as sns

# plt.style.use("ggplot")
plt.style.use("science")
plt.style.use("~/mest/script/src/dis.mplstyle")

# Step 1: Load the metadata CSV and other CSVs
metadata = pd.read_csv("/Users/ieremies/mest/inst/metadata.csv")
metadata = metadata[["instance", "density", "algebraic_connectivity", "energy"]]

# Assuming you have a list of CSV file names
if len(sys.argv) > 3:
    exit("Too many arguments. Please provide at most two CSVs.")
csv_files = sys.argv[1:]

# Read the csvs
df1 = pd.read_csv(csv_files[0])
df2 = pd.read_csv(csv_files[1])

# Filter for solved matilda instances
df1 = df1[
    (df1["lb"] == df1["ub"]) & (df1["lb"] > 0) & (df1["instance"].str.startswith("g"))
]
df2 = df2[
    (df2["lb"] == df2["ub"]) & (df2["lb"] > 0) & (df2["instance"].str.startswith("g"))
]

# Reduce to only the columns we need
df1 = df1[["instance", "time"]]
df2 = df2[["instance", "time"]]

# Merge all dataframes with metadata
df = pd.merge(df1, metadata, on="instance", suffixes=("_1", ""), how="outer")
df = pd.merge(df2, df, on="instance", suffixes=("_2", "_1"), how="outer")

df["v1"] = (
    0.559 * df["density"] + 0.614 * df["algebraic_connectivity"] + 0.557 * df["energy"]
)
df["v2"] = (
    -0.702 * df["density"] - 0.007 * df["algebraic_connectivity"] + 0.712 * df["energy"]
)

# none_solved = df[(df["time_1"].isnull()) & (df["time_2"].isnull())]
# print(none_solved)
# only_1_solved = df[(df["time_1"].notnull()) & (df["time_2"].isnull())]
# print(only_1_solved)
# exit(1)

# Filter to only instances both algorithms solved
df = df[(df["time_1"] != 0) & (df["time_2"] != 0)]

# Diff is the relative difference between the times of the two algorithms
# diff := (time_2 - time_1) / min(time_1, time_2)
# diff < 0: algorithm 1 is faster
# diff > 0: algorithm 2 is faster
# diff = -inf: algorithm 1 solved the instance and algorithm 2 did not
# diff = +inf: algorithm 2 solved the instance and algorithm 1 did not
for i, row in df.iterrows():
    if row["time_1"] is None and row["time_2"] is None:
        df.at[i, "diff"] = None
    elif row["time_1"] is None:
        df.at[i, "diff"] = np.inf
    elif row["time_2"] is None:
        df.at[i, "diff"] = -np.inf
    else:
        df.at[i, "diff"] = (row["time_1"] - row["time_2"]) / min(
            row["time_1"], row["time_2"]
        )

range = max(abs(df["diff"].quantile(0.05)), abs(df["diff"].quantile(0.95)))
df["diff"] = df["diff"].clip(-range, range)
df = df[abs(df["diff"]) > 5]
print(df)

# df = df.sort_values("diff", key=abs)  # sort by absolute value of diff
df = df.sample(frac=1).reset_index(drop=True)  # random

fig, axs = plt.subplots(2, 2)
scatter = axs[0, 0].scatter(df["v1"], df["v2"], c=df["diff"], cmap="coolwarm", s=15)
axs[0, 0].set_xlabel("v1")
axs[0, 0].set_ylabel("v2")

scatter = axs[0, 1].scatter(
    df["density"], df["energy"], c=df["diff"], cmap="coolwarm", s=15
)
axs[0, 1].set_xlabel("Density")
axs[0, 1].set_ylabel("Energy")

scatter = axs[1, 0].scatter(
    df["energy"],
    df["algebraic_connectivity"],
    c=df["diff"],
    cmap="coolwarm",
    s=15,
)
axs[1, 0].set_xlabel("Energy")
axs[1, 0].set_ylabel("Algebraic Connectivity")

scatter = axs[1, 1].scatter(
    df["algebraic_connectivity"],
    df["density"],
    c=df["diff"],
    cmap="coolwarm",
    s=15,
)
axs[1, 1].set_xlabel("Algebraic Connectivity")
axs[1, 1].set_ylabel("Density")

# Place one colorbar on the bottom of the plot
mark = (range // 10) * 10
ticks = [-mark, -mark // 2, 0, mark // 2, mark]
labels = [f"{abs(t):.0f}" for t in ticks]
labels[0] += f"\n{sys.argv[1].split('/')[-1].replace('.csv', '')} is faster"
labels[-1] += f"\n{sys.argv[2].split('/')[-1].replace('.csv', '')} is faster"

cbar = fig.colorbar(
    scatter,
    ax=axs,
    orientation="horizontal",
    pad=0.08,
    fraction=0.05,
)
cbar.set_ticks(ticks=ticks, labels=labels)


plt.savefig("/Users/ieremies/mest/write/dis/img/matilda-perf.svg")
