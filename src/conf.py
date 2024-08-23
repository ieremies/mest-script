#!/usr/bin/env python3

macos_path = "/Users/ieremies/mest"
macos_code = macos_path + "/code"
macos_script = macos_path + "/script"
macos_logs = macos_path + "/logs"
macos_instances = macos_path + "/inst"
macos_hist = macos_instances + "/lit/best.csv"

linux_path = "/home/ieremies"
linux_code = linux_path + "/code"
linux_script = linux_path + "/script"
linux_logs = linux_path + "/logs"
linux_instances = linux_path + "/inst"

default_build = "debug.e"
default_instances = "easy"
default_machine = "spock"
time_limit = 100

debug = False

cmd = "{code}/build/{build} {inst_set}/{instance}"
