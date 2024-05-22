#!/usr/bin/env python3
import yaml

hist = "logs/hist.yaml"
dsatur = "logs/primal_base.yaml"

# read yaml files
with open(hist, "r") as file:
    hist_data = yaml.load(file, Loader=yaml.FullLoader)
with open(dsatur, "r") as file:
    dsatur_data = yaml.load(file, Loader=yaml.FullLoader)

# if hist_data[i]["upper_bound"] == hist_data[i]["lower_bound"] then
# print(i, dsatur_data[i]["dsatur_value"], hist_data[i]["upper_bound"])
for i in dsatur_data:
    if (
        i in hist_data
        and hist_data[i]["lower_bound"] == hist_data[i]["upper_bound"]
        and "lower_bound" in dsatur_data[i]
        and dsatur_data[i]["lower_bound"] < hist_data[i]["upper_bound"] - 2
    ):
        print(
            i, dsatur_data[i]["lower_bound"], int(hist_data[i]["upper_bound"]), sep="  "
        )
