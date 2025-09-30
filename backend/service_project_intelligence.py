"""
Project Intelligence LLM Service
Handles email classification, data extraction, and intelligent processing
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

from emergentintegrations.llm.chat import LlmChat, UserMessage

from models_project_intelligence import (
    EmailClassification, ProjectExtraction, ContactInfo,
    FinancialInfo, DateInfo, EmailExtractionResult
)

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class ProjectIntelligenceLLM:
    """LLM service for project intelligence processing"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY environment variable is required")
        
        # Classification thresholds
        self.AUTO_COMMIT_THRESHOLD = 0.85
        self.NEEDS_REVIEW_THRESHOLD = 0.6
        
        # Initialize LLM chat instances
        self._classifier_chat = None
        self._extractor_chat = None
    
    def _get_classifier_chat(self) -> LlmChat:
        """Get or create classifier chat instance"""
        if not self._classifier_chat:
            self._classifier_chat = LlmChat(
                api_key=self.api_key,
                session_id="project-classifier",
                system_message="""You are an expert email classifier for a fire protection contracting company (Rhino Fire Protection). 

Classify emails into these categories:
- lead_rfp: RFP, bid opportunities, new project leads
- addendum: Project addendums, specification changes
- award: Project awards, contract notifications
- notice_to_proceed: Notice to proceed, start work orders
- change_order: Change orders, scope modifications  
- inspection: Inspection notifications, scheduling
- permit_portal_msg: Permit portal messages, AHJ communications
- pay_app_or_remittance: Payment applications, remittance advice
- shipment_or_quote: Material shipments, quotes, procurement
- schedule_update: Schedule changes, timeline updates
- invoice: Invoices from vendors/suppliers
- payment_confirmation: Payment confirmations, receipts
- progress_update: Progress reports, milestone updates
- general_correspondence: General business correspondence

Return only valid JSON with 'label', 'confidence' (0.0-1.0), and 'reasoning' fields.
Be conservative with confidence scores. Only use >0.85 for very clear cases."""
            ).with_model("openai", "gpt-4o")
        return self._classifier_chat
    
    def _get_extractor_chat(self) -> LlmChat:
        """Get or create extractor chat instance"""
        if not self._extractor_chat:
            self._extractor_chat = LlmChat(
                api_key=self.api_key,
                session_id="project-extractor",
                system_message="""You are an expert data extractor for fire protection project management.

Extract structured data from emails with these guidelines:
1. Be literal - don't infer T&M unless explicitly stated
2. Return null for unknown values - don't guess
3. For billing_type: only use "TM" if Time & Material is explicitly mentioned
4. For addresses: extract complete addresses when available
5. For financial amounts: extract specific dollar amounts mentioned
6. For dates: extract specific dates (not relative like "next week")
7. For contacts: extract names, emails, companies, roles
8. For tasks: suggest logical next steps based on email content
9. For action_items: identify items that need immediate attention
10. For progress_updates: note any mentioned milestones or progress

Return valid JSON matching the expected schema. Be conservative and accurate."""
            ).with_model("openai", "gpt-4o")
        return self._extractor_chat
    
    async def classify_email(self, subject: str, body: str, from_addr: str = "") -> EmailClassification:
        """Classify an email using LLM"""
        try:
            prompt = f"""Classify this email:

Subject: {subject}
From: {from_addr}
Body:
{body[:2000]}...

Return JSON with label, confidence, and reasoning."""

            chat = self._get_classifier_chat()
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Parse JSON response
            result = json.loads(response)
            
            return EmailClassification(
                label=result['label'],
                confidence=result['confidence'],
                reasoning=result.get('reasoning')
            )
            
        except Exception as e:
            logger.error(f"Error classifying email: {str(e)}")
            return EmailClassification(
                label="general_correspondence",
                confidence=0.1,
                reasoning=f"Classification failed: {str(e)}"
            )
    
    async def extract_email_data(
        self, 
        subject: str, 
        body: str, 
        classification: EmailClassification,
        from_addr: str = ""
    ) -> EmailExtractionResult:
        """Extract structured data from email"""
        try:
            schema = {
                "classification": {
                    "label": classification.label,
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning
                },
                "project": {
                    "name": "string or null",
                    "billing_type": "TM|SOV|Fixed|Bid or null",
                    "tm_bill_rate": "number or null",
                    "address": "string or null",
                    "city": "string or null", 
                    "state": "string or null",
                    "zip_code": "string or null",
                    "ahj": "string or null",
                    "client_company": "string or null",
                    "project_manager": "string or null",
                    "description": "string or null"
                },
                "contacts": [
                    {
                        "name": "string",
                        "email": "string", 
                        "company": "string or null",
                        "role": "string or null",
                        "phone": "string or null"
                    }
                ],
                "financial": {
                    "amount": "number or null",
                    "pay_app_number": "string or null",
                    "invoice_number": "string or null", 
                    "remittance": "number or null",
                    "payment_terms": "string or null"
                },
                "dates": {
                    "due_date": "YYYY-MM-DD or null",
                    "inspection_date": "YYYY-MM-DD or null",
                    "start_date": "YYYY-MM-DD or null",
                    "completion_date": "YYYY-MM-DD or null"
                },
                "links": ["array of URLs"],
                "tasks": ["array of suggested tasks"],
                "action_items": ["array of items needing attention"],
                "progress_updates": ["array of progress/milestone updates"]
            }

            prompt = f"""Extract data from this {classification.label} email:

Subject: {subject}
From: {from_addr}
Body:
{body}

Expected JSON schema:
{json.dumps(schema, indent=2)}

Extract all relevant data. Return null for unknown values. Be accurate and literal."""

            chat = self._get_extractor_chat()
            response = await chat.send_message(UserMessage(text=prompt))
            
            # Parse JSON response
            result = json.loads(response)
            
            # Build structured result
            return EmailExtractionResult(
                classification=classification,
                project=ProjectExtraction(**result.get('project', {})) if result.get('project') else None,
                contacts=[ContactInfo(**contact) for contact in result.get('contacts', [])],
                financial=FinancialInfo(**result.get('financial', {})) if result.get('financial') else None,
                dates=DateInfo(**result.get('dates', {})) if result.get('dates') else None,
                links=result.get('links', []),
                tasks=result.get('tasks', []),
                action_items=result.get('action_items', []),
                progress_updates=result.get('progress_updates', [])
            )
            
        except Exception as e:
            logger.error(f"Error extracting email data: {str(e)}")
            return EmailExtractionResult(
                classification=classification,
                action_items=[f"Failed to extract data: {str(e)}"]
            )
    
    async def process_email_complete(
        self, 
        subject: str, 
        body: str, 
        from_addr: str = ""
    ) -> Tuple[EmailExtractionResult, bool]:
        """Complete email processing pipeline"""
        try:
            # Step 1: Classify email
            classification = await self.classify_email(subject, body, from_addr)
            
            # Step 2: Check if classification is confident enough
            if classification.confidence < self.NEEDS_REVIEW_THRESHOLD:
                logger.info(f"Low confidence classification: {classification.confidence}")
                return EmailExtractionResult(
                    classification=classification,
                    action_items=["Low confidence classification - needs human review"]
                ), False
            
            # Step 3: Extract detailed data
            extraction = await self.extract_email_data(subject, body, classification, from_addr)
            
            # Step 4: Determine if auto-commit or needs review
            auto_commit = classification.confidence >= self.AUTO_COMMIT_THRESHOLD
            
            if not auto_commit:
                extraction.action_items.append("Moderate confidence - recommend human review")
            
            return extraction, auto_commit
            
        except Exception as e:
            logger.error(f"Error in complete email processing: {str(e)}")
            return EmailExtractionResult(
                classification=EmailClassification(
                    label="general_correspondence",
                    confidence=0.1,
                    reasoning=f"Processing failed: {str(e)}"
                ),
                action_items=[f"Email processing failed: {str(e)}"]
            ), False
    
    async def summarize_project_progress(self, emails: List[str], current_status: str = "") -> str:
        """Summarize project progress from multiple emails"""
        try:
            email_content = "\n\n---EMAIL SEPARATOR---\n\n".join(emails[:10])  # Limit to 10 emails
            
            prompt = f"""Analyze these project-related emails and provide a concise progress summary:

Current Status: {current_status}

Emails:
{email_content}

Provide a brief summary covering:
1. Key progress updates
2. Current project status
3. Upcoming milestones
4. Any issues or concerns
5. Next steps

Keep it concise but informative."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id="progress-summarizer",
                system_message="You are a project manager summarizing progress from email communications."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response
            
        except Exception as e:
            logger.error(f"Error summarizing project progress: {str(e)}")
            return f"Failed to summarize progress: {str(e)}"
    
    async def analyze_invoice_content(self, subject: str, body: str) -> Dict[str, Any]:
        """Analyze invoice content for key information"""
        try:
            prompt = f"""Extract invoice information from this email:

Subject: {subject}
Body: {body}

Extract and return JSON with:
{{
    "invoice_number": "string or null",
    "invoice_date": "YYYY-MM-DD or null", 
    "due_date": "YYYY-MM-DD or null",
    "amount": "number or null",
    "vendor": "string or null",
    "description": "string or null",
    "payment_terms": "string or null",
    "po_number": "string or null"
}}

Be accurate and return null for missing information."""

            chat = LlmChat(
                api_key=self.api_key,
                session_id="invoice-analyzer",
                system_message="You are an expert at extracting invoice information from emails."
            ).with_model("openai", "gpt-4o")
            
            response = await chat.send_message(UserMessage(text=prompt))
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error analyzing invoice: {str(e)}")
            return {"error": str(e)}

# Global instance
intelligence_llm = ProjectIntelligenceLLM()