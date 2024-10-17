#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys

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

# For each instance, we need to compute v1 and v2, such that:
# - v1 = 0.559 * density + 0.614 * algebraic_connectivity + 0.557 * energy
# - v2 = -0.702 * density + -0.007 * algebraic_connectivity + 0.712 * energy
# - v1 and v2 are the x and y coordinates of the scatter plot
m["v1"] = (
    0.559 * m["density"] + 0.614 * m["algebraic_connectivity"] + 0.557 * m["energy"]
)
m["v2"] = (
    -0.702 * m["density"] + -0.007 * m["algebraic_connectivity"] + 0.712 * m["energy"]
)
print(m)

# Step 5: Plot the graph
plt.figure(figsize=(10, 6))

# Scatter plot where color represents the CSV with the lowest time
scatter = plt.scatter(
    m["algebraic_connectivity"],
    m["energy"],
    c=m["source"].astype("category").cat.codes,
    cmap="viridis",
    s=25,
)

# Make the legend each file/color
plt.legend(
    handles=scatter.legend_elements()[0],
    labels=csv_files,
    title="CSV Files",
    loc="upper left",
)

# make axis logarithmic
plt.xscale("log")
plt.yscale("log")
plt.show()
