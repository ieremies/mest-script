#!/usr/bin/env python3
"""
Read a DIMACS instance and plot the graph
"""
import os
import networkx as nx
import matplotlib.pyplot as plt
import sys


def read_dimacs(file: str):
    """
    Read the instance from a file in the DIMACS format.

    :param file: path to the file containing the instance
    """
    G = nx.Graph()
    with open(file, "r") as f:
        for line in f.readlines():
            if line[0] == "c":
                continue
            if line[0] == "p":
                _, _, n, m = line.split()
                min = 1 if ".col" in file else 0
                for i in range(min, int(n)):
                    G.add_node(i)
            if line[0] == "e":
                _, u, v = line.split()
                G.add_edge(int(u), int(v))
    return G


def draw_graph(G):
    """
    Draw the graph.

    :param G: the graph
    """
    pos = nx.nx_pydot.pydot_layout(G)
    nx.draw(G, pos, with_labels=True)
    plt.show()


if __name__ == "__main__":
    # First argv[1] if the name of the instance
    G = read_dimacs(sys.argv[1])
    draw_graph(G)
    pass
