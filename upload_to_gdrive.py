import os
import io
import zipfile
import sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']
TARGET_EMAIL = 'manish91082@gmail.com'

def zip_project_folder(source_dir, output_zip):
    print(f"Zipping project folder (Zero Data Loss Backup)...")
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            if '__pycache__' in root or '.pytest_cache' in root:
                continue
            for file in files:
                if file.endswith('.zip') or file == 'token.json':
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    print("Project successfully zipped.")

def authenticate_gdrive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("=====================================================")
                print("CRITICAL ERROR: 'credentials.json' is missing.")
                print("Google Drive API requires a Client Secret to authenticate.")
                print("Please go to https://console.cloud.google.com/, create OAuth 2.0 Credentials,")
                print("download the JSON, name it 'credentials.json', and place it in this folder.")
                print("Then tell the AI to re-run the script.")
                print("=====================================================")
                sys.exit(1)
            print(f"Opening browser for Google Drive Authentication. Please login with: {TARGET_EMAIL}")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def create_gdrive_folder(service, folder_name, parent_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    
    file = service.files().create(body=file_metadata, fields='id').execute()
    print(f"Created Folder '{folder_name}' on Google Drive")
    return file.get('id')

def upload_file(service, filepath, parent_id, mimetype=None):
    filename = os.path.basename(filepath)
    file_metadata = {'name': filename, 'parents': [parent_id]}
    media = MediaFileUpload(filepath, mimetype=mimetype, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Uploaded: {filename}")

def main():
    service = authenticate_gdrive()
    if not service:
        return

    project_dir = os.path.abspath(".")
    zip_path = os.path.join(project_dir, "PhantomX_Full_Source_Backup.zip")
    zip_project_folder(project_dir, zip_path)

    print("Creating Google Drive folders...")
    root_folder_id = create_gdrive_folder(service, "PhantomX_Project_Backup")

    print("Uploading Full Project Archive to Google Drive...")
    upload_file(service, zip_path, root_folder_id, mimetype='application/zip')

    docs_folder_id = create_gdrive_folder(service, "Master_Documentation_Files", parent_id=root_folder_id)

    print("Uploading 10 Master Documentation Files (with embedded code)...")
    docs_dir = os.path.join(project_dir, "PhantomX_10_Master_Files")
    for file in sorted(os.listdir(docs_dir)):
        if file.endswith(".md"):
            filepath = os.path.join(docs_dir, file)
            upload_file(service, filepath, docs_folder_id, mimetype='text/markdown')

    print("ALL TASKS COMPLETED. PhantomX is fully backed up to Google Drive.")

if __name__ == '__main__':
    main()
