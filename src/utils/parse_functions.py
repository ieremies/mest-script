#!/usr/bin/env python3
"""
All functions should call the grep function to get the lines of interest
and return a pair (key, value) to be added to the dictionary.
"""
import re
import subprocess


def ggrep(pattern: str, file: str, max_matches: int = 1) -> list[str]:
    """
    Uses linux grep to get the lines that match the pattern and
    return a list of those lines.
    """
    command = f"grep -m {max_matches} '{pattern}' {file}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    res = result.stdout.strip().split("\n")
    if len(res) == 1 and res[0] == "":
        return []
    return res


def pygrep(pattern: str, file: list[str], max_matches: int = 1) -> list[str]:
    regex = re.compile(pattern)
    matches = []
    for line in file:
        if regex.search(line):
            matches.append(line.strip())
            if len(matches) >= max_matches:
                break
    return matches


def grep(pattern: str, file: str | list[str], max_matches: int = 1) -> list[str]:
    if isinstance(file, str):
        return ggrep(pattern, file, max_matches)
    return pygrep(pattern, file, max_matches)


def get_n_components(log_file) -> tuple:
    """
    Get the number of components from the log file.
    """
    n_comp = grep("Read graph", log_file, max_matches=1)
    if not n_comp:
        return "components", None

    value = int(n_comp[0].split()[-3][:-1])
    return "components", value


def get_errors(log_file) -> tuple:
    """
    Get the errors from the log file.
    """
    return "errors", grep("ERR", log_file) + grep("FATL", log_file)


def get_warnings(log_file) -> tuple:
    """
    Get the warnings from the log file.
    """
    return "warnings", grep("WARN", log_file)


def get_time(log_file) -> tuple:
    """
    Get the time from the log file based on the "atexit" message.
    If none is found, the instance has reached time limit.
    """
    time = grep("atexit", log_file, max_matches=1)
    if not time:
        return "time", ""
    return "time", float(time[0].split("s)")[0][1:])


def get_final_solution(log_file) -> tuple:
    """
    Get the final solution from the log file.
    """
    final = grep("Coloring: SOL", log_file, max_matches=1)
    if not final:
        return "solved", ""
    value = float(final[0].split("SOL")[-1].split()[0])
    return "solved", value


def get_lb(log_file) -> tuple:
    """
    Get the lower bound from the log file.
    """
    _, comp = get_n_components(log_file)
    if not comp is None and comp > 1:
        return "lb", ""

    root = grep("Root with value ", log_file)
    if not root:
        return "lb", ""
    value = float(root[0].split()[-1])
    return "lb", value


def get_ub(log_file) -> tuple:
    """
    Get the upper bound from the log file.
    """
    _, comp = get_n_components(log_file)
    if not comp is None and comp > 1:
        return "ub", ""

    dsatur = grep("DSATUR: ", log_file, max_matches=1)
    if not dsatur:
        return "ub", ""
    value = float(dsatur[0].split()[-1])

    upper = grep("New upper bound", log_file)
    if upper:
        upper[0].replace("(integral sol)", "")
        value = float(upper[0].split()[-1])

    return "ub", value


# def get_n_branchs(log_file) -> tuple:
#     """
#     Get the number of branchs from the log file.
#     """
#     return "branchs", len(grep("{ next ub=", log_file)) - 1


# def get_deepest_branch(log_file) -> tuple:
#     """
#     Get the deepest branch from the log file.
#     """
#     branchs = grep("Stack size", log_file)
#     max_depth = 0

#     for b in branchs:
#         depth = int(b.split()[-1])
#         max_depth = max(max_depth, depth)

#     return "deepest", max_depth


# def get_root_solution(log_file) -> tuple:
#     """
#     Get the root solution from the log file.
#     """
#     root = grep("Root with value ", log_file, max_matches=1)
#     if not root:
#         return "root_solution", ""
#     value = float(root[0].split()[-1])
#     return "root", value


# def get_root_gap(log_file) -> tuple:
#     """
#     Get the root gap from the log file.
#     """
#     root = grep("Root gap ", log_file, max_matches=1)
#     if not root:
#         return "root_gap", ""
#     value = float(root[0].split()[-1])
#     return "root_gap", value


# def get_root_n_sets(log_file) -> tuple:
#     """
#     Get the number of sets from the root solution.
#     """
#     final = grep("Final model with ", log_file, max_matches=1)
#     if not final:
#         return "root_sets", ""
#     value = int(final[0].split("sets")[0].split()[-1])
#     return "root_sets", value


# def get_n_pricing(log_file) -> tuple:
#     """
#     Get the number of pricing from the log file.
#     """
#     return "n_pricing", len(grep(" s: Pricing::solve", log_file))


# def get_n_pricing_with_one_set(log_file) -> tuple:
#     """
#     Get the number of pricing with one set from the log file.
#     """
#     return "n_pricing_one_set", len(grep("Found 1 violated sets!", log_file))


# def get_sum_pricing_time(log_file) -> tuple:
#     """
#     Get the sum of pricing time from the log file.
#     """
#     pricing = grep(" s: Pricing::solve", log_file)
#     time = 0.0
#     for p in pricing:
#         time += float(p.split(" s: Pricing::solve")[0].split()[-1])

#     return "sum_pricing_time", round(time, 3)


# def get_sum_gurobi_time(log_file) -> tuple:
#     """
#     Get the sum of gurobi time from the log file.
#     """
#     gurobi = grep("Solved in ", log_file)
#     time = 0.0
#     for g in gurobi:
#         time += float(g.split("Solved in ")[-1].split()[0])

#     return "sum_gurobi_time", round(time, 3)
