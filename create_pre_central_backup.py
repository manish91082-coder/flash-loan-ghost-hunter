import os
import sys
import zipfile
import time

sys.stdout.reconfigure(encoding="utf-8")

def create_full_backup(source_dir, output_zip):
    print(f"📦 Creating zero-data-loss backup archive: {output_zip}")
    start_time = time.time()
    file_count = 0
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip caches, git, and virtualenvs to keep backup clean and fast
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', 'htmlcov']]
            
            for file in files:
                # Do not zip zip files themselves or sensitive token files
                if file.endswith('.zip') or file == 'token.json':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                file_count += 1
                
    elapsed = time.time() - start_time
    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"✅ Successfully created: {output_zip}")
    print(f"📊 Files Archived: {file_count:,} | Archive Size: {size_mb:.2f} MB | Time Taken: {elapsed:.2f}s")

if __name__ == "__main__":
    project_dir = os.path.abspath(os.path.dirname(__file__))
    output_zip_file = os.path.join(project_dir, "PhantomX_CentralStream_PreBackup.zip")
    create_full_backup(project_dir, output_zip_file)
