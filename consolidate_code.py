import os

base_dir = r"c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter"
files_to_consolidate = [
    "economics/profit_calculator.py",
    "quote_engine/adapters.py",
    "quote_engine/rpc_fetcher.py",
    "data/live_chain_verifier.py",
    "risk/risk_guard.py",
    "execution/pipeline.py",
    "tests/adversarial/test_negative_controls.py",
    "scripts/pflc_5_1_runner.py",
    "scripts/pflc_5_1_master_runner.py",
    "scripts/pflc_5_1_auditor.py"
]

output_file = os.path.join(base_dir, "PFLC_5.1_Consolidated_Code.md")

with open(output_file, "w", encoding="utf-8") as out_f:
    out_f.write("# PFLC-5.1 Consolidated Code\n\n")
    for file_path in files_to_consolidate:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            out_f.write(f"## File: `{file_path}`\n\n")
            out_f.write("```python\n")
            with open(full_path, "r", encoding="utf-8") as in_f:
                out_f.write(in_f.read())
            out_f.write("\n```\n\n")
        else:
            out_f.write(f"## File: `{file_path}`\n\n")
            out_f.write(f"> ERROR: File not found at {full_path}\n\n")

print(f"Consolidation complete. Output written to {output_file}")
