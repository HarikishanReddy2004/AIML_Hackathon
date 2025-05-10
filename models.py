from pydantic import BaseModel, Field
from typing import Optional, List


class ClassificationResult(BaseModel):
    primary_request_type: str
    sub_request_type: Optional[str] = None
    confidence_score: float
    additional_request_types: Optional[List[str]] = None
    reason: Optional[str] = None


class ExtractionResult(BaseModel):
    request_type: str
    deal_name: str
    borrower: str
    amount: Optional[float] = None
    payment_date: Optional[str] = None
    transaction_reference: Optional[str] = None


class DuplicateCheckResult(BaseModel):
    duplicate_flag: bool
    duplicate_reason: str


class ProcessedEmail(BaseModel):
    email_id: str
    subject: str
    sender: str
    date: str
    body: str
    snippet: str
    classification: Optional[ClassificationResult] = None
    extraction: Optional[ExtractionResult] = None
    is_processed: bool = False