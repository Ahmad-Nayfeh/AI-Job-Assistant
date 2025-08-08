import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    # (This function remains the same, no changes needed)
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Error: 'credentials.json' not found.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        print("Gmail service created successfully.")
        return service
    except HttpError as error:
        print(f'An error occurred while creating Gmail service: {error}')
        return None

def create_message_with_attachment(sender, to, subject, message_text, file_path):
    """
    Creates an email message with an attachment, specifying the body as HTML.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # --- THIS IS THE ONLY CHANGE ---
    # We now specify 'html' instead of 'plain' to render the email correctly.
    msg = MIMEText(message_text, 'html')
    # --- END OF CHANGE ---

    message.attach(msg)

    try:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        message.attach(part)
    except FileNotFoundError:
        print(f"Error: Attachment file not found at {file_path}")
        return None

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    # (This function remains the same, no changes needed)
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {sent_message['id']} sent successfully.")
        return True
    except HttpError as error:
        print(f'An error occurred during sending: {error}')
        return False
