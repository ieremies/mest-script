#!/usr/bin/env python3
"""
Receive a yaml file and convert it to a csv file
"""
import sys
import yaml
import pandas as pd


def yaml_to_csv(yaml_file):
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)

    instances = list(data.keys())

    # Find all unique attributes across all instances
    all_attributes = list(
        set(
            attribute
            for instance_attributes in data.values()
            for attribute in instance_attributes
        )
    )

    # Create an empty DataFrame
    df = pd.DataFrame(columns=all_attributes, index=instances)

    # Fill in the DataFrame with values from the YAML data
    for instance, attributes in data.items():
        df.loc[instance] = [
            attributes.get(attribute, None) for attribute in all_attributes
        ]

    # Replace '.yaml' with '.csv' in the file name
    csv_file = yaml_file.replace(".yaml", ".csv")

    # Write the DataFrame to CSV
    df.to_csv(csv_file)

    print(f"CSV file '{csv_file}' created successfully.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <yaml_file>")
        sys.exit(1)

    yaml_file_path = sys.argv[1]
    yaml_to_csv(yaml_file_path)
