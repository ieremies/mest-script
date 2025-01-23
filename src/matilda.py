#!/usr/bin/env python3.12

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pgf import _tex_escape as mpl_common_texification
import seaborn as sns

import sys

plt.style.use("ggplot")

# Step 1: Load the metadata CSV and other CSVs
metadata = pd.read_csv("/Users/ieremies/mest/inst/metadata.csv")
metadata = metadata[["instance", "density", "algebraic_connectivity", "energy"]]

# Assuming you have a list of CSV file names
csv_files = sys.argv[1:]

# Step 2: Load and merge all the CSV files into one dataframe
dataframes = []
for file in csv_files:
    df = pd.read_csv(file)
    df["source"] = file  # Add a column to track the source CSV
    # for each row in the dataframe, if lb != ub and lb > 0, then time = NaN
    df.loc[(df["lb"] != df["ub"]) & (df["lb"] > 0), "time"] = None
    dataframes.append(df)

# Concatenate all dataframes
all_data = pd.concat(dataframes, ignore_index=True)
all_data = all_data[["instance", "time", "source"]]

# Step 4: For each instance, find the CSV with the lowest time
# Sort the merged dataframe by 'time', group by 'instances', and take the first row for each group
best_times = all_data.sort_values(by="time").groupby("instance").first().reset_index()

# Merge the best times with the metadata
m = pd.merge(best_times, metadata, on="instance")
m = m.dropna()

# For each instance, compute v1 and v2
m["v1"] = (
    0.559 * m["density"] + 0.614 * m["algebraic_connectivity"] + 0.557 * m["energy"]
)
m["v2"] = (
    -0.702 * m["density"] + -0.007 * m["algebraic_connectivity"] + 0.712 * m["energy"]
)

# Generate a color map for each unique file
unique_files = m["source"].unique()
colors = plt.cm.get_cmap("tab10", len(unique_files))
color_map = {file: colors(i) for i, file in enumerate(unique_files)}

# Step 5: Create a plot with 4 subplots
fig, axs = plt.subplots(2, 2, figsize=(14, 10))


# Plot function to simplify each scatter plot with color mapping
def plot_scatter(ax, x, y, xlabel, ylabel, title, log=True):
    for file, color in color_map.items():
        subset = m[m["source"] == file]
        ax.scatter(subset[x], subset[y], color=color, label=file, s=10)
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)


# Plot each relationship
plot_scatter(axs[0, 0], "v1", "v2", "v1", "v2", "v1 vs v2")
plot_scatter(
    axs[0, 1],
    "density",
    "algebraic_connectivity",
    "Density",
    "Algebraic Connectivity",
    "Density vs Algebraic Connectivity",
    log=False,
)
plot_scatter(
    axs[1, 0], "density", "energy", "Density", "Energy", "Density vs Energy", log=False
)
plot_scatter(
    axs[1, 1],
    "energy",
    "algebraic_connectivity",
    "Energy",
    "Algebraic Connectivity",
    "Energy vs Algebraic Connectivity",
    log=False,
)

# Add a single legend for all subplots
handles = [
    plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=color, markersize=6)
    for color in color_map.values()
]
labels = list(color_map.keys())
fig.legend(
    handles, labels, loc="upper center", title="CSV Files", ncol=len(unique_files)
)

# Adjust layout and show plot
plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for the legend
plt.show()
