#!/usr/bin/env python3
import os
import csv


# TODO in the time, change -1.0 to TL
# TODO in the UB and LB, change -1.0 to ""
def write_csv(results, csv_file):
    header = ",".join(results[0].keys())
    with open(csv_file, "w") as fd:
        fd.write(header + "\n")
        for result in results:
            line = ",".join([str(result[key]) for key in result.keys()])
            fd.write(line + "\n")


def write_dict_to_csv(data, file_path):
    # Gather all unique keys from inner dictionaries
    headers = set()
    for value in data.values():
        headers.update(value.keys())
    headers = list(headers)
    headers.sort()

    # Write to CSV
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["instance"] + headers)

        # Write rows
        for instance, values in data.items():
            row = [instance] + [values.get(header, "") for header in headers]
            writer.writerow(row)


def read_csv(csv_file):
    with open(csv_file, "r") as fd:
        lines = fd.readlines()
    header = lines[0].strip().split(",")
    return [
        {k: v for k, v in zip(header, line.strip().split(","))} for line in lines[1:]
    ]


def read_csv_to_dict(csv_file) -> dict:
    with open(csv_file, "r") as fd:
        lines = fd.readlines()
    header = lines[0].strip().split(",")
    # first element if the key
    d = {}
    for line in lines[1:]:
        values = line.strip().split(",")
        key = values[0]
        d[key] = {k: v for k, v in zip(header[1:], values[1:])}
    return d
