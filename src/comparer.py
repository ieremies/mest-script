#!/usr/bin/env python3
"""
Compares to json with the results of the parser.
"""

# import json
from math import inf
import yaml
import sys
import os


class Comparer:
    def __init__(self, file1: str, file2: str):
        self.file1 = file1
        self.file2 = file2

        print(f"Comparing {file1.split("/")[-1]} | {file2.split('/')[-1]}")

        self._compare()
        self._print_results()

    def _load_file(self, file_name: str):
        # expand path
        file_name = os.path.expanduser(file_name)
        with open(file_name, "r") as file:
            # read yaml file
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data

    def _compare(self):
        data1 = self._load_file(self.file1)
        data2 = self._load_file(self.file2)

        self._not_found = []
        self._different = []
        for k in data1:
            if k not in data2:
                self._not_found.append(k)
                continue

            lb1 = data1[k]["lower_bound"] if "lower_bound" in data1[k] else 0
            up1 = data1[k]["upper_bound"] if "upper_bound" in data1[k] else inf
            lb2 = data2[k]["lower_bound"] if "lower_bound" in data2[k] else 0
            up2 = data2[k]["upper_bound"] if "upper_bound" in data2[k] else inf
            opt1 = lb1 if lb1 == up1 else 0
            opt2 = lb2 if lb2 == up2 else 0

            if opt2 != 0 and opt1 != opt2:
                self._different.append((k, opt1, opt2))
            if up2 > 0 and (up2 < lb1 or lb2 > up1):
                print(
                    f"❌Error: {k} has bounds ({int(lb1)}, {int(up1)}) and ({lb2}, {up2})"
                )

    def _print_results(self):
        if len(self._not_found) > 0:
            print(f"Not found in {self.file2}:")
            if len(self._not_found) > 10:
                print("\t", len(self._not_found), "instances not found")
            else:
                for k in sorted(self._not_found):
                    print("\t", k)

        if len(self._different) > 0:
            print(
                f"Diff optimal:\t{self.file1.split('/')[-1].replace('.yaml', '')}\t{self.file2.split('/')[-1].replace('.yaml', '')}"
            )
            for k in sorted(self._different):
                print(" ", *k, sep="\t")


if __name__ == "__main__":
    c = Comparer(sys.argv[1], sys.argv[2])
