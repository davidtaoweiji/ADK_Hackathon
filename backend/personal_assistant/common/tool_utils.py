from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os


def get_google_service(
    service_name,
    version="v1",
    scopes=None,
    token_file="token.json",
    credentials_file="credentials.json",
):
    """
    Returns a Google API service client for the specified service.
    """
    creds = None
    if scopes is None:
        raise ValueError("Scopes must be provided")
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return build(service_name, version, credentials=creds)
