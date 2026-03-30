"""
Application Configuration
=========================
Central configuration for the FastAPI application

ARCHITECTURE: Single Database, Multiple Domains
================================================
This system uses ONE PostgreSQL database with multiple DOMAINS.
Each domain has its own ALLOWED_TABLES and ALLOWED_COLUMNS.

Domains:
- HR Operations: checklist, delegation, users, leave_request, visitors, etc.
- Sales CRM: fms_leads, enquiry_to_order, make_quotation, login
- Maintenance: maintenance_task_assign
"""

from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "DB Assistant API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM Settings (Using OpenAI GPT)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("MODEL_NAME", "gpt-4o-mini")  # OpenAI GPT-4o-mini
    LLM_TEMPERATURE: float = 0.0
    
    # ────────────────────────────────────────────────────────
    # DATABASE CONNECTION (SINGLE DATABASE)
    # ────────────────────────────────────────────────────────
    # All domains connect to the SAME database.
    # Domain isolation is handled by ALLOWED_TABLES per domain.
    
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    
    # Primary Database URL (used by all domains)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "DB_CHECKLIST_URL", 
            f"postgresql://{os.getenv('DB_USER', '')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', '')}"
        )
    )
    
    # Legacy aliases (for backward compatibility - all point to same DB)
    @property
    def DB_CHECKLIST_URL(self) -> str:
        """Legacy alias - use DATABASE_URL instead"""
        return self.DATABASE_URL
    
    @property
    def DB_LEAD_TO_ORDER_URL(self) -> str:
        """Legacy alias - use DATABASE_URL instead"""
        return self.DATABASE_URL
    
    @property
    def DB_SAGAR_URL(self) -> str:
        """Legacy alias - use DATABASE_URL instead"""
        return self.DATABASE_URL
    
    # ────────────────────────────────────────────────────────
    # GLOBAL ALLOWED TABLES (All domains combined)
    # ────────────────────────────────────────────────────────
    # Note: Each domain only sees its subset via its own config.py
    
    # Security Settings
    MAX_QUERY_LENGTH: int = 50000
    MAX_RESULT_ROWS: int = 200
    ALLOWED_TABLES: List[str] = [
        # HR Operations Domain
        "users", "checklist", "delegation",
        "ticket_book", "leave_request",
        "request", "resume_request",
        "master", "all_loans", "request_forclosure", "collect_noc",
        "subscription", "approval_history", "payment_history", "subscription_renewals",
        "documents", "sharedocuments", "payment_fms",
        "visitors",
        # Sales CRM Domain
        "fms_leads", "enquiry_to_order", "make_quotation", "login",
        # Maintenance Domain
        "maintenance_task_assign"
    ]
    
    # Validation Settings
    MAX_VALIDATION_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: int = 70  # Auto-execute queries with confidence >= 70%
    
    # Metadata Settings
    METADATA_FILE: str = "metadata.json"
    
    # Session Settings
    SESSION_DB_PATH: str = "chat_sessions.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
