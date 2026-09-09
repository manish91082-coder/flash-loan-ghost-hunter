import os

base = r'c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter'
archive_path = os.path.join(base, 'phantomx_full_system_archive.md')

# Get all relevant files
all_files = []
for f in os.listdir(base):
    if os.path.isfile(os.path.join(base, f)) and f != 'phantomx_full_system_archive.md':
        all_files.append(f)

# Sort them alphabetically
all_files.sort()

with open(archive_path, 'w', encoding='utf-8') as out:
    out.write("# PHANTOMX FULL SYSTEM ARCHIVE & FILE HIERARCHY\n\n")
    out.write("## 1. FILE HIERARCHY\n")
    out.write("```text\nflash loan ghost hunter/\n")
    for f in all_files:
        out.write(f"├── {f}\n")
    out.write("```\n\n")
    
    out.write("## 2. FILE CONTENTS (100% Data Preservation)\n\n")
    
    for f in all_files:
        fpath = os.path.join(base, f)
        out.write(f"### File: `{f}`\n")
        ext = f.split('.')[-1]
        lang = ext if ext in ['json', 'py', 'md'] else 'text'
        if lang == 'md': lang = 'markdown'
        
        try:
            with open(fpath, 'r', encoding='utf-8') as infile:
                content = infile.read()
            out.write(f"```{lang}\n{content}\n```\n\n")
            out.write("---\n\n")
        except Exception as e:
            out.write(f"*Error reading file: {e}*\n\n")

# Append to project log
log_path = os.path.join(base, 'project_log.md')
with open(log_path, 'a', encoding='utf-8') as logf:
    logf.write("- **[2026-08-31T18:27:30+05:30]** Generated `phantomx_full_system_archive.md` containing entire file hierarchy and 100% content of all files for zero data loss.\n")

print("Archive Generated.")
