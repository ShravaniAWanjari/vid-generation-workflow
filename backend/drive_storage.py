"""
drive_storage.py - Handles project asset storage via Google Drive API.
"""

import io
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service(credentials_path: str = 'credentials.json'):
    """Authenticates securely using a local service account credentials JSON file or env var."""
    env_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if env_creds:
        creds_info = json.loads(env_creds)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=SCOPES)
            
    service = build('drive', 'v3', credentials=creds)
    return service

def get_or_create_folder(service, folder_name: str, parent_id: str = None) -> str:
    """Finds a folder by name (and optionally parent), creating it if it doesn't exist."""
    # Escape single quotes in folder name for the query
    safe_name = folder_name.replace("'", "\\'")
    query = f"name='{safe_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    
    if parent_id:
        query += f" and '{parent_id}' in parents"
        
    results = service.files().list(
        q=query, spaces='drive', fields='files(id, name)',
        supportsAllDrives=True, includeItemsFromAllDrives=True
    ).execute()
    items = results.get('files', [])
    
    if not items:
        # Folder doesn't exist, create it
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
            
        folder = service.files().create(
            body=folder_metadata, fields='id', supportsAllDrives=True
        ).execute()
        return folder.get('id')
    
    return items[0].get('id')

def upload_production_render(video_binary_stream: bytes, client_name: str, project_name: str) -> dict:
    """
    Uploads a production render to Google Drive in the specified client folder,
    makes it publicly readable, and returns the shareable link and file ID.
    """
    service = get_drive_service()
    
    # 1. Ensure main parent folder exists (from env var or create it by name)
    main_folder_id = os.getenv("GOOGLE_PARENT_FOLDER_ID")
    if not main_folder_id:
        main_folder_id = get_or_create_folder(service, 'Naturo_Studio_Archive')
    
    # 2. Ensure specific client folder exists within the main parent
    client_folder_id = get_or_create_folder(service, client_name, main_folder_id)
    
    # 3. Upload the raw binary video stream into the client folder
    file_metadata = {
        'name': f"{project_name}_Render.mp4",
        'parents': [client_folder_id]
    }
    
    # Wrap bytes in a BytesIO object so MediaIoBaseUpload can read it like a file
    fh = io.BytesIO(video_binary_stream)
    media = MediaIoBaseUpload(fh, mimetype='video/mp4', resumable=True)
    
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink',
        supportsAllDrives=True
    ).execute()
    
    file_id = uploaded_file.get('id')
    webview_link = uploaded_file.get('webViewLink')
    
    # 4. Update file's permissions to make it readable by anyone with the link
    permission_body = {
        'role': 'reader',
        'type': 'anyone'
    }
    
    service.permissions().create(
        fileId=file_id,
        body=permission_body,
        supportsAllDrives=True
    ).execute()
    
    # 5. Fetch and return direct, shareable web viewing link and the Google Drive File ID
    # Note: we already requested `webViewLink` in the create call
    return {
        'file_id': file_id,
        'webViewLink': webview_link
    }
