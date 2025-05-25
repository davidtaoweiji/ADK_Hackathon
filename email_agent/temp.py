# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.oauth2.credentials import Credentials
# import os
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# def get_credentials():
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     return creds

# creds = get_credentials()
import os
from functools import wraps
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from adk import Agent, Tool

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

def gmail_auth(func):
    """
    Decorator to handle Gmail API authentication and inject the service object.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
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
        service = build('gmail', 'v1', credentials=creds)
        return func(service, *args, **kwargs)
    return wrapper


def check_emails(service, max_results=5):
    """
    Fetches the most recent emails using the Gmail API.

    Args:
        service: Authenticated Gmail API service instance.
        max_results (int): Number of recent emails to fetch.

    Returns:
        str: A formatted string of email snippets.
    """
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get('messages', [])
        output = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg_data.get('snippet', '')
            output.append(snippet)
        return "\n\n".join(output)
    except HttpError as error:
        return f"An error occurred: {error}"


def send_email(service, to, subject, body):
    """
    Sends an email using the Gmail API.

    Args:
        service: Authenticated Gmail API service instance.
        to (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email body content.

    Returns:
        str: Status message.
    """
    from email.mime.text import MIMEText
    import base64

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        return f"Email sent successfully. Message ID: {message['id']}"
    except HttpError as error:
        return f"An error occurred: {error}"

class GmailFetchTool(Tool):
    def run(self, input_text: str) -> str:
        return fetch_recent_emails()

email_agent = Agent(
    name="EmailAgent",
    tools=[GmailFetchTool()],
    system_instruction="You are an assistant that reads recent emails and summarizes them."
)

if __name__ == "__main__":
    print(email_agent.run("Check my latest emails"))


