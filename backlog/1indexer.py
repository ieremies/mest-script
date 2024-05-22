#!/usr/bin/env python3
"""
Reads a DIMACS instance. If its zero-indexed, it will be converted to one-indexed.
"""


from sys import argv
import os


def convert(file: str):
    with open(file, "r") as f:
        lines = f.readlines()
        zero_indexed = 0
        for l in lines:
            if l.startswith("e"):
                _, a, b = l.split()
                if int(a) == 0 or int(b) == 0:
                    zero_indexed = 1
        new_file = file.replace("hugo", "fix")
        new_file = new_file.replace("color3", "fix")
        new_file = new_file.replace("cedric", "fix")
        if zero_indexed == 1:
            with open(new_file, "w") as f:
                for l in lines:
                    if l.startswith("e"):
                        _, a, b = l.split()
                        f.write(f"e {int(a) + zero_indexed} {int(b) + zero_indexed}\n")
                    else:
                        f.write(l)


if __name__ == "__main__":

    # For every file in argv[1], call the convert function
    for file in os.listdir(argv[1]):
        convert(argv[1] + file)
