#!/usr/bin/env python3

macos_path = "/Users/ieremies/mest"
macos_code = macos_path + "/code"
macos_script = macos_path + "/script"
macos_logs = macos_path + "/logs"
macos_instances = macos_path + "/inst"

spock_path = "/home/ieremies"
spock_code = spock_path + "/code"
spock_script = spock_path + "/script"
spock_logs = spock_path + "/logs"
spock_instances = spock_path + "/inst"

default_build = "debug.e"
default_instances = "easy"
time_limit = 100

debug = False

cmd = "{code}/build/{build} {inst}/{instance}"
