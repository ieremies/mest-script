#!/usr/bin/env python3
"""
This script takes a number o csv files and combines the data into yaml file.

Each csv file has three columns: instance, LB and UB. The instance column
contains the name of the instance, the LB column contains the lower bound
and the UB column contains the upper bound.

The result file will contain a dictionary with the instance name as key and
the greater lower bound and lowest upper bound as values, together with a
comment from ehich file the data came from.
"""
import sys
import csv
import yaml
from collections import defaultdict


def combine_csv_to_yaml(csv_files, output_yaml):
    data_dict = defaultdict(
        lambda: {"LB": float("-inf"), "UB": float("inf"), "source_files": []}
    )

    # Process each CSV file
    for csv_file in csv_files:
        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                instance = row["instance"]
                lb = float(row["LB"])
                ub = float(row["UB"])

                # Update data dictionary
                if lb > data_dict[instance]["LB"]:
                    data_dict[instance]["LB"] = lb
                    data_dict[instance]["lb_source_file"] = csv_file.split("/")[
                        -1
                    ].split(".")[0]
                if ub < data_dict[instance]["UB"]:
                    data_dict[instance]["UB"] = ub
                    data_dict[instance]["ub_source_file"] = csv_file.split("/")[
                        -1
                    ].split(".")[0]

                # Add source file information
                data_dict[instance]["source_files"].append(csv_file)

    # Write to YAML file
    with open(output_yaml, "w") as yaml_file:
        for instance, values in data_dict.items():
            yaml_file.write(f"{instance}:\n")
            yaml_file.write(
                f"    lower_bound: {values['LB']}. # {data_dict[instance]['lb_source_file']}\n"
            )
            yaml_file.write(
                f"    upper_bound: {values['UB']}  # {data_dict[instance]['ub_source_file']}\n"
            )


if __name__ == "__main__":
    # Check if at least two arguments are provided (script name + at least one CSV file)
    if len(sys.argv) < 3:
        print("Usage: python script.py <output_yaml> <csv_file1> [<csv_file2> ...]")
        sys.exit(1)

    # Extract command-line arguments
    output_yaml = sys.argv[1]
    csv_files = sys.argv[2:]

    combine_csv_to_yaml(csv_files, output_yaml)
