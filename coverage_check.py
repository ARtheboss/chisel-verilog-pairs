import gen_all_configs
import pair_extractor

import os

MODULE_ONLY = None # "sodor"
SHOW_FILES = False

EXCLUDE_FILES = [
    "util",
    "debug",
    "instructions",
    "package",
    "consts"
]

def not_excluded(s: str):
    for ef in EXCLUDE_FILES:
        if s.endswith(f"{ef}.scala"):
            return False
    return True

def find_scala_files(directory: str, used_files):
    scala_files = set()
    total = 0
    hits = 0
    if os.path.isfile(directory):
        if directory.endswith(".scala") and not_excluded(directory):
            scala_files.add(directory)
            d = directory[len("../chipyard/"):]
            if d in used_files:
                hits += 1
        return (scala_files, hits, 1)
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".scala") and not_excluded(filename):
                dp = dirpath[len("../chipyard/"):]
                path = os.path.join(dp, filename)
                if path in used_files:
                    hits += 1
                    if SHOW_FILES:
                        print(path)
                elif SHOW_FILES:
                    print(f"\033[91m{path}\033[0m")
                total += 1
                scala_files.add(path)
    return (scala_files, hits, total)

def find_scala_src(directory, used_files):
    scala_files = set()
    for entry in os.listdir(directory):
        scala_src = os.path.join(directory, entry, "src", "main", "scala")
        if MODULE_ONLY and MODULE_ONLY not in scala_src:
            continue
        if os.path.isdir(scala_src):
            hits = 0
            total = 0
            for p in os.listdir(scala_src):
                s, h, t = find_scala_files(os.path.join(scala_src, p), used_files)
                scala_files.update(s)
                hits += h
                total += t
        print(f"{entry}: {hits}/{total}")
    return scala_files

cf = set()
for config in gen_all_configs.configs:
    if gen_all_configs.gen_verilog_cmd(config):
        cf.update(pair_extractor.chisel_files(config))
for config in gen_all_configs.chipyard2_configs:
    if gen_all_configs.gen_verilog_cmd(config, chipyard2=True):
        cf.update(pair_extractor.chisel_files(config, chipyard2=True))

all_cf = set(find_scala_src("../chipyard/generators", cf))

print(len(cf), len(all_cf))