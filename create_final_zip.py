import os
import zipfile

def create_full_backup(source_dir, output_zip):
    print(f"Creating zero-data-loss backup archive: {output_zip}")
    print("This may take a few moments as it is packing all databases, AI models, logs, and matrices...")
    
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # Skip massive caches to ensure clean zip but preserve ALL project data
            if '__pycache__' in root or '.pytest_cache' in root:
                continue
            
            for file in files:
                # Do not zip the zip file itself or token files
                if file.endswith('.zip') or file == 'token.json':
                    continue
                
                file_path = os.path.join(root, file)
                # The arcname is the path inside the zip file relative to the source dir
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
                
    print(f"Successfully created: {output_zip}")
    print("You can now directly upload this single file to your Google Drive.")

if __name__ == "__main__":
    project_directory = r"c:\Users\Admin\.gemini\antigravity-ide\scratch\flash loan ghost hunter"
    output_zip_file = os.path.join(project_directory, "PhantomX_Ultimate_Backup_v1.zip")
    
    create_full_backup(project_directory, output_zip_file)
