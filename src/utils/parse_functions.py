#!/usr/bin/env python3
"""
All functions should call the grep function to get the lines of interest
and return a pair (key, value) to be added to the dictionary.
"""
import re
import subprocess


def gnugrep(pattern: str, file: str, max_matches: int = -1) -> list[str]:
    command = f"grep -m {max_matches} '{pattern}' {file}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    res = result.stdout.strip().split("\n")
    if len(res) == 1 and res[0] == "":
        return []
    return res


def pygrep(pattern: str, file: list[str], max_matches: int = -1) -> list[str]:
    regex = re.compile(pattern)
    matches = []
    for line in file:
        if regex.search(line):
            matches.append(line.strip())
            if max_matches > 0 and len(matches) >= max_matches:
                break
    return matches


def grep(pattern: str, file: str | list[str], max_matches: int = -1) -> list[str]:
    if isinstance(file, str):
        return gnugrep(pattern, file, max_matches)
    return pygrep(pattern, file, max_matches)


def get_n_components(log_file) -> dict:
    n_comp = grep("INFO| { Solver.", log_file, max_matches=1)
    if not n_comp:
        return {"components": None}

    return {"components": len(n_comp)}


def get_errors(log_file) -> dict:
    errors = grep("ERR", log_file) + grep("FATL", log_file)
    return {"errors": errors if errors else None}


def get_warnings(log_file) -> dict:
    warn = grep("WARN", log_file)
    return {"warnings": warn if warn else None}


def get_time(log_file) -> dict:
    time = grep("atexit", log_file, max_matches=1)
    if not time:
        return {"time": None}
    return {"time": float(time[0].split("s)")[0][1:])}


def get_final_solution(log_file) -> dict:
    final = grep("Coloring: SOL", log_file, max_matches=1)
    if not final:
        return {"solved": ""}
    value = float(final[0].split("SOL")[-1].split()[0])
    return {"solved": value}


def get_lb(log_file) -> dict:
    comp = get_n_components(log_file)["components"]
    if not comp is None and comp > 1:
        return {"lb": ""}

    root = grep("Root ", log_file)
    if not root:
        return {"lb": ""}

    value = float(root[0].split()[-3])
    return {"lb": value}


def get_ub(log_file) -> dict:
    initial = grep("INFO| Upper bound", log_file, max_matches=1)
    if not initial:
        return {"ub": ""}

    initial = int(initial[0].split()[-1])

    comp = get_n_components(log_file)["components"]
    if not comp is None and comp > 1:
        return {"ub": initial}

    all = [initial]
    upper = grep("New upper bound:", log_file) + grep("New UB:", log_file)
    for u in upper:
        all.append(int(u.split()[-1]))

    return {"ub": max(all)}


def get_root_solution(log_file) -> dict:
    root = grep("Root ", log_file, max_matches=1)
    if not root or len(root) > 1:
        return {"root": ""}

    ub = int(root[0].split()[-1])
    lb = int(root[0].split()[-3])
    time = float(root[0].split()[1][:-2])

    return {"root_time": time, "root_lb": lb, "root_ub": ub}
