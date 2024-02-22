#!/usr/bin/env python3
import os
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
from random import shuffle
import subprocess


class Runner:
    def __init__(self, log_directory: str, commands: str, time_limit: int = 3600):
        self._log_directory = log_directory
        self._commands = self._parse_commands(commands)
        self._time_limit = time_limit

    def _parse_commands(self, commands: str):
        c = commands.split()
        parsed_commands = []

        for param in c:
            if param.startswith("[file"):
                param_clean = self._cleanup_path(param)
                parsed_commands.append(self._get_all_files(param_clean))
            elif param.startswith("~/"):
                param_clean = os.path.expanduser(param)
                parsed_commands.append([param_clean])
            else:
                parsed_commands.append([param])

        return parsed_commands

    def _cleanup_path(self, path: str):
        path = path.split(":")[1][:-1]
        if path.startswith("~/"):
            path = os.path.expanduser(path)
        if path[-1] == "/":
            path = path[:-1]
        return path

    def _get_all_files(self, path: str):
        """
        Gets all files under a given diretory
        """
        res = [
            file.split()[-1]
            for file in os.popen(f"find {path} -type f -ls | sort -n -k7")
            .read()
            .strip()
            .split("\n")
        ]
        # remove all that contains ".directory"
        shuffle(res)
        return [file for file in res if ".directory" not in file]

    def _run_command(self, *args):
        log_file = ""
        # TODO this will get the bin name an the instance name,
        # but not any option such as "-b 2"
        for a in args:
            if "/" in a:
                log_file += a.split("/")[-1] + "_"
        log_file = f"{self._log_directory}/{log_file[:-1]}.log"

        # print(f"Running {' '.join(args)} > {log_file}")
        with open(log_file, "w") as file:
            subprocess.run(
                args, timeout=self._time_limit, stdout=None, stderr=file, text=True
            )

    def run(self):
        if not os.path.exists(self._log_directory):
            os.makedirs(self._log_directory)

        total_tasks = 1
        for p in self._commands:
            total_tasks *= len(p)

        max_workers = os.cpu_count()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._run_command, *p) for p in product(*self._commands)
            ]

            with tqdm(total=total_tasks) as pbar:
                for _ in as_completed(futures):
                    pbar.update()


if __name__ == "__main__":
    r = Runner(sys.argv[2], sys.argv[1])
    r.run()
