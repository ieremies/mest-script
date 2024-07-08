#!/usr/bin/env python3
import os


# TODO in the time, change -1.0 to TL
# TODO in the UB and LB, change -1.0 to ""
def write_csv(results, csv_file):
    header = ",".join(results[0].keys())
    with open(csv_file, "w") as fd:
        fd.write(header + "\n")
        for result in results:
            line = ",".join([str(result[key]) for key in result.keys()])
            fd.write(line + "\n")


def read_csv(csv_file):
    with open(csv_file, "r") as fd:
        lines = fd.readlines()
    header = lines[0].strip().split(",")
    return [
        {k: v for k, v in zip(header, line.strip().split(","))} for line in lines[1:]
    ]


def get_all_files(directory):
    """
    Get a list of all files in a directory, including symbolic links.
    """
    all_files = []
    for root, _, files in os.walk(directory, followlinks=True):
        for name in files:
            filepath = os.path.join(root, name)
            all_files.append(filepath)
    return all_files


if __name__ == "__main__":
    print(read_csv("/Users/ieremies/mest/logs/jun28.csv"))
