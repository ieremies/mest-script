#!/usr/bin/env python3


import pandas as pd
import matplotlib.pyplot as plt
import scienceplots

plt.style.use("science")
import numpy as np
import sys

# If more than 2 args
if len(sys.argv) > 3:
    print("Usage: matilda.py <file1> <file2> ...")
    sys.exit(1)

# Step 1: Load the metadata CSV and other CSVs
data1 = pd.read_csv(sys.argv[1])
data1.loc[(data1["lb"] != data1["ub"]) & (data1["lb"] > 0), "time"] = None
data1 = data1.dropna(subset=["time", "lb", "ub"])
data2 = pd.read_csv(sys.argv[2])
data2.loc[(data2["lb"] != data2["ub"]) & (data2["lb"] > 0), "time"] = None
data2 = data2.dropna(subset=["time", "lb", "ub"])

instances = set(data1["instance"].tolist())
instances.update(data2["instance"].tolist())

histogram = []
qtd_inst_1_closes_but_not_2 = 0
qtd_inst_2_closes_but_not_1 = 0
for i in instances:
    time1 = data1[data1["instance"] == i]["time"].values
    time2 = data2[data2["instance"] == i]["time"].values

    time1 = time1[0] if len(time1) > 0 else 0
    time2 = time2[0] if len(time2) > 0 else 0

    # # check if time1[0] is nan
    if not time1 > 0 and not time2 > 0:
        continue
    if not time1 > 0:
        qtd_inst_2_closes_but_not_1 += 1
    elif not time2 > 0:
        qtd_inst_1_closes_but_not_2 += 1
    elif time1 > time2:
        histogram.append(time1 / time2 - 1)
    else:
        histogram.append(-time2 / time1 + 1)

# remove the smallest 5% and the largest 5%
histogram.sort()
histogram = histogram[int(len(histogram) * 0.05) : int(len(histogram) * 0.95)]

# Step 5: Plot the graph
plt.hist(histogram, bins=100, color="blue", edgecolor="black")
plt.xlabel("Time ratio")
plt.ylabel("Frequency")
plt.title("Time ratio histogram")

# draw a vertical line on the median
plt.axvline(np.median(histogram), color="green", linestyle="dashed", linewidth=1)
# get maximum value on y
max_freq = max(plt.hist(histogram, bins=100, color="blue", edgecolor="black")[0])
# write the median
plt.text(
    np.median(histogram),
    max_freq - 1,
    f"Median: {np.median(histogram):.2f}",
    verticalalignment="bottom",
)

# print
# "qtd_inst_1_closes_but_not_2" instances close in {sys.argv[1]} but not in {sys.argv[2]}
# "qtd_inst_2_closes_but_not_1" instances close in {sys.argv[2]} but not in {sys.argv[1]}
#
# "{sys.argv[1]} is faster in {count the amount of values in histogram that are < 0} instances"
# "{sys.argv[2]} is faster in {count the amount of values in histogram that are > 0} instances"
print(
    f"{qtd_inst_1_closes_but_not_2} instances closed in {sys.argv[1]} but not in {sys.argv[2]}"
)
print(
    f"{qtd_inst_2_closes_but_not_1} instances closed in {sys.argv[2]} but not in {sys.argv[1]}"
)
print(f"{sys.argv[1]} is faster in {len([i for i in histogram if i < 0])} instances")
print(f"{sys.argv[2]} is faster in {len([i for i in histogram if i > 0])} instances")


plt.show()
