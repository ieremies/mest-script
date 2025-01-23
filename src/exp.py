#!/usr/bin/env python3
import sys
import os

from utils.utils import get_all_files

builds = [
    "no_held_trim.e",
    "held_branching.e",
    "no_rec.e",
    "no_heu.e",
    "bp_dsatur_two.e",
    "bp_dsatur_four.e",
    "bp_dsatur_eight.e",
    "bp_rounding_two.e",
    "bp_rounding_four.e",
    "bp_rounding_eight.e",
    "bp_rf_two.e",
    "bp_rf_four.e",
    "bp_rf_eight.e",
    "round_four_five.e",
    "round_six_five.e",
    "direct_four.e",
    "direct_eight.e",
    "direct_fourteen.e",
    "round_two.e",
    "round_four.e",
    "round_eight.e",
]

for b in builds:
    if b[-1] != "e":
        continue
    if "debug.e" in b or "primal.e" in b:
        continue
    # run "py script/src/runner.py {build} easy+medium+dimacsreduced -tl 30"
    print(f"Running {b}")
    os.system(f"python3 script/src/runner.py {b} easy+medium+dimacsreduced -tl 30")
    print(f"Finished {b}")
    print("\n")
