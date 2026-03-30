"""
HR Operations Domain - Connection Manager
==========================================
Manages connection to the shared PostgreSQL database.
This domain handles: users, checklist, delegation, ticket_book, leave_request,
request, resume_request, visitors, and other HR/Admin tables.

NOTE: All domains now use the SAME database (DATABASE_URL).
      Each domain only sees its ALLOWED_TABLES.
"""

from langchain_community.utilities import SQLDatabase
from app.core.config import settings
import os

class RestrictedSQLDatabase(SQLDatabase):
    """Database with table restrictions for HR domain"""
    def get_usable_table_names(self):
        all_tables = super().get_usable_table_names()
        # Allowed tables: task management + admin/HR modules
        allowed = [
            "checklist", "delegation", "users",
            "ticket_book", "leave_request",
            "request", "resume_request",
            "master", "all_loans", "request_forclosure", "collect_noc",
            "subscription", "approval_history", "payment_history", "subscription_renewals",
            "documents", "sharedocuments", "payment_fms",
            "visitors"
        ] 
        return [t for t in all_tables if t.lower() in allowed]

def get_db_instance():
    """
    Get the configured LangChain SQLDatabase instance for Agent usage.
    
    IMPORTANT: Uses shared DATABASE_URL (same as all other domains).
    Domain isolation is enforced via ALLOWED_TABLES in RestrictedSQLDatabase.
    """
    # Use the shared database URL (single database for all domains)
    url = settings.DATABASE_URL
    
    if not url:
        raise ValueError("DATABASE_URL is not set in configuration.")
    
    try:
        db = RestrictedSQLDatabase.from_uri(url)
        return db
    except Exception as e:
        print(f"[ERROR] Failed to connect to HR Operations domain: {e}")
        raise
