import streamlit as st
import time
import os
import base64
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Constants
CREDENTIALS_FILE = "../token.json"
st.set_page_config(layout="wide")
# Load Gmail API service
def get_gmail_service():
    creds = None
    if os.path.exists(CREDENTIALS_FILE):
        creds = Credentials.from_authorized_user_file(CREDENTIALS_FILE)
    else:
        st.error("Missing credentials. Please authenticate with Gmail API.")
        return None

    return build("gmail", "v1", credentials=creds)

gmail_service = get_gmail_service()

if "processed_emails" not in st.session_state:
    st.session_state["processed_emails"] = set()

if "email_data" not in st.session_state:
    st.session_state["email_data"] = []
# Function to fetch recent emails
def fetch_recent_emails(max_results=5):
    if not gmail_service:
        return []
    
    try:
        response = gmail_service.users().messages().list(userId="me", maxResults=max_results).execute()
        emails = []

        for msg in response.get("messages", []):
            if msg["id"] not in st.session_state["processed_emails"]:
                st.session_state["processed_emails"].add(msg["id"])
                email = get_email_details(msg["id"])
                if email:
                    emails.append(email)

        return emails
    except Exception as e:
        st.error(f"Error fetching emails: {e}")
        return []

# Function to recursively extract email body
def get_body(payload):
    """ Recursively extracts email body from nested parts """
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
            elif part["mimeType"] == "text/html":
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
            elif "parts" in part:
                return get_body(part)  # Recursive call
    elif "body" in payload and "data" in payload["body"]:
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    return "No content available"

# Function to extract only the email address
def extract_email(sender):
    match = re.search(r"<(.*?)>", sender)
    return match.group(1) if match else sender  # Extract email if found

# Function to get email details
def get_email_details(message_id):
    try:
        message = gmail_service.users().messages().get(userId="me", id=message_id).execute()
        payload = message["payload"]
        headers = payload["headers"]

        # Extract email metadata
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        sender_email = extract_email(sender)  # Extract only the email
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")

        # Extract email body using the recursive function
        body = get_body(payload)

        return {
            "id": message_id,
            "subject": subject,
            "from": sender_email,  # Use only the extracted email
            "date": date,
            "full_body": body.strip() if body else "No content available"
        }
    except Exception as e:
        st.error(f"Error fetching email details: {e}")
        return None

# Streamlit UI
st.markdown("<h1 style='text-align: center; color: red;'>📩 EMAIL NOTIFICATIONS</h1>", unsafe_allow_html=True)

# CSS Styling
st.markdown(
    """
    <style>
        .full-width-container {
            width: 100%;
            margin: 0;
            padding: 10px;
            background-color: yellow;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        .email-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            padding: 10px;
            border-bottom: 2px solid red;
            background-color: white;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        .email-subject {
            flex: 3;
            color: black;
            font-weight: bold;
        }
        .input-box {
            flex: 2;
            padding: 5px;
        }
        .action-buttons {
            flex: 2;
            display: flex;
            gap: 5px;
            justify-content: center;
        }
        .accept-btn, .edit-btn {
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            text-align: center;
        }
        .accept-btn {
            background-color: red;
            color: white;
        }
        .edit-btn {
            background-color: yellow;
            color: black;
        }
        details {
            width: 100%;
        }
        summary {
            cursor: pointer;
            list-style: none;
            font-size: 16px;
        }
        summary::marker {
            display: none;
        }
        summary::before {
            content: "▶ ";
            font-size: 14px;
            color: red;
        }
        details[open] summary::before {
            content: "▼ ";
            color: red;
        }
    </style>
    <div class="full-width-container">
    """,
    unsafe_allow_html=True
)

# Header Row
st.markdown(
    """
    <div class="email-row" style="font-weight: bold; background-color: red; color: white;">
        <div style="flex: 3;">Email Subject</div>
        <div style="flex: 2;">Request</div>
        <div style="flex: 2;">Sub Request</div>
        <div style="flex: 2;">Stream</div>
        <div style="flex: 2; text-align: center;">Actions</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Fetch and display emails
if "emails" not in st.session_state:
    st.session_state["emails"] = fetch_recent_emails()

for idx, email in enumerate(st.session_state["emails"]):
    st.markdown(
        f"""
        <div class="email-row">
            <div class="email-subject">
                <details>
                    <summary>{email['subject']}</summary>
                    <p><strong>Date:</strong> {email['date']}</p>
                    <p><strong>From:</strong> <span>{email['from']}</span></p>
                    <p><strong>Full Email:</strong> {email['full_body']}</p>
                </details>
            </div>
            <div class="input-box"><input type="text" placeholder="Request Type" style="width: 100%;"></div>
            <div class="input-box"><input type="text" placeholder="Sub Request Type" style="width: 100%;"></div>
            <div class="input-box"><input type="text" placeholder="Stream" style="width: 100%;"></div>
            <div class="action-buttons">
                <button class="accept-btn">Accept</button>
                <button class="edit-btn">Edit</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Close full-width container
st.markdown("</div>", unsafe_allow_html=True)

# Auto-refresh
time.sleep(10)#
st.rerun()
