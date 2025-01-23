#!/usr/bin/env python3

import pandas as pd

my = pd.read_csv("root_gap")
held = pd.read_csv("logs/held-root.csv")
meta = pd.read_csv("inst/metadata.csv")

merged = pd.merge(my, held, on="instance", suffixes=("_my", "_held"))
merged = pd.merge(merged, meta, on="instance", suffixes=("", "_meta"))
merged.loc[merged["lb"] == merged["ub"], "chi"] = merged["lb"]

# Check if 'lb_my' == 'lb_held' & 'components' == 1 & 'components_complement' == 1
print("Root check (only on connected instances)!")
root_lb = merged[
    (merged["lb_my"] != merged["lb_held"])
    & (merged["components"] == 1)
    & (merged["components_complement"] == 1)
]
print(root_lb)

# Throw away any lines where 'lb_my' == 'ub_my' & 'lb_my' == 'lb'
unsolved = merged[
    ~((merged["lb_my"] == merged["ub_my"]) & (merged["lb_my"] == merged["lb"]))
]
unsolved = unsolved[
    ["instance", "lb_my", "ub_my", "lb_held", "ub_held", "lb", "ub", "chi"]
]
unsolved["gap"] = unsolved["ub_my"] - unsolved["lb_my"]
unsolved["UB-opt"] = unsolved["ub_my"] - unsolved["chi"]
unsolved["opt-LB"] = unsolved["chi"] - unsolved["lb_my"]
print(unsolved)

# # If unsolved["gap"] < 0 is not empty, print it
# if not unsolved[unsolved["gap"] < 0].empty:
#     print("Negative gap!")
#     print(unsolved[unsolved["gap"] < 0])

# # If unsolved["UB-opt"] < 0 is not empty, print it
# if not unsolved[unsolved["UB-opt"] < 0].empty:
#     print("Negative UB-opt!")
#     print(unsolved[unsolved["UB-opt"] < 0])

# # If unsolved["opt-LB"] < 0 is not empty, print it
# if not unsolved[unsolved["opt-LB"] < 0].empty:
#     print("Negative opt-LB!")
#     print(unsolved[unsolved["opt-LB"] < 0])

# print the quantity of instances with gap >= 2
print(f"Gap >= 4 : {len(unsolved[unsolved["gap"] >= 4]):<4}")
print(f"Gap == 3 : {len(unsolved[unsolved["gap"] == 3]):<4}")
print(f"Gap == 2 : {len(unsolved[unsolved["gap"] == 2]):<4}")
print(f"Gap == 1 : {len(unsolved[unsolved["gap"] == 1]):<4}")


print(f"UB-Opt >= 4 : {len(unsolved[unsolved["UB-opt"] >= 4]):<4}")
print(f"UB-Opt == 3 : {len(unsolved[unsolved["UB-opt"] == 3]):<4}")
print(f"UB-Opt == 2 : {len(unsolved[unsolved["UB-opt"] == 2]):<4}")
print(f"UB-Opt == 1 : {len(unsolved[unsolved["UB-opt"] == 1]):<4}")

print(f"Opt-LB >= 4 : {len(unsolved[unsolved["opt-LB"] >= 4]):<4}")
print(f"Opt-LB == 3 : {len(unsolved[unsolved["opt-LB"] == 3]):<4}")
print(f"Opt-LB == 2 : {len(unsolved[unsolved["opt-LB"] == 2]):<4}")
print(f"Opt-LB == 1 : {len(unsolved[unsolved["opt-LB"] == 1]):<4}")

print(unsolved[unsolved["UB-opt"] >= 4])
