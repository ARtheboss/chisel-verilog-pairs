import os
import json

main_directory = "./output_pairs"
output_file = "./training_data.json"

formatted_pairs = []
for folder_name in os.listdir(main_directory):
    folder_path = os.path.join(main_directory, folder_name)
    
    if os.path.isdir(folder_path):
        scala_code = None
        verilog_code = None

        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
        
            if file_name.endswith(".scala"):
                with open(file_path, 'r') as scala_file:
                    scala_code = scala_file.read().strip()

            elif file_name.endswith(".sv"):
                with open(file_path, 'r') as verilog_file:
                    verilog_code = verilog_file.read().strip()

        if scala_code and verilog_code:
            formatted_pair = {
                "prompt": f"Generate the Verilog code corresponding to this Chisel code {scala_code}",
                "response": verilog_code
            }
            formatted_pairs.append(formatted_pair)

with open(output_file, 'w') as f:
    json.dump(formatted_pairs, f, indent=4)

print(f"Data successfully saved data from {len(formatted_pairs)} files to {output_file}")