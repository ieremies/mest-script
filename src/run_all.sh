#!/usr/bin/env sh

python3 script/src/run_held.py all -tl 500
python3 script/src/runner.py primal.e all -tl 500
