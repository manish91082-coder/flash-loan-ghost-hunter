"""
PhantomX Backup Updater (update_project_backups_complete.py)
============================================================
Syncs all new/modified live data files to backup folders.
"""
import os
import shutil
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
V2_BACKUP = os.path.join(BASE_DIR, "backup_v2_mvp")
V3_BACKUP = os.path.join(BASE_DIR, "backup_v3_universal")

os.makedirs(V2_BACKUP, exist_ok=True)
os.makedirs(V3_BACKUP, exist_ok=True)

FILES_TO_BACKUP_V2 = [
    "live_price_fetcher.py",
    "live_spread_analyzer.py",
    "run_247_continuous_shadow_engine.py",
    "test_live_data_verification.py",
    "phantomx_v2_realtime_transactions.jsonl",
    "prevent_sleep.py",
]

FILES_TO_BACKUP_V3 = [
    "live_price_fetcher.py",
    "live_spread_analyzer.py",
    "run_247_continuous_shadow_engine.py",
    "test_live_data_verification.py",
    "phantomx_v3_realtime_transactions.jsonl",
    "prevent_sleep.py",
]

def backup_file(src_name, dest_dir, optional=False):
    src = os.path.join(BASE_DIR, src_name)
    if not os.path.exists(src):
        if optional:
            print(f"  [SKIP] {src_name} (not yet created)")
        else:
            print(f"  [WARN] {src_name} not found!")
        return False
    dest = os.path.join(dest_dir, src_name)
    shutil.copy2(src, dest)
    size = os.path.getsize(dest)
    print(f"  [OK] {src_name} -> {os.path.basename(dest_dir)}/ ({size:,} bytes)")
    return True

ts = time.strftime("%Y-%m-%d %H:%M:%S")
print(f"PhantomX Backup Sync — {ts}")
print("=" * 60)

print(f"\n[V2 Backup] -> {V2_BACKUP}")
for f in FILES_TO_BACKUP_V2:
    backup_file(f, V2_BACKUP, optional=(f.endswith('.jsonl')))

print(f"\n[V3 Backup] -> {V3_BACKUP}")
for f in FILES_TO_BACKUP_V3:
    backup_file(f, V3_BACKUP, optional=(f.endswith('.jsonl')))

print(f"\n[Done] Backup sync complete at {time.strftime('%Y-%m-%d %H:%M:%S')}")
