import os

files_changed = [
    ("execution/lifecycle.py", "Removed DummyProvider, enforced strict flash loan provider checking"),
    ("scripts/pflc_5_1_runner.py", "Removed dummies, enforced strict gas checking and fee configuration"),
    ("phantomx_sprint5_runner.py", "Removed DummyProvider and simulated bridge fees"),
    ("economics/profit_calculator.py", "Removed L1 fee fallback logic, enforcing strict failure on error"),
    ("quote_engine/adapters.py", "Removed default fee_bips for V2 adapter to mandate configuration"),
    ("quote_engine/rpc_fetcher.py", "Added strict chain ID verification and fixed block-based quote age calculation"),
    ("data/live_chain_verifier.py", "Added deep pool verification logic retrieving actual token and reserve states"),
    ("scripts/pflc_5_3_intensive_runner.py", "Created 30-minute intensive mode structure as per rule 48"),
    ("PFLC-5.3_FINAL_FORENSIC_EXECUTION_REPORT.md", "Final required execution forensic report")
]

output_file = "PFLC-5.3_Consolidated_Modifications.md"

with open(output_file, 'w') as out_f:
    out_f.write("# PFLC-5.3 Consolidated File Modifications\n\n")
    
    for file_path, summary in files_changed:
        if os.path.exists(file_path):
            with open(file_path, 'r') as in_f:
                content = in_f.read()
                
            out_f.write(f"## {file_path}\n")
            out_f.write(f"**Summary of Changes**: {summary}\n\n")
            out_f.write("```python\n" if file_path.endswith('.py') else "```markdown\n")
            out_f.write(content)
            out_f.write("\n```\n\n")
        else:
            out_f.write(f"## {file_path}\n")
            out_f.write(f"**Summary of Changes**: {summary}\n\n")
            out_f.write(f"> File not found at path: {file_path}\n\n")

print("Consolidated file generated successfully.")
