import pair_extractor
import subprocess
import os

configs = [
    "RocketConfig",
    "TinyRocketConfig",
    "V4096Ara2LaneRocketConfig",
    "DualRocketConfig",
    "ScratchpadOnlyRocketConfig",
    "MMIOScratchpadOnlyRocketConfig",
    "L1ScratchpadRocketConfig",
    "MulticlockRocketConfig",
    "CustomIOChipTopRocketConfig",
    "PrefetchingRocketConfig",
    "ClusteredRocketConfig",
    "SV48RocketConfig",

    "MINV128D64RocketConfig",

    "GemminiRocketConfig",
    "FPGemminiRocketConfig",
    "LeanGemminiRocketConfig",
    "LeanGemminiPrintfRocketConfig",
    "MempressRocketConfig",
    "AES256ECBRocketConfig",
    "ReRoCCTestConfig",
    "ReRoCCManyGemminiConfig",
    "ZstdCompressorRocketConfig",

    "DualLargeBoomAndDualRocketConfig",
    "DefaultHwachaConfig",
    "DualSmallBoomV3Config",
    "GemminiParamsDSE1",
    "GemminiParamsDSE11",
    "GENV1024D128ShuttleConfig",
    "IbexConfig",
    "LargeBoomV3Config",
    "LargeBoomV4Config",
    "LoopbackNICLargeBoomV3Config",
    "MediumBoomV4Config",
    
    "ShuttleConfig",
    "SmallBoomV3Config",
    "SpikeConfig",

    "Sodor1StageConfig",
    "Sodor2StageConfig",
    "Sodor3StageSinglePortConfig",
    "Sodor3StageConfig",
    "Sodor5StageConfig",
    "SodorUCodeConfig",

    "BoomV4TraceGenConfig",
    "BoomV3TraceGenConfig",
    "NonBlockingTraceGenL2RingConfig",

    "dmiCVA6Config",
    "CVA6Config"
]

chipyard2_configs = [
    "MINV64D64RocketConfig",
    "REFV128D128RocketConfig",
    "REFV256D64RocketConfig",
    "GENV256D128ShuttleConfig",
    "MINV128D64RocketCosimConfig",
    "GENV256D128ShuttleCosimConfig",

    "MultiNoCConfig",
    "SharedNoCConfig",
    "SbusRingNoCConfig",
    "SbusMeshNoCConfig",
    "QuadRocketSbusRingNoCConfig",

    "FFTRocketConfig",
    "GCDTLRocketConfig",
    "GCDAXI4BlackBoxRocketConfig",
    "GCDHLSRocketConfig",
    "InitZeroRocketConfig",
    "StreamingPassthroughRocketConfig",
    "StreamingFIRRocketConfig",
    "SmallNVDLARocketConfig",
    "LargeNVDLARocketConfig",
    "ManyMMIOAcceleratorRocketConfig",
]

def gen_verilog_cmd(config, chipyard2=False):
    if chipyard2:
        cy = "../chipyard2"
    else:
        cy = "../chipyard"
    try:

        folder_path = os.path.join(f"{cy}/sims/vcs/generated-src", f"chipyard.harness.TestHarness.{config}")
        fir_path = os.path.join(f"{cy}/sims/vcs/generated-src", f"chipyard.harness.TestHarness.{config}/chipyard.harness.TestHarness.{config}.fir")
        if folder_path and os.path.isdir(folder_path) and os.path.isdir(fir_path):
            return os.path.isdir(f"{folder_path}/gen-collateral")
        
        print(f"Generating {config}")
        
        # Source the environment
        # subprocess.run(["source ./env.sh"], check=True, shell=True, cwd="../chipyard", stdout=subprocess.DEVNULL)
        # subprocess.run(["source /ecad/tools/vlsi.bashrc"], check=True, shell=True, cwd="../chipyard")
        
        # Execute the make command with the chosen configuration
        subprocess.run([f"make CONFIG={config}"], check=True, shell=True, cwd=f"{cy}/sims/vcs", stdout=subprocess.DEVNULL)
        
        print(f"Verilog generated for config {config}")

        return True
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred for {config}: {e}")

    return False

if __name__ == "__main__":
    for config in configs:
        if gen_verilog_cmd(config):
            pair_extractor.extract_one_to_one_pairs(config)
    for config in chipyard2_configs:
        if gen_verilog_cmd(config, chipyard2=True):
            pair_extractor.extract_one_to_one_pairs(config, chipyard2=True)
            