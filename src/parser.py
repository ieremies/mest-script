#!/usr/bin/env python3
"""
Parse the results of an experiment
"""
import os
import sys
import yaml
from math import ceil, floor

import checker
import comparer


hist_yaml = "/Users/ieremies/mest/logs/hist.yaml"
if not os.path.exists(hist_yaml):
    hist_yaml = "/home/ieremies/logs/hist.yaml"


class Parser:
    data = {}
    checker = checker.Checker()

    def __init__(self):
        self.parsers = [
            getattr(self, method) for method in dir(self) if method.startswith("_get_")
        ]

    def _get_run_time(self, instance_name: str, line: str):
        """
        Get the time from lines in the form of
        (   0.020s)              loguru.cpp:560   INFO| atexit
        """
        if "s)" not in line:
            return
        time = line.split("s)")[0].split("(")[-1]
        self.data[instance_name]["run_time"] = float(time)

    def _get_solution(self, instance_name: str, line: str):
        """
        Get solution from lines in the form of
        (   0.019s)                main.cpp:83    INFO| Coloring: SOL (3.000000) =  {0, 2} {1, 3} {4}
        """
        if "Coloring: SOL " not in line:
            return
        solution = line.split("SOL ")[1].split(" = ")[0]
        self.data[instance_name]["upper_bound"] = floor(float(solution))
        self.data[instance_name]["lower_bound"] = floor(float(solution))
        # check if the solution is correct
        self.checker.check(line.split(" = ")[-1], instance_name)

    def _get_n_branchs(self, instance_name: str, line: str):
        if "{ next " not in line:
            return
        if "n_branchs" not in self.data[instance_name]:
            self.data[instance_name]["n_branchs"] = 0
        self.data[instance_name]["n_branchs"] += 1

    def _get_n_pricing(self, instance_name: str, line: str):
        if "{ Pricing." not in line:
            return
        if "n_pricing" not in self.data[instance_name]:
            self.data[instance_name]["n_pricing"] = 0
        self.data[instance_name]["n_pricing"] += 1

    def _get_n_pricing_1_set(self, instance_name: str, line: str):
        if "Added 1 sets" not in line:
            return
        if "n_pricing_1_set" not in self.data[instance_name]:
            self.data[instance_name]["n_pricing_1_set"] = 0
        self.data[instance_name]["n_pricing_1_set"] += 1

    def _get_dsatur_time(self, instance_name: str, line: str):
        """
        Get the running time of the dsatur algorithm
        (   0.003s)           heuristic.cpp:9     INFO| } 0.000 s: dsatur
        """
        if "s: dsatur" not in line:
            return
        if "dsatur_time" in self.data[instance_name]:
            self.data[instance_name]["dsatur_time"] += float(
                line.split("} ")[1].split(" s:")[0]
            )
        else:
            self.data[instance_name]["dsatur_time"] = float(
                line.split("} ")[1].split(" s:")[0]
            )

    def _get_dsatur_value(self, instance_name: str, line: str):
        """
        Get the value of the dsatur algorithm
        (   0.003s)              dsatur.cpp:66    INFO| .   DSATUR: 4 colors
        """
        if "DSATUR: " not in line or "dsatur_value" in self.data[instance_name]:
            return
        self.data[instance_name]["dsatur_value"] = int(
            line.split("DSATUR: ")[1].split()[0]
        )

    def _get_n_components(self, instance_name: str, line: str):
        """
        Get the number of components of the original instance
        (   0.003s)                main.cpp:78    INFO| Graph has 1 component
        """
        if not "component" in line:
            return
        try:
            type, _, n, _ = line.split(" INFO| ")[1].split()
            self.data[instance_name]["n_components"] = int(n)
            self.data[instance_name]["type_components"] = type
        except:
            ...

    def remove_numbers(self, s):
        return s.translate(str.maketrans("", "", "0123456789"))

    def parse(self, file: str):
        """
        For each line, calls all the _get_ methods
        """
        with open(file, "r") as f:
            lines = f.readlines()

        instance_name = file.split(".e_")[-1].replace(".log", "")
        self.data[instance_name] = {}
        warnings = {}

        for l in lines:
            if "FATL" in l:
                print(f"❌ {instance_name} {l.split('FATL')[1].strip()}")
                continue
            if "WARN" in l:
                error = l.split("WARN")[1].strip().replace(" . ", "")
                error = self.remove_numbers(error)
                if error not in warnings:
                    warnings[error] = 1
                else:
                    warnings[error] += 1

            for p in self.parsers:
                p(instance_name, l)

        if len(lines) < 4:
            print(f"❌ {instance_name} not enough lines")
        else:
            self._get_run_time(instance_name, lines[-3])

        for w in warnings:
            print(f"⚠️ {instance_name} ", f"{w} x{warnings[w]}")

    def write(self, file: str) -> str:
        """
        Writes the data to a yaml file
        """
        # For every intance name, remove the .gph or the .col
        new_data = {}
        for instance_name in self.data:
            new_data[instance_name.replace(".col", "").replace(".gph", "")] = self.data[
                instance_name
            ]
        # If the file does not end in .yaml, add it
        if not file.endswith(".yaml"):
            file += ".yaml"

        # Write the data to the file
        with open(file, "w") as f:
            yaml.dump(new_data, f)

        print(f"✅ Data written to {file}")
        return file


def run_for_all(file: str):
    p = Parser()
    for f in os.listdir(file):
        f = os.path.join(file, f)
        p.parse(f)
    return p.write(file), p


if __name__ == "__main__":
    yaml_file, p = run_for_all(sys.argv[1])
    print(f"✅ Done parsing {len(p.data.keys())} instances.")
    print(f"🤔 Comparing to {hist_yaml}")
    c = comparer.Comparer(hist_yaml, yaml_file)
