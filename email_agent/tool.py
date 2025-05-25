from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, List

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


def fetch_lastest_emails(max_results=10, after=None, before=None) -> list:
    """
    Fetches the most recent emails from the inbox using the Gmail API, optionally within a date range.

    Args:
        max_results (int): Number of recent emails to fetch.
        after (str): Fetch emails after this (YYYY/MM/DD or unix timestamp).
        before (str): Fetch emails before this (YYYY/MM/DD or unix timestamp).

    Returns:
        list: a list of dicts with email details (sender, subject, date, snippet).
    """
    try:
        service = get_gmail_service()
        query = ""
        if after:
            query += f"after:{after} "
        if before:
            query += f"before:{before} "
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            maxResults=max_results,
            q=query.strip() if query else None
        ).execute()
        messages = results.get('messages', [])
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            email_info = {
                'snippet': msg_data.get('snippet', ''),
                'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), None),
                'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), None),
                'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), None),
                'id': msg['id']
            }
            output.append(email_info)
        return output
    except HttpError as error:
        return f"An error occurred: {error}"

def send_email(to, subject, body):
    """
    Sends an email using the Gmail API.

    Args:
        to (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body text.

    Returns:
        dict: The sent message metadata or error message.
    """
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw}
        sent_message = service.users().messages().send(userId='me', body=message_body).execute()
        return sent_message
    except HttpError as error:
        return f"An error occurred: {error}"

def search_emails(
    max_results: int = 10,
    keyword: Optional[str] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    after: Optional[datetime] = None,
    before: Optional[datetime] = None
) -> List[dict]:
    '''
    Search Gmail messages using the Gmail API with optional filters and return full email content.

    This function constructs a Gmail search query based on the provided parameters and retrieves matching emails using the Gmail API. It returns a list of email metadata including sender, subject, date, and the plain text body of the message.

    Parameters:
    max_results (int): Maximum number of emails to return.
    keyword (str, optional): Keyword to search in email content.
    sender (str, optional): Filter by sender email address.
    subject (str, optional): Filter by subject line.
    after (datetime, optional): Filter emails sent after this (YYYY/MM/DD or unix timestamp).
    before (datetime, optional): Filter emails sent before this (YYYY/MM/DD or unix timestamp).
    Returns:

    List[dict]: A list of emails, each represented as a dictionary
'''
    # Build the Gmail API service
    try:
        service = get_gmail_service()

        # Construct the search query
        query_parts = []
        if keyword:
            query_parts.append(keyword)
        if sender:
            query_parts.append(f"from:{sender}")
        if subject:
            query_parts.append(f"subject:{subject}")
        if after:
            query_parts.append(f"after:{after.strftime('%Y/%m/%d')}")
        if before:
            query_parts.append(f"before:{before.strftime('%Y/%m/%d')}")
        query = ' '.join(query_parts)

        # Search for messages
        results = service.users().messages().list(userId='me', q=query,maxResults=max_results).execute()
        messages = results.get('messages', [])
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            email_info = {
                'snippet': msg_data.get('snippet', ''),
                'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), None),
                'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), None),
                'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), None),
                'id': msg['id']
            }
            output.append(email_info)
        return output
    except HttpError as error:
        return f"An error occurred: {error}"

def set_auto_reply(
    enable: bool,
    subject: str,
    message: str,
    start_time: int = 0,
    end_time: int = 0
):
    """
    Sets up or disale an automatic reply (vacation responder) in Gmail.

    Parameters:
        enable (bool): Whether to enable or disable the auto-reply.
        subject (str): Subject line of the auto-reply email.
        message (str): Body of the auto-reply email.
        start_time (int): Start time in milliseconds since epoch (optional).
        end_time (int): End time in milliseconds since epoch (optional).
    """
    service = get_gmail_service()
    vacation_settings = {
        'enableAutoReply': enable,
        'responseSubject': subject,
        'responseBodyPlainText': message,
        'restrictToContacts': False,
        'restrictToDomain': False,
        'startTime': start_time,
        'endTime': end_time
    }

    result = service.users().settings().updateVacation(
        userId='me',
        body=vacation_settings
    ).execute()

    return result

def download_attachments(message_id: str, download_dir: str = "./attachments"):
    """
    Downloads all attachments from a Gmail message.

    Parameters:
        message_id (str): The ID of the Gmail message to extract attachments from.
        download_dir (str): Directory to save the attachments.

    Returns:
        List[str]: List of file paths to the downloaded attachments.
    """
    service = get_gmail_service()
    message = service.users().messages().get(userId='me', id=message_id).execute()

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    attachments = []

    for part in message['payload'].get('parts', []):
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and "attachmentId" in body:
            attachment_id = body["attachmentId"]
            attachment = service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            file_path = os.path.join(download_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_data)
            attachments.append(file_path)

    return attachments

def reply_email(message_id: str, reply_text: str):
    """
    Replies to a Gmail message using the Gmail API.

    Parameters:
        message_id (str): The ID of the Gmail message to reply to.
        reply_text (str): The body of the reply message.

    Returns:
        dict: Metadata of the sent reply message.
    """
    service = get_gmail_service

    # Fetch the original message metadata
    original = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
    headers = {h['name']: h['value'] for h in original['payload']['headers']}
    to = headers.get('From')
    subject = headers.get('Subject')
    thread_id = original['threadId']
    in_reply_to = headers.get('Message-ID')

    # Create MIME reply message
    message = MIMEText(reply_text)
    message['to'] = to
    message['subject'] = f"Re: {subject}"
    message['In-Reply-To'] = in_reply_to
    message['References'] = in_reply_to
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the reply
    reply = {
        'raw': raw_message,
        'threadId': thread_id
    }
    sent = service.users().messages().send(userId='me', body=reply).execute()
    return sent


if __name__ == "__main__":
    # temp = check_emails(max_results=20, after="2025/01/01", before="2025/02/01")
    temp = search_emails(max_results=5, keyword="microsoft")
    print(len(temp))
    print(temp)
    # result = send_email("wenhaos@umich.edu", "Test Subject", "Hello from Gmail API!")
    # print(result)