from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, List
from personal_assistant.common.tool_utils import get_google_service
import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_gmail_service():
    return get_google_service(service_name="gmail", version="v1", scopes=SCOPES)


def fetch_lastest_emails(
    max_results: int, after: Optional[str] = None, before: Optional[str] = None
) -> list:
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
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                labelIds=["INBOX"],
                maxResults=max_results,
                q=query.strip() if query else None,
            )
            .execute()
        )
        messages = results.get("messages", [])
        output = []
        for msg in messages:
            msg_data = (
                service.users().messages().get(userId="me", id=msg["id"]).execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])
            email_info = {
                "snippet": msg_data.get("snippet", ""),
                "from": next(
                    (h["value"] for h in headers if h["name"].lower() == "from"), None
                ),
                "subject": next(
                    (h["value"] for h in headers if h["name"].lower() == "subject"),
                    None,
                ),
                "date": next(
                    (h["value"] for h in headers if h["name"].lower() == "date"), None
                ),
                "id": msg["id"],
            }
            output.append(email_info)
        print(f"Fetched {len(output)} emails.")
        return output
    except HttpError as error:
        return f"An error occurred: {error}"


def send_email(to: str, subject: str, body: str) -> dict:
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
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {"raw": raw}
        sent_message = (
            service.users().messages().send(userId="me", body=message_body).execute()
        )
        return sent_message
    except HttpError as error:
        return f"An error occurred: {error}"


def search_emails(
    max_results: int,
    keyword: Optional[str] = None,
    sender: Optional[str] = None,
    subject: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
) -> List[dict]:
    """
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
    """
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
        query = " ".join(query_parts)

        # Search for messages
        results = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])
        output = []
        for msg in messages:
            msg_data = (
                service.users().messages().get(userId="me", id=msg["id"]).execute()
            )
            headers = msg_data.get("payload", {}).get("headers", [])
            email_info = {
                "snippet": msg_data.get("snippet", ""),
                "from": next(
                    (h["value"] for h in headers if h["name"].lower() == "from"), None
                ),
                "subject": next(
                    (h["value"] for h in headers if h["name"].lower() == "subject"),
                    None,
                ),
                "date": next(
                    (h["value"] for h in headers if h["name"].lower() == "date"), None
                ),
                "id": msg["id"],
            }
            output.append(email_info)
        return output
    except HttpError as error:
        return f"An error occurred: {error}"


def set_auto_reply(
    enable: bool, subject: str, message: str, start_time: int, end_time: int
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
        "enableAutoReply": enable,
        "responseSubject": subject,
        "responseBodyPlainText": message,
        "restrictToContacts": False,
        "restrictToDomain": False,
        "startTime": start_time,
        "endTime": end_time,
    }

    result = (
        service.users()
        .settings()
        .updateVacation(userId="me", body=vacation_settings)
        .execute()
    )

    return result


def download_attachments(message_id: str):
    """
    Downloads all attachments from a Gmail message.

    Parameters:
        message_id (str): The ID of the Gmail message to extract attachments from.

    Returns:
        List[str]: List of file paths to the downloaded attachments.
    """
    service = get_gmail_service()
    message = service.users().messages().get(userId="me", id=message_id).execute()
    download_dir: str = "./attachments"
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    attachments = []

    for part in message["payload"].get("parts", []):
        filename = part.get("filename")
        body = part.get("body", {})
        if filename and "attachmentId" in body:
            attachment_id = body["attachmentId"]
            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            file_data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
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
    service = get_gmail_service()

    # Fetch the original message metadata
    original = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="metadata")
        .execute()
    )
    headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
    to = headers.get("From")
    subject = headers.get("Subject")
    thread_id = original["threadId"]
    in_reply_to = headers.get("Message-ID")

    # Create MIME reply message
    message = MIMEText(reply_text)
    message["to"] = to
    message["subject"] = f"Re: {subject}"
    message["In-Reply-To"] = in_reply_to
    message["References"] = in_reply_to
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Send the reply
    reply = {"raw": raw_message, "threadId": thread_id}
    sent = service.users().messages().send(userId="me", body=reply).execute()
    return sent


def mark_email(message_ids, read: Optional[str] = None, starred: Optional[str] = None):
    """
    Marks Gmail messages as read/unread or starred/unstarred.

    This function modifies the labels of one or more Gmail messages to update their read or starred status.
    You can use it to mark messages as read, unread, starred, or unstarred by specifying the appropriate flags.

    Parameters:
        message_ids (List[str]): A list of Gmail message IDs to modify.
        read (bool, optional):
            - True to mark messages as read.
            - False to mark messages as unread.
            - None to leave read status unchanged.
        starred (bool, optional):
            - True to add the "STARRED" label.
            - False to remove the "STARRED" label.
            - None to leave starred status unchanged.

    Returns:
        None
    """

    service = get_gmail_service
    labels_to_add = []
    labels_to_remove = []

    if read is not None:
        if read:
            labels_to_remove.append("UNREAD")
        else:
            labels_to_add.append("UNREAD")

    if starred is not None:
        if starred:
            labels_to_add.append("STARRED")
        else:
            labels_to_remove.append("STARRED")

    for msg_id in message_ids:
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"addLabelIds": labels_to_add, "removeLabelIds": labels_to_remove},
        ).execute()
