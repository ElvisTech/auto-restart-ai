import time
import os
from utils import safe_parse_json, find_json_files

def tail_file(path):
    with open(path, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            yield line.rstrip("\n"), path

def tail_text_files(paths):
    while True:
        for p in paths:
            if os.path.exists(p):
                with open(p, "r") as f:
                    f.seek(0, os.SEEK_END)
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        yield line.rstrip("\n"), p
        time.sleep(1)

def tail_json_files(glob_patterns):
    files = find_json_files(glob_patterns)
    watchers = {}
    for p in files:
        try:
            f = open(p, "r")
            f.seek(0, os.SEEK_END)
            watchers[p] = f
        except Exception:
            continue
    while True:
        for p, f in list(watchers.items()):
            line = f.readline()
            if not line:
                continue
            parsed = safe_parse_json(line)
            if parsed:
                yield parsed, p
        time.sleep(1)
