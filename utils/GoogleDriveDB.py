import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from Constants import CLIENT_SECRET_FILE
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']

CREDS_FILE = CLIENT_SECRET_FILE

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

def upload_file_to_drive(file_path, file_name):
    drive_service = authenticate_google_drive()

    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    file_metadata = {'name': file_name}
    file = drive_service.files().create(media_body=media, body=file_metadata).execute()
    print(f"Fișierul {file_name} a fost încărcat pe Google Drive!")
    return file

if __name__ == '__main__':
    db_file_path = 'D:\\Facultate\\An 3\\Licenta\\Lucrare Licenta\\companies.db'
    db_file_name = 'companies.db'

    upload_file_to_drive(db_file_path, db_file_name)