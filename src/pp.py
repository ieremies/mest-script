#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import json


def get_times(data):
    times = []
    for k in data:
        times.append(data[k]["run_time"])
    return times


def plot_cumulative_times(times):
    times = np.array(times)
    times.sort()
    y = np.arange(len(times)) / len(times)
    # x axis in log scale
    plt.xscale("log")
    plt.xlabel("Time (s)")
    plt.xlim(0.001, 3555)

    plt.ylabel("Cumulative probability")
    plt.ylim(0.0, 1.0)
    # plot the grid
    plt.grid(True)
    plt.plot(times, y)
    plt.show()


if __name__ == "__main__":
    # First argv[1] if the name of the json
    with open(sys.argv[1], "r") as file:
        data = json.load(file)
        times = get_times(data)
        plot_cumulative_times(times)
    pass
