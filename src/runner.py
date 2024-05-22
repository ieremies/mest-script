#!/usr/bin/env python3
"""
This is a script to run a command with all possible combinations of files in a given directory.

Usage:
    python3 runner.py "command [file:~/path/to/directory]"
    python3 runner.py "command [file:~/path/to/directory]" ~/path/to/log/directory
    python3 runner.py "command [file:~/path/to/directory]" ~/path/to/log/directory time_limit

    The first argument is the command to be executed. The second argument is the directory where the log files will be saved. The third argument is the time limit for the execution of each command.

    The command can contain multiple arguments. The [file:~/path/to/directory] argument will be replaced by all files in the given directory. The command can also contain the ~ symbol to refer to the home directory.

    The log directory is optional. If not given, the log files will be saved in the current directory.

    The time limit is also optional. If not given, the time limit will be 3600 seconds.

    Example:
    python3 runner.py "python3 script.py [file:~/instances]" ~/logs 3600
"""
import os
import time
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
from random import shuffle
import subprocess

count = 0


class Runner:
    def __init__(
        self,
        log_directory: str,
        commands: str,
        instance_path: str,
        time_limit: int = 3600,
    ):
        self._log_directory = log_directory
        self._time_limit = time_limit
        self._instance_path = instance_path
        self._commands = self._parse_commands(commands)

    def _parse_commands(self, commands: str):
        c = commands.split()
        parsed_commands = []

        for param in c:
            if param.startswith("[file"):
                param_clean = self._cleanup_path(param)
                parsed_commands.append(self._get_all_files(param_clean))
            elif param.startswith("[from_file"):
                param_clean = self._cleanup_path(param)
                parsed_commands.append(self._get_files_from_file(param_clean))
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

    def _get_files_from_file(self, file_path: str):
        """
        Reads a file containing the name of instances. For each one, searches for the file in the instance path recursivelly.
        """
        with open(file_path, "r") as file:
            instance_names = [line.strip() for line in file.readlines()]

        res = []
        for instance_name in instance_names:
            res.extend(
                [
                    file.split()[-1]
                    for file in os.popen(
                        f"find {self._instance_path} -print | grep {instance_name}"
                    )
                    .read()
                    .strip()
                    .split("\n")
                ]
            )
        return res

    def _run_command(self, *args):
        global count
        log_file = ""
        for a in args:
            if "/" in a:
                log_file += a.split("/")[-1] + "_"
        log_file = f"{self._log_directory}/{log_file[:-1]}.log"

        # if log file exists, skip
        if os.path.exists(log_file):
            return

        start_time = time.time()

        with open(log_file, "w") as file:
            # ignore all exceptions
            try:
                subprocess.run(
                    args, timeout=self._time_limit, stdout=file, stderr=file, text=True
                )
            # timeout exception
            except subprocess.TimeoutExpired:
                pass
            except Exception as e:
                print(f"❌ Error: {e}")

        end_time = time.time()
        running_time = end_time - start_time

        with open(log_file, "a") as file:
            count += 1
            file.write(f"\nRunning time: {running_time} seconds\n")

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

        print(count)


def main():
    parser = argparse.ArgumentParser(
        description="Run a command with different file combinations."
    )
    parser.add_argument("command", help="Command to be executed.")
    parser.add_argument(
        "-l",
        default=".",
        dest="log_directory",
        help="Directory where log files will be saved.",
    )
    parser.add_argument(
        "-tl",
        dest="time_limit",
        type=int,
        default=3600,
        help="Time limit for the execution of each command.",
    )
    # --instance-path or -i
    parser.add_argument(
        "-i",
        dest="instance_path",
        type=str,
        default="",
        help="Path to the instance files.",
    )

    args = parser.parse_args()

    r = Runner(args.log_directory, args.command, args.instance_path, args.time_limit)

    total_tasks = 1
    for p in r._commands:
        total_tasks *= len(p)

    print(
        f"Running {args.command}\nLog directory: {args.log_directory}\nTime limit: {args.time_limit}\nUsing {os.cpu_count()} workers\n\t{total_tasks} tasks."
    )
    r.run()


if __name__ == "__main__":
    main()
