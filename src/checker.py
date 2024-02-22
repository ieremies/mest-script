#!/usr/bin/env python3
import os
from itertools import combinations

instance_path = "/Users/ieremies/mest/code/inst/"


class Checker:

    def _find_instance_file(self, instance_name: str) -> str:
        # Find a file with the same name as the instance
        # under the instance_path directory or any subdirectory
        for root, _, files in os.walk(instance_path):
            for file in files:
                if file == instance_name:
                    return os.path.join(root, file)
        raise FileNotFoundError(f"File {instance_name} not found")

    def _load_instance(self, instance_file: str) -> list[list[bool]]:
        with open(instance_file, "r") as file:
            lines = file.readlines()
            n = 0
            for l in lines:
                if l.startswith("p"):
                    n = int(l.split()[2])
                    break
            adj = [[False for _ in range(n)] for _ in range(n)]
            for l in lines:
                if l.startswith("e"):
                    u, v = l.split()[1:3]
                    if instance_file.endswith(".col"):
                        u, v = int(u) - 1, int(v) - 1
                    else:
                        u, v = int(u), int(v)
                    adj[u][v] = adj[v][u] = True

        return adj

    def _load_solution(self, sol: str) -> list[set[int]]:
        res = []
        for c in sol.split("} {"):
            c = c.replace("{", "").replace("}", "").replace(",", "")
            res.append(set(map(int, c.split())))
        return res

    def _confirm_coverage(self, adj: list[list[bool]], solution: list[set[int]]):
        covered = [False for _ in range(len(adj))]
        for subset in solution:
            # For each combination of vertices in the subset
            for u, v in combinations(subset, 2):
                # If the edge is not in the graph, print an error
                if adj[u][v]:
                    print(f"!!! Error: ({u}, {v}) in graph")
                # If the edge is in the graph, mark the vertices as covered
                covered[u] = True
                covered[v] = True
            if len(subset) == 1:
                covered[subset.pop()] = True
        # If there is any vertex that is not covered, print an error
        for i, c in enumerate(covered):
            if not c:
                print(f"!!! Error: vertex {i} not covered")

    def check(self, sol: str, instance_name: str):
        instance_file = self._find_instance_file(instance_name)
        adj = self._load_instance(instance_file)
        solution = self._load_solution(sol)
        self._confirm_coverage(adj, solution)


if __name__ == "__main__":
    c = Checker()
    c.check(
        "{28, 78} {53, 107} {76, 109} {2, 26} {62, 85, 108} {38, 41, 94, 111} {55, 73, 80} {49, 60, 79} {14, 21, 89, 105} {8, 59, 104} {20, 113} {35, 48, 116} {58, 127} {0, 10, 81} {7, 47} {3, 42} {17, 77} {25, 101, 117} {39, 124} {4, 61} {67, 103} {72, 123} {75, 84} {16, 87} {90} {91} {99} {18} {27, 36} {100} {46, 51} {86, 98} {34, 63} {66, 120} {33, 54} {56} {65} {50, 69} {121} {52, 97} {106} {122} {6, 118} {22, 96} {114, 119} {31, 125} {30, 93} {57, 102} {32, 126} {15, 74} {44, 71} {64, 70} {11, 68} {13, 43} {82} {1} {9} {92} {112} {19} {95} {5} {88} {12} {83} {110} {23} {29} {40} {24} {45} {115} {37}",
        "miles1500.col",
    )