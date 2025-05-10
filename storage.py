# storage.py - Data persistence functions
import json
import os
import pickle

LAST_PROCESSED_ID_FILE = "last_processed_id.txt"
PROCESSED_EMAILS_FILE = "processed_emails.pickle"

def save_last_processed_id(email_id):
    """Save the ID of the last processed email"""
    with open(LAST_PROCESSED_ID_FILE, "w") as f:
        f.write(email_id)

def get_last_processed_id():
    """Get the ID of the last processed email"""
    if not os.path.exists(LAST_PROCESSED_ID_FILE):
        return None
    with open(LAST_PROCESSED_ID_FILE, "r") as f:
        return f.read().strip() or None

def save_processed_emails(processed_emails):
    """Save the set of processed email IDs"""
    with open(PROCESSED_EMAILS_FILE, "wb") as f:
        pickle.dump(processed_emails, f)

def load_processed_emails():
    """Load the set of processed email IDs"""
    if not os.path.exists(PROCESSED_EMAILS_FILE):
        return set()
    with open(PROCESSED_EMAILS_FILE, "rb") as f:
        return pickle.load(f)

def save_email_data(email_data):
    """Save processed email data to a JSON file"""
    email_id = email_data["email"]["id"]
    filename = f"email_data_{email_id}.json"
    with open(filename, "w") as f:
        json.dump(email_data, f)