#!/usr/bin/env python3.12
#
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import scienceplots
import seaborn as sns

# plt.style.use("ggplot")
plt.style.use("science")
plt.style.use("~/mest/script/src/dis.mplstyle")

# Assuming you have a list of CSV file names
if len(sys.argv) > 3:
    exit("Too many arguments. Please provide at most two CSVs.")
csv_files = sys.argv[1:]

# Read the csvs
df1 = pd.read_csv(csv_files[0])
df2 = pd.read_csv(csv_files[1])

# Filter for solved
df1 = df1[(df1["lb"] == df1["ub"]) & (df1["lb"] > 0)]
df2 = df2[(df2["lb"] == df2["ub"]) & (df2["lb"] > 0)]

# Reduce to only the columns we need
df1 = df1[["instance", "time"]]
df2 = df2[["instance", "time"]]

# Merge all dataframes
df = pd.merge(df1, df2, on="instance", suffixes=("_1", "_2"), how="outer")
df = df[(df["time_1"] != 0) & (df["time_2"] != 0)]

for i, row in df.iterrows():
    if row["time_1"] is None and row["time_2"] is None:
        df.at[i, "diff"] = None
    elif row["time_1"] is None:
        df.at[i, "diff"] = np.inf
    elif row["time_2"] is None:
        df.at[i, "diff"] = -np.inf
    else:
        df.at[i, "diff"] = row["time_2"] / row["time_1"]

range = max(abs(df["diff"].quantile(0.05)), abs(df["diff"].quantile(0.95)))
df = df.sort_values("diff")

# Filter insntaces that start with "g"
matilda = df[df["instance"].str.startswith("g")]
dimacs = df[~df["instance"].str.startswith("g")]

# Use sns to plot the cumulative distribution of "diff", on a log scale
sns.ecdfplot(data=dimacs, x="diff", log_scale=True, label="DIMACS")
sns.ecdfplot(data=matilda, x="diff", log_scale=True, label="MATILDA")
plt.legend(loc="lower right")

plt.xlim(1 / range, range)
plt.xlabel("Performance Ratio")
plt.ylabel("")

plt.grid(True, which="major", ls="--", alpha=0.7)


# plt.show()
plt.savefig("/Users/ieremies/mest/write/dis/img/accu-perf-matilda.svg")
