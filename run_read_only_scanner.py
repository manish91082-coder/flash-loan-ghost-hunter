import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from execution.lifecycle import AutonomousLifecycleDaemon

def run_single_scan():
    # Set dummy env vars for the read-only scan so it doesn't fail init
    os.environ.setdefault("PHANTOMX_PRIVATE_KEY", "0x" + "1" * 64)
    os.environ.setdefault("PHANTOMX_EXECUTOR_CONTRACT", "0x7c5cE74e72AEC0748d4726570e81545b1BCDB626")
    
    daemon = AutonomousLifecycleDaemon()
    print("=== STARTING READ-ONLY MAINNET SCAN (1 ITERATION) ===")
    
    chains = daemon.chain_config
    
    for chain_id_str, config in chains.items():
        if not isinstance(config, dict) or "chain_id" not in config:
            continue
        chain_id = int(chain_id_str)
        if chain_id == 8453: # Enforce Base Golden Reference
            daemon._scan_chain(chain_id, config)
            
    print("=== SCAN COMPLETE ===")

if __name__ == "__main__":
    run_single_scan()
