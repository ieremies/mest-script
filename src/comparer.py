#!/usr/bin/env python3
"""
Compares to json with the results of the parser.
"""

import json
import sys
import os


class Comparer:
    def __init__(self, file1: str, file2: str):
        self.file1 = file1
        self.file2 = file2

        self._compare()

    def _load_file(self, file_name: str):
        # expand path
        file_name = os.path.expanduser(file_name)
        with open(file_name, "r") as file:
            data = json.load(file)
        return data

    def _compare(self):
        data1 = self._load_file(self.file1)
        data2 = self._load_file(self.file2)

        for k in data1:
            if k not in data2:
                print(f"{k} NOT FOUND")
                continue

            if (
                data1[k]["upper_bound"] == data1[k]["lower_bound"]
                and data2[k]["upper_bound"] == data2[k]["lower_bound"]
            ):
                if data1[k]["upper_bound"] != data2[k]["upper_bound"]:
                    print(
                        f"{k} DIFFERENT {data1[k]['upper_bound']} {data2[k]['upper_bound']}"
                    )


if __name__ == "__main__":
    c = Comparer(sys.argv[1], sys.argv[2])
