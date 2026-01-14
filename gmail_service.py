import os
import base64
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import GMAIL_SCOPES, STATE_FILE

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials.json', GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_unread_emails(service):
    """Fetch unread emails from inbox"""
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages', [])
    return messages

def fetch_email(service, msg_id):
    """Get email details"""
    message = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = message['payload']
    headers = payload.get('headers', [])
    data = {}
    for header in headers:
        if header['name'] == 'From':
            data['from'] = header['value']
        if header['name'] == 'Subject':
            data['subject'] = header['value']
        if header['name'] == 'Date':
            data['date'] = header['value']
    # Email body
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data['body'] = base64.urlsafe_b64decode(part['body']['data']).decode()
    else:
        data['body'] = base64.urlsafe_b64decode(payload['body']['data']).decode()
    return data

def mark_as_read(service, msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_ids": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)
