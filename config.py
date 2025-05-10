# Configuration settings
import os

# Constants
CREDENTIALS_FILE = "../token.json"
MAX_EMAILS_TO_FETCH = 50  # Increased from 5

# Request types dictionary
REQUEST_TYPES = {
    "Adjustment": [],
    "AU Transfer": [],
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement Inbound": ["Principal", "Interest", "Principal+Interest", "Principal+Interest+Fee"],
    "Money Movement Outbound": ["Timebound", "Foreign Currency"],
}