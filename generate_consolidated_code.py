import os

files_to_merge = [
    "execution/intent.py",
    "execution/pipeline.py",
    "data/live_chain_verifier.py",
    "economics/profit_calculator.py",
    "execution/lifecycle.py",
    "risk/auditor.py"
]

output_file = "PFLC-5.4R_Consolidated_Code.md"

with open(output_file, "w", encoding="utf-8") as outfile:
    outfile.write("# PFLC-5.4R FINAL GOLDEN SLICE CONSOLIDATED CODE\n\n")
    outfile.write("This document contains all source files modified during the PFLC-5.4R execution phase.\n\n")
    
    for filepath in files_to_merge:
        outfile.write(f"## File: `{filepath}`\n\n")
        outfile.write("```python\n")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
        else:
            outfile.write(f"# ERROR: {filepath} not found.\n")
        outfile.write("\n```\n\n")

print(f"Successfully generated {output_file}")
