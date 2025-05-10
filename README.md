# Problem Statement :

Commercial Bank Lending Service teams handle a high volume of servicing requests via email, often with attachments. These emails require manual triage by gatekeepers who read, classify request types, extract key details, and assign tasks to the right teams. This process is time-consuming, error-prone, and inefficient, especially at scale.
The challenge is to automate email classification and data extraction using Generative AI (LLMs) to improve accuracy, efficiency, and turnaround time while minimizing manual effort. The solution should classify emails, extract relevant information for service requests, and enable skill-based auto-routing to the appropriate processing teams.

# Solution Proposed :

The proposed solution is an AI-powered email processing system that automates the extraction, classification, and analysis of email content, including attachments. The system fetches emails from a Gmail inbox using the Gmail API, processes the email body along with its attachments (PDFs, images, PowerPoint slides, and Excel sheets), and then performs intelligent classification using LLM’s and GenAI Agents.
To enhance efficiency, the system integrates Optical Character Recognition (OCR) for extracting text from images and scanned PDFs, while libraries like PyMuPDF and Pandas process textual PDFs and Excel sheets. The extracted content is then combined with the email text and passed through a model for categorization and prioritization.Using Retrieval Augmented Generation duplicate documents are figured out.
The architecture ensures scalability by supporting large volumes of emails and attachments while maintaining high processing speed. The uniqueness of the solution lies in its ability to understand email intent holistically by merging structured (Excel, PPT) and unstructured (image, text) data for a unified analysis. The efficiency is maximized by parallel processing and optimized data pipelines, ensuring real-time insights for business decision-making.

# Steps :

# Gmail Authentication & Email Fetching : 

Objective: Connect to the Gmail API, authenticate using OAuth2, and fetch new loan servicing emails.

Step 1: Authenticate Gmail API
●	Uses quickstart.py for initial authentication & token generation.

●	Reads credentials.json to authorize Gmail API.

●	Stores access tokens in token.json for re-authentication.

Step 2: Fetch Unprocessed Emails
●	Connects to Gmail API using get_gmail_service().

●	Fetches emails received after the last processed email.

●	Extracts subject, sender, date, and body content.

●	Uses fetch_emails_after_id() to get email IDs.

# Email Processing (Classification, Duplicate Check, Field Extraction)

 Objective: Process the fetched emails using AI models.
 
Step 3: Extract & Process Email Data
●	Fetches email details using get_email_details().

●	Extracts subject, sender, date, body, and snippet.

●	Uses regex-based function to extract the sender email.

Step 4: Classify Email (CrewAI)
●	Calls CrewAI (process_email_with_crew) to classify the email.There are three different types of agents
	1.Classification Agent
	2.Extraction Agent
	3.Duplicate Email Detection Agent

●	Identifies Request Type, Sub-Request Type, and Confidence Score.

Step 5: Detect Duplicate Emails
●	Marks an email as duplicate if the body text is highly similar .
●	Used RAG approach to find the similarity between the documents .

Step 6: Extract Loan Servicing Data
●	Extracts Borrower Name, Loan Amount, Payment Date .

# Storing Processed Emails

  Objective: Save processed emails for future reference.
  
Step 7: Store Processed Email IDs
●	Saves last processed email ID to prevent duplicate processing.

# Displaying Emails in UI
 Objective: Show emails with classification results in Streamlit UI.

Step 8: Display Processed Emails
●	Shows Subject, Request Type, Sub-Type, Confidence Score.

●	Includes Accept & Edit buttons for manual verification.

# Auto-Refresh & Continuous Processing
 Objective: Enable automatic fetching & processing of new emails.
 
Step 9: Auto-Refresh New Emails
●	Runs every 10-300 seconds based on UI slider.

●	Calls fetch_and_process_new_emails() at intervals.


