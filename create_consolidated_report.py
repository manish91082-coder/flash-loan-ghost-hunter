import os

files_to_bundle = [
    "config/chains.json",
    "execution/intent.py",
    "economics/flash_loan.py",
    "economics/profit_calculator.py",
    "risk/mev.py",
    "execution/lifecycle.py"
]

report_path = "PFLC-REAL-MISSION-3.0-CODE-MODIFICATIONS.md"

with open(report_path, "w") as f_out:
    f_out.write("# PFLC-REAL-MISSION-3.0 Code Modifications\n\n")
    for file_path in files_to_bundle:
        if os.path.exists(file_path):
            with open(file_path, "r") as f_in:
                content = f_in.read()
            f_out.write(f"## File: `{os.path.basename(file_path)}`\n")
            f_out.write(f"Path: `{file_path}`\n")
            ext = os.path.splitext(file_path)[1][1:]
            if ext == "":
                ext = "text"
            f_out.write(f"```{ext}\n")
            f_out.write(content)
            f_out.write(f"\n```\n\n")
        else:
            f_out.write(f"## File: `{os.path.basename(file_path)}`\n")
            f_out.write(f"Path: `{file_path}`\n")
            f_out.write(f"> File not found.\n\n")

print(f"Report generated at {report_path}")
