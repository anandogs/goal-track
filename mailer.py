import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText
import json

from requests import HTTPError

# Load your service account credentials from environment variable
SERVICE_ACCOUNT_INFO = json.loads(base64.b64decode(os.environ.get('SERVICE_ACCOUNT_FILE')).decode())

SCOPES = os.environ.get('SCOPES').split(',')  
USER_ID = os.environ.get('USER_ID') 


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print(f'Message Id: {message["id"]}')
        return message
    except HTTPError as error:
        print(f'An error occurred: {error}')

def get_service():
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    delegated_creds = creds.with_subject(USER_ID)
    service = build('gmail', 'v1', credentials=delegated_creds)
    return service

def send_mail(message_to_send, receipient):
    # Call the Gmail API
    service = get_service()
    # create mail
    sender = USER_ID
    to = receipient
    subject = "Your Daily Shame Report"
    message_text = message_to_send
    message = create_message(sender, to, subject, message_text)
    # send mail
    send_message(service, USER_ID, message)
    return None
