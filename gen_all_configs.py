import pair_extractor
import subprocess

configs = [
    "RocketConfig",
    "SmallBoomV3Config",
    "IbexConfig"
]

def gen_verilog_cmd(config):
    try:
        # Change directory to chipyard
        subprocess.run(["cd", "../chipyard"], check=True, shell=True)
        
        # Source the environment
        subprocess.run(["source ./env.sh"], check=True, shell=True)
        subprocess.run(["source /ecad/tools/vlsi.bashrc"], check=True, shell=True)
        
        # Change to sims/vcs directory
        subprocess.run(["cd", "sims/vcs"], check=True, shell=True)
        
        # Execute the make command with the chosen configuration
        subprocess.run([f"make CONFIG={config}"], check=True, shell=True)
        
        print(f"Verilog generated for config {config}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

for config in configs:
    gen_verilog_cmd(config)
    pair_extractor.extract_one_to_one_pairs(config)