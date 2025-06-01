import os
import re
import shutil

def load_verilog_file(file_path, chipyard2=False):
    out_lines = []
    chisel_files = []
    module_name = None

    with open(file_path, 'r') as file:
        lines = file.readlines() 
        lines = [line for line in lines] 

        in_module = False
        in_ifdef = 0
        for line in lines:
            if line.startswith("module"):
                in_module = True
                m = re.search(r"module\s+(?P<module>\S+)\(", line)
                if m:
                    module_name = m.group('module')
            if in_module:
                comment_loc = line.find("//")
                if comment_loc != -1:
                    m = re.search(r"@\[(?P<file>\S+\.scala)\:(?P<line>\d+)\:(?P<char>\d+)\]", line)
                    if m:
                        if not m.group('file').startswith('src'):
                            cf = m.group('file')
                            if cf not in chisel_files:
                                chisel_files.append(cf)
                                # line_set.add(int(m.group('line')))
                    start_comment = line.find("@[")
                    last_slash = line.rfind("/")
                    line = line[:start_comment+2] + line[last_slash+1:]
                if "`ifdef" in line or "`ifndef" in line:
                    in_ifdef += 1
                    continue
                elif "`endif" in line:
                    in_ifdef -= 1
                    continue
                if in_ifdef == 0:
                    out_lines.append(line)
            if line.startswith("endmodule"):
                in_module = False
    return (out_lines, chisel_files, module_name)

def extract_one_to_one_pairs(config, chipyard2=False):

    save_folder = "/scratch/advayratan/chisel-verilog-pairs/output_pairs"
    os.makedirs(save_folder, exist_ok=True)
    collateral_folder = f"/scratch/advayratan/{'chipyard2' if chipyard2 else 'chipyard'}/sims/vcs/generated-src/chipyard.harness.TestHarness.{config}/gen-collateral"
    firrtl_file = f"/scratch/advayratan/{'chipyard2' if chipyard2 else 'chipyard'}/sims/vcs/generated-src/chipyard.harness.TestHarness.{config}/chipyard.harness.TestHarness.{config}.fir"

    path = [
        "/scratch/advayratan/chipyard/", 
        "/scratch/advayratan/chipyard2/", 
        "/scratch/advayratan/chipyard/sims/firesim/sim/rocket-chip/dependencies/chisel/",
        "/scratch/advayratan/chipyard2/sims/firesim/sim/rocket-chip/dependencies/chisel/",
        ] # ram_data_3x64.sv

    wrote = 0

    verilog_modules = dict()

    duplicates = 0

    for filename in os.listdir(collateral_folder):
        file_path = os.path.join(collateral_folder, filename)
        if os.path.isfile(file_path):
            
            verilog_out_lines, chisel_files, module_name = load_verilog_file(file_path)

            if len(verilog_out_lines) == 0 or len(chisel_files) == 0:
                continue

            i = 0
            match_found = False
            while True:
                folder_path = os.path.join(save_folder, f"{filename}_{i}")
                if os.path.exists(folder_path):
                    m = True
                    with open(f"{folder_path}/verilog.sv", "r") as f:
                        lines = f.readlines() 
                        for l1, l2 in zip(lines, verilog_out_lines):
                            if l1 != l2:
                                m = False
                                break
                    if m:
                        match_found = True
                        break
                else:
                    break
                i += 1
            folder_path = os.path.join(save_folder, f"{filename}_{i}")
            verilog_modules[module_name] = folder_path
            if match_found:
                duplicates += 1
                continue
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, 'verilog.sv')
            with open(file_path, 'w') as file:
                file.writelines(verilog_out_lines)

            for i, cf in enumerate(chisel_files):
                found = False
                for p in path:
                    try:
                        name = cf[cf.rfind("/")+1:]
                        shutil.copyfile(f"{p}/{cf}", f"{folder_path}/{name}")
                        found = True
                        break
                    except:
                        continue
                if not found:
                    print(cf)

            # print(f"Written to {file_path}") # , chisel_file, sorted(line_set))

            wrote += 1

    firrtl_matches = 0
    with open(firrtl_file, "r") as file:
        in_module = None
        lines = []
        for line in file.readlines():
            m = re.search(r"\s+module\s+(?P<module>\S+)\s+\:", line)
            if m and in_module != None:
                file_path = os.path.join(verilog_modules[in_module], "firrtl.fir")
                with open(file_path, 'w') as file:
                    file.writelines(lines)
                in_module = None
                firrtl_matches += 1
            if m and m.group('module') in verilog_modules:
                in_module = m.group('module')
                lines = []
            if in_module:
                cl = line.find("@")
                if cl != -1:
                    line = line[:cl]
                lines.append(line + "\n")
        if in_module != None:
            file_path = os.path.join(verilog_modules[in_module], "firrtl.fir")
            with open(file_path, 'w') as file:
                file.writelines(lines)
            firrtl_matches += 1

    
    print(f"{config} wrote {wrote} files for Chisel and {firrtl_matches} files for FIRRTL. There were {duplicates} duplicate files.")

def chisel_files(config, chipyard2=False):
    cf = set()
    collateral_folder = f"/scratch/advayratan/{'chipyard2' if chipyard2 else 'chipyard'}/sims/vcs/generated-src/chipyard.harness.TestHarness.{config}/gen-collateral"
    for filename in os.listdir(collateral_folder):
        file_path = os.path.join(collateral_folder, filename)
        if os.path.isfile(file_path):
            _, chisel_files, _ = load_verilog_file(file_path, chipyard2=chipyard2)
            cf.update(chisel_files)
    return cf

if __name__ == "__main__":
    configs = [
        "RocketConfig",
        "SmallBoomV3Config",
        "IbexConfig"
    ]
    extract_one_to_one_pairs("RocketConfig")
    extract_one_to_one_pairs("DualRocketConfig")
    subdirs = [d for d in os.listdir("output_pairs") if os.path.isdir(os.path.join("output_pairs", d))]
    print(len(subdirs))