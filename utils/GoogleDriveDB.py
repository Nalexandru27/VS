import os
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from Constants import SERVICE_ACCOUNT_FILE, GOOGLE_DRIVE_FOLDER_ID

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDS_FILE = SERVICE_ACCOUNT_FILE
FOLDER_ID = GOOGLE_DRIVE_FOLDER_ID

def authenticate_google_drive():
    """Autentificare cu Google API folosind Service Account"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
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
    try:
        drive_service = authenticate_google_drive()

        backup_file_name = "backup_" + file_name

        existing_file = get_existing_file(drive_service, file_name)  # companies.db
        existing_backup = get_existing_file(drive_service, backup_file_name)  # backup_companies.db
        
        # Dacă există companies.db, îl redenumim în backup_companies.db
        if existing_file:
            # Dacă există deja un backup_companies.db, îl ștergem (dacă avem permisiuni)
            if existing_backup:
                try:
                    drive_service.files().delete(fileId=existing_backup['id']).execute()
                    print(f"Fișierul {backup_file_name} anterior a fost șters.")
                except Exception as e:
                    print(f"Nu s-a putut șterge backup-ul anterior: {e}")
            
            # Redenumim companies.db actual în backup_companies.db
            try:
                drive_service.files().update(
                    fileId=existing_file['id'],
                    body={"name": backup_file_name}
                ).execute()
                print(f"Fișierul existent {file_name} a fost redenumit în {backup_file_name}.")
            except Exception as e:
                print(f"Nu s-a putut redenumi fișierul existent: {e}")
        
        # Încărcăm noul fișier ca companies.db
        media = MediaFileUpload(file_path, mimetype='application/octet-stream')
        
        file_metadata = {
            'name': file_name,  # companies.db
            'parents': [FOLDER_ID]
        }

        file = drive_service.files().create(media_body=media, body=file_metadata).execute()
        print(f"Noul fișier {file_name} a fost încărcat pe Google Drive în folderul specificat!")
        return file
        
    except Exception as e:
        print(f"Eroare la încărcarea fișierului pe Google Drive: {e}")
        return None

def get_file_id(drive_service, file_name):
    """Caută un fișier după nume în folderul specificat și returnează ID-ul acestuia"""
    query = f"name='{file_name}' and \"{FOLDER_ID}\" in parents and trashed=false"
    print(f"Query folosit pentru căutare: {query}")
    
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        print(f"Rezultate găsite pentru '{file_name}': {len(files)}")
        for file in files:
            print(f"- {file['name']} (ID: {file['id']})")
        
        if not files:
            print(f"Fișierul {file_name} nu a fost găsit în folderul specificat.")
            return None
        
        return files[0]['id']
    except Exception as e:
        print(f"Eroare la căutarea fișierului: {e}")
        return None

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

def list_files_in_folder():
    drive_service = authenticate_google_drive()
    query = f"'{FOLDER_ID}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if not files:
        print("Nu s-a găsit niciun fișier în folderul specificat.")
    else:
        print("Fișiere găsite în folder:")
        for file in files:
            print(f"- {file['name']} (ID: {file['id']})")
    
    return files