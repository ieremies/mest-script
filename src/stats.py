#!/usr/bin/env python3

import networkx as nx
import numpy as np
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from utils.utils import get_instances_from_set


def read_dimacs(filename: str) -> nx.Graph:
    try:
        G = nx.Graph()
        with open(filename) as f:
            for line in f:
                if line.startswith("e"):
                    _, u, v = line.split()
                    G.add_edge(int(u), int(v))
        return G
    except Exception as _:
        # Return empty graph if there is an error
        return nx.Graph()


def get_algebraic_connectivity(G: nx.Graph) -> float:
    return nx.algebraic_connectivity(G)


def get_energy(G: nx.Graph) -> float:
    return np.sum(np.abs(nx.adjacency_spectrum(G)))


def print_stats(inst_name: str, G: nx.Graph):
    try:
        print(
            f"{inst_name}, {nx.density(G):.6f}, {get_algebraic_connectivity(G):.6f}, {get_energy(G)/100:.6f}"
        )
    except Exception as _:
        pass


if __name__ == "__main__":
    inst_dir = (
        "/Users/ieremies/mest/inst/"
        if os.uname().sysname == "Darwin"
        else "/home/ieremies/inst/"
    )
    insts = get_instances_from_set(inst_dir, "dimacs")

    graphs = [
        (inst_name, read_dimacs(inst_dir + "all/" + inst_name)) for inst_name in insts
    ]

    graphs.sort(key=lambda x: len(x[1]))

    print(os.cpu_count())
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex:
        f2e = {ex.submit(print_stats, *i): i for i in graphs}

        # tqdm progress bar
        for _ in tqdm(as_completed(f2e), total=len(f2e)):
            pass
