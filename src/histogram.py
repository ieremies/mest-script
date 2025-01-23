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
sns.set_palette("tab10")

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
df = pd.merge(df1, df2, on="instance", suffixes=("_1", "_2"), how="outer")


df = df[(df["time_1"] != 0) & (df["time_2"] != 0)]

# df = df[(df["time_1"] > 0.1) & (df["time_2"] > 0.1)]

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

df = df.sort_values("diff", key=abs)  # sort by absolute value of diff
# df = df.sample(frac=1).reset_index(drop=True) # random

# === Plotting ================================================================
sns.histplot(df["diff"], bins=40, kde=True)

# add a mark on the mean value
plt.axvline(
    df["diff"].mean(),
    color="k",
    linestyle="--",
    label="Mean = {:.2f}".format(df["diff"].mean()),
)

# add a mark on the median value
plt.axvline(
    df["diff"].median(),
    color="r",
    linestyle="-.",
    label="Median = {:.2f}".format(df["diff"].median()),
)

plt.legend()
# save as svg
plt.savefig("hist.svg")
