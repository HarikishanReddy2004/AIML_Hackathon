import streamlit as st
import time
from gmail_service import get_gmail_service, get_email_details, fetch_emails_after_id
from crew import process_email_with_crew
from storage import (
    save_last_processed_id, get_last_processed_id,
    save_processed_emails, load_processed_emails
)
from ui_styles import get_css_styles
from config import MAX_EMAILS_TO_FETCH

# Page configuration
st.set_page_config(layout="wide", page_title="Loan Servicing Email Processor")

# Initialize session state
if "processed_emails" not in st.session_state:
    try:
        st.session_state["processed_emails"] = load_processed_emails()
    except:
        st.session_state["processed_emails"] = set()

if "email_data" not in st.session_state:
    st.session_state["email_data"] = []

if "last_processed_id" not in st.session_state:
    st.session_state["last_processed_id"] = get_last_processed_id()

if "auto_refresh" not in st.session_state:
    st.session_state["auto_refresh"] = False

# Initialize Gmail service
gmail_service = get_gmail_service()
if not gmail_service:
    st.error("❌ Gmail API authentication failed. Please check your credentials.")
    st.stop()


def fetch_and_process_new_emails():
    """Fetch and process new emails since the last processed email"""
    with st.spinner("📥 Fetching new emails..."):
        email_ids = fetch_emails_after_id(
            gmail_service,
            st.session_state["last_processed_id"],
            MAX_EMAILS_TO_FETCH
        )

        if not email_ids:
            st.info("No new emails found.")
            return

        st.success(f"✅ Found {len(email_ids)} new emails to process.")

        for email_id in email_ids:
            if email_id in st.session_state["processed_emails"]:
                continue

            email_data = get_email_details(gmail_service, email_id)
            if not email_data:
                continue

            result = process_email_with_crew(
                email_data,
                [e["email"] for e in st.session_state["email_data"][-10:]]
            )

            st.session_state["processed_emails"].add(email_id)
            st.session_state["email_data"].insert(0, {"email": email_data, "result": result})
            st.session_state["last_processed_id"] = email_id

            save_last_processed_id(email_id)
            save_processed_emails(st.session_state["processed_emails"])


# UI Header
st.markdown("<h1 style='text-align: center; color: red;'>📩 Email Notifications</h1>", unsafe_allow_html=True)

# CSS Styles
st.markdown(get_css_styles(), unsafe_allow_html=True)

# Control Panel
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Fetch & Process New Emails"):
        fetch_and_process_new_emails()
with col2:
    auto_refresh = st.checkbox("Enable Auto-Refresh", value=st.session_state["auto_refresh"])
    st.session_state["auto_refresh"] = auto_refresh
with col3:
    refresh_interval = st.slider("Refresh Interval (seconds)", 10, 300, 60)

st.divider()

# Table Header
st.markdown(
    """
    <div class="email-row header-row" style="background-color: #ffe5e5;">
        <div style="flex: 3; color: red;"><b>Email Subject</b></div>
        <div style="flex: 2; color: red;"><b>Request Type</b></div>
        <div style="flex: 2; color: red;"><b>Sub Request Type</b></div>
        <div style="flex: 2; color: red;"><b>Confidence</b></div>
        <div style="flex: 2; text-align: center; color: red;"><b>Actions</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Display emails in rows
for item in st.session_state["email_data"]:
    email = item["email"]
    result = item["result"]
    if not result:
        continue

    confidence = result["classification"].confidence_score
    primary_type = result["classification"].primary_request_type
    sub_type = result["classification"].sub_request_type or ""

    with st.expander(f"📧 {email['subject']}", expanded=False):
        st.write(f"**Date:** {email['date']}")
        st.write(f"**From:** {email['from']}")
        st.write(f"**Full Email:**\n{email['full_body']}")

    col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 2])

    col1.text(email['subject'])
    col2.text_input("Request Type", value=primary_type)
    col3.text_input("Sub Request Type", value=sub_type)
    col4.text(f"{confidence:.2f}")

    with col5:
        btn_col1, btn_col2 = st.columns(2)  # Create two columns for buttons
        with btn_col1:
            st.button("✅", key=f"approve_{email['subject']}")
        with btn_col2:
            st.button("✏️", key=f"edit_{email['subject']}")

# Auto-refresh logic
if st.session_state["auto_refresh"]:
    time.sleep(refresh_interval)
    fetch_and_process_new_emails()
    st.rerun()

# Footer
st.markdown("---")
st.markdown(f"**Total emails processed:** {len(st.session_state['processed_emails'])}")
if st.session_state["last_processed_id"]:
    st.markdown(f"**Last processed email ID:** {st.session_state['last_processed_id']}")
