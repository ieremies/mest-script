#!/usr/bin/env python3
from utils.read_write import read_csv_to_dict
import sys
from math import ceil, floor


def check(base, to_check):
    all_good = True
    base = read_csv_to_dict(base)
    to_check = read_csv_to_dict(to_check)

    no_lb = [i for i in to_check if not to_check[i]["lb"]]

    for i in to_check:
        # check if there is an instance in to_check that is not in base
        to_print = []
        if i not in base:
            to_print.append(f"⚠️ We do not have information about {i}.")
            continue

        try:
            base_lb = ceil(float(base[i]["lb"]))
            base_ub = floor(float(base[i]["ub"]))
        except ValueError:
            to_print.append(f"⚠️ We do not have information about {i}.")
            continue

        if not to_check[i]["lb"]:
            # print("❌", i, "has no lower bound.")
            continue
        to_check_lb = ceil(float(to_check[i]["lb"]))
        to_check_ub = floor(float(to_check[i]["ub"]))

        if to_check_lb > 1 and to_check_lb > base_ub:
            to_print.append(f"❌ {i} lower ({to_check_lb}) > base upper ({base_ub}).")
            all_good = False

        if to_check_ub > 1 and to_check_ub < base_lb:
            to_print.append(f"❌ {i} upper ({to_check_ub}) < base lower ({base_lb}).")
            all_good = False

        if to_check_lb > to_check_ub and to_check_lb > 1 and to_check_ub > 1:
            to_print.append(
                f"⚠️ Something is wrong with {i} gap: {to_check_lb} | {to_check_ub}"
            )
            all_good = False

        if base_lb > base_ub and base_lb > 1 and base_ub > 1:
            to_print.append(
                f"⚠️ Something is wrong with {i} base gap: {base_lb} | {base_ub}"
            )
            all_good = False

        if to_check_lb > 1 and to_check_lb > base_lb and all_good:
            to_print.append(
                f"❇️ Found better lower for {i}: (new) {to_check_lb} > (old) {base_lb}"
            )

        if to_check_ub > 1 and to_check_ub < base_ub and all_good:
            to_print.append(
                f"❇️ Found better upper for {i}: (new) {to_check_ub} < (old) {base_ub}"
            )

        to_check_solved = to_check_lb == to_check_ub and to_check_lb > 1
        base_solved = base_lb == base_ub and base_lb > 1

        if to_check_solved and not base_solved:
            to_print.append(f"❇️ {i} is solved, but not in historical results.")
            all_good = False

        if to_print:
            print(i, end=": ")
            if all_good:
                print("✅\n    ", end="")
            elif len(to_print) == 1:
                print(to_print[0])
            else:
                print("❌\n    ", end="")
                print("\n    ".join(to_print))

    if no_lb:
        print(f"❌ {len(no_lb)} instances with no lower bound...")

    return all_good


if __name__ == "__main__":
    check(sys.argv[1], sys.argv[2])
