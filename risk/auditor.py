import json
import os
import hashlib
from datetime import datetime

class IndependentAuditor:
    def __init__(self, manifest_path="PFLC_5.4R_Evidence_Manifest.jsonl", log_dir="PFLC_5.4R_Reports"):
        self.manifest_path = manifest_path
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
    def verify_manifest(self):
        """
        Validates evidence lineage and cryptographic consistency.
        """
        if not os.path.exists(self.manifest_path):
            return False, ["Evidence manifest not found."], 0
            
        violations = []
        valid_records = 0
        
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            prev_hash_tracker = "0" * 64
            
            for line_no, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    entry_hash = entry.get("hash")
                    data = entry.get("data", {})
                    
                    # Cryptographic verification (P0-17)
                    data_str = json.dumps(data, sort_keys=True)
                    expected_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
                    
                    if entry_hash != expected_hash:
                        violations.append(f"Line {line_no}: Cryptographic Hash Mismatch! Data mutated.")
                        continue
                        
                    # Chain Parity Verification (P0-17)
                    if data.get("prev_hash") != prev_hash_tracker:
                        violations.append(f"Line {line_no}: Hash Chain Broken! Expected prev_hash {prev_hash_tracker}, got {data.get('prev_hash')}")
                    
                    prev_hash_tracker = entry_hash
                        
                    # Semantic Checks (P0-17)
                    status = data.get("final_status")
                    if status == "RECONCILED":
                        if not data.get("tx_hash"):
                            violations.append(f"Line {line_no}: Status RECONCILED but missing tx_hash.")
                        if data.get("receipt_status") != 1:
                            violations.append(f"Line {line_no}: Status RECONCILED but receipt_status != 1.")
                        if data.get("actual_gas_used") is None or data.get("actual_gas_used") <= 0:
                            violations.append(f"Line {line_no}: Status RECONCILED but invalid actual_gas_used.")
                        if data.get("effective_gas_price") is None or data.get("effective_gas_price") <= 0:
                            violations.append(f"Line {line_no}: Status RECONCILED but invalid effective_gas_price.")
                            
                    # Missing fields validation
                    if not data.get("expected_profit"):
                        violations.append(f"Line {line_no}: Missing expected_profit.")
                    if data.get("execution_mode") in ["TESTNET", "MAINNET_CAPITAL"] and not data.get("execution_block"):
                        violations.append(f"Line {line_no}: Missing execution_block for active transaction.")
                    if data.get("execution_mode") in ["TESTNET", "MAINNET_CAPITAL"] and not data.get("calldata_hash"):
                        violations.append(f"Line {line_no}: Missing calldata_hash for verifiable intent payload.")
                    
                    valid_records += 1
                except Exception as e:
                    violations.append(f"Line {line_no}: Parse error - {e}")
                    
        # P0-16: Zero records is FAIL
        if valid_records == 0:
            return False, ["Evidence manifest was empty or no valid JSON records found. Empty manifests are NOT valid."], 0
            
        return len(violations) == 0, violations, valid_records

    def audit(self):
        print("Starting Independent Forensic Audit (Semantic JSON Verification)...")
        is_valid, violations, valid_records = self.verify_manifest()
        
        report = f"# PFLC-5.4R Independent Execution Audit\n\n"
        report += f"**Timestamp**: {datetime.now().isoformat()}\n"
        
        report += "## Evidence Lineage Verification\n"
        if not is_valid:
            report += "**Status: FAILED**\n"
            report += "Cryptographic or Semantic violations found in Evidence Manifest:\n"
            for v in violations:
                report += f"- {v}\n"
        else:
            report += "**Status: PASS**\n"
            report += f"All {valid_records} records verified successfully with cryptographic hashes.\n"
            
        with open(os.path.join(self.log_dir, "PFLC_5.4R_Audit_Report.md"), "w") as f:
            f.write(report)
            
        print("Audit Complete. Report generated.")

if __name__ == "__main__":
    IndependentAuditor().audit()
