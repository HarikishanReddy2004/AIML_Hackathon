# crew_agents.py - CrewAI agents and tasks setup
from crewai import Agent, Task, Crew, Process, LLM
from config import REQUEST_TYPES
from models import ClassificationResult, DuplicateCheckResult, ExtractionResult
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="sambanova/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.7
)


def create_agents():
    """Create and return CrewAI agents"""
    classification_agent = Agent(
        role="Email Classifier",
        goal=f"""
        Classify the email into one or more predefined request types and subrequest types.

        """,
        backstory="you are a classification agent",
        llm=llm,
        verbose=True
    )

    extraction_agent = Agent(
        role="Data Extractor",
        goal="Extract structured financial data based on the request type.",
        backstory="you are a data extraction agent",
        llm=llm,
        verbose=True
    )

    duplicate_checker_agent = Agent(
        role="Duplicate Detector",
        goal="Detect duplicate emails and provide a reason if classified as a duplicate.",
        backstory="you are a duplicate detection agent",
        llm=llm,
        verbose=True
    )

    return classification_agent, extraction_agent, duplicate_checker_agent


def create_tasks(classification_agent, extraction_agent, duplicate_checker_agent):
    """Create and return CrewAI tasks"""
    classify_task = Task(
        description='''Identify the request type(s) from the email {email_text} and assign a primary request type if multiple exist.
        Identify the **primary request type** if multiple requests exist.
        Ensure classification accuracy and return a **confidence score**.

        ## Request Types & Sub-Types:
        {REQUEST_TYPES}

        ## Rules for Multi-Intent Emails:
        1. If an email contains multiple request types, detect the **primary request type** based on the **main action required**.  
        2. List **secondary request types** separately.  
        3.  Assign a **confidence score (0-1)** to each classification.  
        4. If unsure, return the **most likely request type** with a confidence score.  
        ''',
        agent=classification_agent,
        output_pydantic=ClassificationResult,
        expected_output="Primary request type, subrequest type, confidence score, additional request types"
    )

    extract_task = Task(
        description="Extract structured loan servicing data from email body {email_text} and attachments.",
        agent=extraction_agent,
        output_pydantic=ExtractionResult,
        expected_output="Extracted feilds"
    )

    duplicate_task = Task(
        description="Check if the email {email_text} is a duplicate based on prior received emails {previous_emails}and provide reason if the email is duplicate.",
        agent=duplicate_checker_agent,
        output_pydantic=DuplicateCheckResult,
        expected_output="Duplicate flag, duplicate reason"
    )

    return classify_task, extract_task, duplicate_task


"""Process an email using CrewAI agents and tasks"""
classification_agent, extraction_agent, duplicate_checker_agent = create_agents()
classify_task, extract_task, duplicate_task = create_tasks(
    classification_agent, extraction_agent, duplicate_checker_agent
)
# Create a crew with the agents and tasks

crew1 = Crew(
    agents=[classification_agent],
    tasks=[classify_task, ],
    process=Process.sequential
)
crew2 = Crew(
    agents=[extraction_agent],
    tasks=[extract_task, ],
    process=Process.sequential
)
crew3 = Crew(
    agents=[duplicate_checker_agent],
    tasks=[duplicate_task, ],
    process=Process.sequential
)


def process_email_with_crew(email_data, previous_emails=None):
    # Add previous emails for duplicate checking if available
    inputs = {
        "email_text": email_data.get("full_body") or email_data.get("snippet", ""),
        "REQUEST_TYPES": REQUEST_TYPES
    }

    if previous_emails:
        inputs["previous_emails"] = previous_emails
    else:
        inputs["previous_emails"] = []

    # Execute the crew
    try:
        response1 = crew1.kickoff(inputs=inputs)
        response2 = crew2.kickoff(inputs=inputs)
        response3 = crew3.kickoff(inputs=inputs)
        response = [response1, response2, response3]
    except Exception as e:
        print(f"Error processing email: {e}")
        return None
    # Process and structure the results
    result = {
        "classification": ClassificationResult(
            primary_request_type=response[0]["primary_request_type"],
            sub_request_type=response[0]["sub_request_type"],
            confidence_score=response[0]["confidence_score"],
            additional_request_types=response[0]["additional_request_types"],
            reason=response[0]["reason"],

        ),
        "extraction": ExtractionResult(
            request_type=response[1]["request_type"] or "Unknown",
            deal_name=response[1]["deal_name"] or "Unknown",
            borrower=response[1]["borrower"] or "Unknown",
            amount=response[1]["amount"],
            payment_date=response[1]["payment_date"],
            transaction_reference=response[1]["transaction_reference"]
        ),
        "duplicate": DuplicateCheckResult(
            duplicate_flag=response[2]["duplicate_flag"],
            duplicate_reason=response[2]["duplicate_reason"]
        )

    }
    print(response)
    print(result)
    return result