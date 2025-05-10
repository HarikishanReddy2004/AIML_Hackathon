# gmail_service.py - Gmail API integration
import os
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import CREDENTIALS_FILE


def get_gmail_service():
    """Initialize and return Gmail API service"""
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE)
        return build("gmail", "v1", credentials=creds)
    return None


def extract_email_address(sender):
    """Extract email address from sender string"""
    match = re.search(r"<(.*?)>", sender)
    return match.group(1) if match else sender


def get_email_body(payload):
    """Recursively extract email body from nested parts"""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
            elif part["mimeType"] == "text/html":
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
            elif "parts" in part:
                return get_email_body(part)  # Recursive call
    elif "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    return "No content available"


def get_email_details(service, message_id):
    """Get detailed information about a specific email"""
    try:
        message = service.users().messages().get(userId="me", id=message_id).execute()
        payload = message["payload"]
        headers = payload["headers"]

        # Extract email metadata
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        sender_email = extract_email_address(sender)
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

        # Get full email body
        body = get_email_body(payload)
        snippet = message.get("snippet", "")

        return {
            "id": message_id,
            "subject": subject,
            "from": sender_email,
            "date": date,
            "full_body": body.strip() if body else "No content available",
            "snippet": snippet
        }
    except Exception as e:
        print(f"Error fetching email details: {e}")
        return None


def fetch_emails_after_id(service, last_processed_id=None, max_results=50):
    """Fetch emails after a specific email ID"""
    if not service:
        return []

    try:
        query = ""
        if last_processed_id:
            # Get timestamp of the last processed email
            last_msg = service.users().messages().get(userId="me", id=last_processed_id).execute()
            last_internal_date = int(last_msg.get('internalDate', 0))
            # Fetch newer emails based on timestamp
            query = f"after:{last_internal_date // 1000}"

        response = service.users().messages().list(
            userId="me",
            maxResults=max_results,
            q=query
        ).execute()

        message_ids = response.get("messages", [])
        return [msg["id"] for msg in message_ids]
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []