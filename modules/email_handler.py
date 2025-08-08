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

# النطاقات التي سيطلبها البرنامج. إذا قمت بتعديلها، يجب حذف ملف token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """
    يقوم بمصادقة المستخدم مع Gmail API وإرجاع كائن الخدمة.
    """
    creds = None
    # ملف token.json يخزن رموز الوصول الخاصة بالمستخدم ويتم إنشاؤه
    # تلقائياً عند إكمال عملية المصادقة لأول مرة.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # إذا لم تكن هناك بيانات اعتماد صالحة، اسمح للمستخدم بتسجيل الدخول.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # تأكد من وجود ملف credentials.json الذي قمت بتنزيله من Google Cloud
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("Error: 'credentials.json' not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # حفظ بيانات الاعتماد للتشغيلات القادمة
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
    ينشئ رسالة بريد إلكتروني مع مرفق.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, 'plain')
    message.attach(msg)

    # التعامل مع المرفق
    try:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={os.path.basename(file_path)}',
        )
        message.attach(part)
    except FileNotFoundError:
        print(f"Error: Attachment file not found at {file_path}")
        return None

    # تحويل الرسالة إلى الصيغة التي تتطلبها Gmail API
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """
    يرسل رسالة بريد إلكتروني باستخدام Gmail API.
    """
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {sent_message['id']} sent successfully.")
        return True
    except HttpError as error:
        print(f'An error occurred during sending: {error}')
        return False
