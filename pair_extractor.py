import os
import re
import shutil

def extract_one_to_one_pairs(config):

    save_folder = "/scratch/advayratan/chisel-verilog-pairs/output_pairs"
    os.makedirs(save_folder, exist_ok=True)
    collateral_folder = f"/scratch/advayratan/chipyard/sims/vcs/generated-src/chipyard.harness.TestHarness.{config}/gen-collateral"

    path = ["/scratch/advayratan/chipyard/", "/scratch/advayratan/chipyard/sims/firesim/sim/rocket-chip/dependencies/chisel/"]

    def load_verilog_file(file_path):
        out_lines = []
        chisel_file = None
        line_set = set()

        with open(file_path, 'r') as file:
            lines = file.readlines() 
            lines = [line for line in lines] 

            in_module = False
            in_ifdef = 0
            for line in lines:
                if line.startswith("module"):
                    in_module = True
                if in_module:
                    comment_loc = line.find("//")
                    if comment_loc != -1:
                        m = re.search(r"@\[(?P<file>\S+\.scala)\:(?P<line>\d+)\:(?P<char>\d+)\]", line)
                        if m:
                            if not m.group('file').startswith('src'):
                                if not chisel_file:
                                    chisel_file = m.group('file')
                                    line_set.add(int(m.group('line')))
                                elif chisel_file != m.group('file'):
                                    print("Referenced Chisel files don't match:", chisel_file, m.group('file'))
                                    return (None, None, None)
                                else:
                                    line_set.add(int(m.group('line')))
                        line = line[:comment_loc-1] + "\n"
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
        return (out_lines, chisel_file, line_set)

    wrote = 0

    for filename in os.listdir(collateral_folder):
        file_path = os.path.join(collateral_folder, filename)
        if os.path.isfile(file_path):
            
            verilog_out_lines, chisel_file, line_set = load_verilog_file(file_path)

            if not verilog_out_lines:
                continue

            folder_path = os.path.join(save_folder, filename)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, 'verilog.sv')
            with open(file_path, 'w') as file:
                file.writelines(verilog_out_lines)

            for p in path:
                try:
                    shutil.copyfile(f"{p}/{chisel_file}", f"{folder_path}/chisel.scala")
                    break
                except:
                    continue

            # print(f"Written to {file_path}") # , chisel_file, sorted(line_set))

            wrote += 1
    
    print(f"Config {config} wrote {wrote} files")

if __name__ == "__main__":
    configs = [
        "RocketConfig",
        "SmallBoomV3Config",
        "IbexConfig"
    ]
    extract_one_to_one_pairs(configs[0])