#!/usr/bin/env python3
"""
For every instance, I have to get:
- Run time
- Lower bound
- Upper bound

TODO For every instance, check against known results.
TODO Check if every instance is present

{
    "instance_name": {
        "run_time": 0.0,
        "lower_bound": 0,
        "upper_bound": 0,
    }
}
"""
import os
import sys
import json
from math import ceil, floor

import checker


class Parser:
    data = {}
    checker = checker.Checker()

    def _get_run_time(self, instance_name: str, line: str):
        """
        Get the time from lines in the form of
        (   0.020s)              loguru.cpp:560   INFO| atexit
        """
        if "s)" in line:
            time = line.split("s)")[0].split("(")[-1]
            self.data[instance_name]["run_time"] = float(time)

    def _get_solution(self, instance_name: str, line: str):
        """
        Get solution from lines in the form of
        (   0.001s)              dsatur.cpp:78    WARN| .   SOL: 4.000000 = {1, 4, 10} {0, 2, 5, 7} {3, 6, 8} {9}
        """
        if "SOL" in line:
            solution = line.split("SOL: ")[1].split(" = ")[0]
            self.data[instance_name]["upper_bound"] = floor(float(solution))
            # check if the solution is correct
            self.checker.check(line.split(" = ")[-1], instance_name)

    def _get_lower_bound(self, instance_name: str, line: str):
        """
        Get lower bound from the first line in the form of
        (   0.017s)                main.cpp:44    INFO| Solved with value 3.000000
        """
        if "Solved with value" in line and self.data[instance_name]["lower_bound"] == 0:
            lower_bound = line.split("Solved with value ")[1]
            self.data[instance_name]["lower_bound"] = ceil(float(lower_bound))

    def parse(self, file: str):
        """
        For each line of the file, calls the corresponding parsing function.

        If it is the last line, calls the _get_run_time function.
        If it has "SOL", calls the _get_solution function.
        If it has "Solved with value", calls the _get_lower_bound function.
        """
        with open(file, "r") as f:
            instance_name = (
                file.split("/")[-1].replace("primal.e_", "").replace(".log", "")
            )
            self.data[instance_name] = {
                "run_time": 0.0,
                "lower_bound": 0,
                "upper_bound": 0,
            }

            lines = f.readlines()
            for l in lines:
                if "FATL" in l:
                    print(f"!!! Error in {file}!!!")
                    continue
                if "SOL" in l:
                    self._get_solution(instance_name, l)
                elif "Solved with value" in l:
                    self._get_lower_bound(instance_name, l)

            self._get_run_time(instance_name, lines[-1])

    def write(self, file: str):
        """
        Writes the data to a json file
        """
        # For every intance name, remove the .gph or the .col
        for instance_name in self.data:
            if instance_name.endswith(".gph"):
                self.data[instance_name.replace(".gph", "")] = self.data.pop(
                    instance_name
                )
            elif instance_name.endswith(".col"):
                self.data[instance_name.replace(".col", "")] = self.data.pop(
                    instance_name
                )
        # If the file does not end in .json, add it
        if not file.endswith(".json"):
            file += ".json"

        # Write the data to the file
        with open(file, "w") as f:
            f.write(json.dumps(self.data, indent=4))


if __name__ == "__main__":
    p = Parser()

    # run parse for every file under argv[1]
    for f in os.listdir(sys.argv[1]):
        # expand path
        f = os.path.join(sys.argv[1], f)
        p.parse(f)

    # wirte the json to the file in argv[2]
    p.write(sys.argv[2])
