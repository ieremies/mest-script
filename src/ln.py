#!/usr/bin/env python3

import os
from tqdm import tqdm

# Read the file names from 'files.txt'
with open("files.txt", "r") as file:
    file_names = [line.strip() for line in file.readlines()]

# Iterate through each file and create a symbolic link
for file_name in tqdm(file_names, desc="Creating symlinks", unit="file"):
    command = f"ln -s ../all/{file_name}"
    os.system(command)
