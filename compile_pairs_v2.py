import os
import json

main_directory = "./output_pairs"
chisel_output = "./dataset/chisel_verilog_training_data_2.json"
firrtl_output = "./dataset/firrtl_verilog_training_data.json"

chisel_formatted_pairs = []
firrtl_formatted_pairs = []
for folder_name in os.listdir(main_directory):
    folder_path = os.path.join(main_directory, folder_name)
    
    if os.path.isdir(folder_path):
        scala_code = []
        verilog_code = None
        fir_code = None

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
        
            if file_name.endswith(".scala"):
                with open(file_path, 'r') as scala_file:
                    scala_code.append(scala_file.read().strip())

            elif file_name.endswith(".sv"):
                with open(file_path, 'r') as verilog_file:
                    verilog_code = verilog_file.read().strip()

            elif file_name.endswith(".fir"):
                with open(file_path, 'r') as fir_file:
                    fir_code = fir_file.read().strip()

        if len(scala_code) > 0 and verilog_code:
            scala_comb = '\n'.join(scala_code)
            formatted_pair = {
                "prompt": f"Generate the Verilog code corresponding to this Chisel code {scala_comb}",
                "response": verilog_code
            }
            chisel_formatted_pairs.append(formatted_pair)
        if fir_code and verilog_code:
            formatted_pair = {
                "prompt": f"Generate the Verilog code corresponding to this FIRRTL code {fir_code}",
                "response": verilog_code
            }
            firrtl_formatted_pairs.append(formatted_pair)

with open(chisel_output, 'w') as f:
    json.dump(chisel_formatted_pairs, f, indent=4)

with open(firrtl_output, 'w') as f:
    json.dump(firrtl_formatted_pairs, f, indent=4)

print(f"Chisel/Verilog successfully saved data from {len(chisel_formatted_pairs)} files to {chisel_output}")
print(f"FIRRTL/Verilog successfully saved data from {len(firrtl_formatted_pairs)} files to {firrtl_output}")