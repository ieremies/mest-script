#!/usr/bin/env python3

import os
import sys
import yaml
from math import ceil, floor


class Parser:
    data = {}

    def _get_run_time(self, instance_name: str, line: str):
        """
        Get the time from lines in the form of
        Compute_coloring took 3537.000000 seconds (initial lower bound:1.000000, heur. upper bound: 0.000000, branching real: 3536.000000, branching cpu: 3500.695460).
        """
        if "Computing coloring took" in line:
            time = line.split(" ")[3]
            self.data[instance_name]["run_time"] = float(time)

    def _get_solution(self, instance_name: str, line: str):
        """
        Get solution from lines in the form of
        Compute coloring finished: LB 4 and UB 6
        """
        if "Compute coloring finished" in line:
            solution = line.split("UB ")[1]
            self.data[instance_name]["upper_bound"] = int(solution)
            # get lb
            lb = line.split("LB ")[1].split(" and UB")[0]
            self.data[instance_name]["lower_bound"] = int(lb)

    def parse(self, file: str):
        """
        For each line of the file, calls the corresponding parsing function.

        If it is the last line, calls the _get_run_time function.
        If it has "SOL", calls the _get_solution function.
        If it has "Solved with value", calls the _get_lower_bound function.
        """
        with open(file, "r") as f:
            instance_name = file.split("color_")[-1].replace(".log", "")
            self.data[instance_name] = {
                "run_time": None,
                "lower_bound": 0,
                "upper_bound": 0,
            }

            lines = f.readlines()
            for l in lines:
                if "Compute coloring finished" in l:
                    self._get_solution(instance_name, l)
                elif "Computing coloring took" in l:
                    self._get_run_time(instance_name, l)

            if self.data[instance_name]["run_time"] != None:
                return
            if "Branching" in lines[-1]:
                self.data[instance_name]["run_time"] = 3600
            elif "Academic license" in lines[-1]:
                print(f"⚠️Error: {file} halts at Academic license")
            else:
                print(f"❌Error: {file} does not have a run time")

    def write(self, file: str) -> str:
        """
        Writes the data to a yaml file
        """
        # For every intance name, remove the .gph or the .col
        new_data = {}
        for instance_name in self.data:
            if instance_name.endswith(".gph"):
                new_data[instance_name.replace(".gph", "")] = self.data[instance_name]
            elif instance_name.endswith(".col"):
                new_data[instance_name.replace(".col", "")] = self.data[instance_name]
        # If the file does not end in .yaml, add it
        if not file.endswith(".yaml"):
            file += ".yaml"

        # Write the data to the file
        with open(file, "w") as f:
            yaml.dump(self.data, f)

        return file


if __name__ == "__main__":
    p = Parser()

    # run parse for every file under argv[1]
    for f in os.listdir(sys.argv[1]):
        # expand path
        f = os.path.join(sys.argv[1], f)
        p.parse(f)

    # wirte the yaml to the file in argv[2]
    yaml_file = p.write(sys.argv[2])
