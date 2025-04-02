import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from Constants import CLIENT_SECRET_FILE
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_FILE = CLIENT_SECRET_FILE
FOLDER_ID = "1gb30u_IhDzWrz0dQewB4rTBhvDdZlZgV"

def authenticate_google_drive():
    """Autentificare cu Google API"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def get_existing_file(drive_service, file_name):
    """Caută un fișier după nume în folderul specificat"""
    query = f"name='{file_name}' and \"{FOLDER_ID}\" in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files[0] if files else None

def rename_existing_file(drive_service, file_id, new_name):
    """Redenumește un fișier existent pe Google Drive"""
    updated_metadata = {'name': new_name}
    drive_service.files().update(fileId=file_id, body=updated_metadata).execute()
    print(f"Fișierul existent a fost redenumit ca {new_name}")

def upload_file_to_drive(file_path, file_name):
    drive_service = authenticate_google_drive()

    backup_file_name = "backup_" + file_name

    existing_file = get_existing_file(drive_service, file_name)
    existing_backup = get_existing_file(drive_service, backup_file_name)
    
    if existing_backup:
        drive_service.files().delete(fileId=existing_backup['id']).execute()
        print(f"Previous backup {backup_file_name} was deleted.")

    if existing_file:
        rename_existing_file(drive_service, existing_file['id'], backup_file_name)
        print(f"Existing file {file_name} has been renamed to {backup_file_name}.")

    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }

    file = drive_service.files().create(media_body=media, body=file_metadata).execute()
    print(f"File {file_name} has been uploaded on Google Drive into the specified folder!")
    return file

def get_file_id(drive_service, file_name):
    """Caută un fișier după nume în folderul specificat și returnează ID-ul acestuia"""
    query = f"name='{file_name}' and \"{FOLDER_ID}\" in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print(f"Fișierul {file_name} nu a fost găsit în folderul specificat.")
        return None
    
    return files[0]['id']

def download_file_from_drive(file_name, destination_path):
    """Descarcă un fișier de pe Google Drive în calea specificată"""
    drive_service = authenticate_google_drive()
    
    # Obține ID-ul fișierului
    file_id = get_file_id(drive_service, file_name)
    
    if not file_id:
        return False
    
    # Creează folderele destinație dacă nu există
    os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
    
    # Descarcă fișierul
    request = drive_service.files().get_media(fileId=file_id)
    
    with open(destination_path, 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Descărcare {int(status.progress() * 100)}%.")
    
    print(f"Fișierul {file_name} a fost descărcat cu succes la: {destination_path}")
    return True