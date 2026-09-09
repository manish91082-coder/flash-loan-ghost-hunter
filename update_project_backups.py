import os
import sys
import shutil

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base_dir = os.path.dirname(os.path.abspath(__file__))
v2_backup = os.path.join(base_dir, "backup_v2_mvp")
v3_backup = os.path.join(base_dir, "backup_v3_universal")

files_to_copy = [
    "auto_tuner_engine.py",
    "prevent_sleep.py",
    "run_247_continuous_shadow_engine.py",
    "PROJECT_LIVE.md"
]

os.makedirs(v2_backup, exist_ok=True)
os.makedirs(v3_backup, exist_ok=True)

for f in files_to_copy:
    src = os.path.join(base_dir, f)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(v2_backup, f))
        shutil.copy(src, os.path.join(v3_backup, f))
        print(f"✅ Backup updated for {f}")

print("🎉 Backups v2 and v3 updated successfully!")
