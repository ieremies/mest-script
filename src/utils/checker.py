#!/usr/bin/env python3
import pandas as pd
import os

import conf

inst = conf.macos_instances if os.uname().sysname == "Darwin" else conf.linux_instances

hist = {
    line[1]["instance"]: dict(line[1])
    for line in pd.read_csv(f"{inst}/metadata.csv").iterrows()
}

root = {
    line[1]["instance"]: dict(line[1])
    for line in pd.read_csv(f"{inst}/held-root.csv").iterrows()
}


def check(i: dict) -> list[str]:
    # get the line from hist with hist["instance"] == inst["instance"]
    inst = i["instance"] + " " * (14 - len(i["instance"]))
    if i["instance"] not in hist.keys():
        return [f"🚧 {inst}: Instance not found in historical data."]

    h = hist[i["instance"]]

    i["lb"] = int(i["lb"]) if i["lb"] else None
    i["ub"] = int(i["ub"]) if i["ub"] else None
    try:
        i["root_lb"] = int(i["root_lb"]) if "root_lb" in i and i["root_lb"] else None
    except ValueError:
        i["root_lb"] = None

    try:
        held = int(root[i["instance"]]["lb"])
    except ValueError:
        held = None

    # TODO adicionar checks da raiz
    if i["root_lb"] and held and i["root_lb"] != held:
        return [f"❌ {inst}: My root LB {i['root_lb']} != Held's LB {held}."]
    if i["lb"] and h["ub"] < i["lb"]:
        return [f"❌ {inst}: LB {i['lb']} is higher than historical UB {h['ub']}."]
    if i["ub"] and h["lb"] > i["ub"]:
        return [f"❌ {inst}: UB {i['ub']} is lower than historical LB {h['lb']}."]

    if i["lb"] and h["lb"] != h["ub"] and i["lb"] == i["ub"]:
        return [f"⭐ {inst}: We closed an instance never solved before!"]

    ret = []
    if i["ub"] and h["ub"] > i["ub"]:
        ret.append(f"🎀 {inst}: UB {i['ub']} is better the historical UB {h['ub']}.")
    if i["lb"] and h["lb"] < i["lb"]:
        ret.append(f"🎀 {inst}: LB {i['lb']} is better the historical LB {h['lb']}.")

    return ret
