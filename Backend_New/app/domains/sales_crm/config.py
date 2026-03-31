"""
Sales CRM Domain - Configuration
=================================
Domain: lead_to_order (Sales CRM)
Tables: 4 (fms_leads, enquiry_to_order, make_quotation, login)

Part of Single Database, Multi-Domain Architecture (v2.2)
All domains share DATABASE_URL with isolation via ALLOWED_TABLES.
"""

# 1. Table & Column Restrictions
ALLOWED_TABLES = ["fms_leads", "enquiry_to_order", "make_quotation", "login"]

# Router Metadata (Used for Auto-Discovery)
ROUTER_METADATA = {
    "name": "lead_to_order",
    "description": "A full-cycle Sales CRM & Pipeline Management System. It tracks the entire customer journey from initial Lead (FMS Leads) -> Enquiry -> Quotation -> Final Order. Use this domain for questions about sales figures, lead conversion rates, quotation details, customer enquiries, and sales team performance. It focuses on 'money', 'customers', and the 'sales process'.",
    "keywords": [
        "lead", "enquiry", "quote", "quotation", "sales", "customer", "call", 
        "planned", "actual", "converted", "fms", "lead to order database", 
        "crm", "sales system", "sales db", "users", "admin", "login", "password",
        "revenue", "pipeline", "conversion"
    ]
}

COLUMNS_RESTRICTION = {
    "fms_leads": [
        "created_at", "planned", "actual", 
        "planned1", "actual1", 
        "enquiry_received_status", "is_order_received",
        "lead_source", "status"
    ],
    "enquiry_to_order": [
        "timestamp", "planned", "actual", "is_order_received"
    ],
    "make_quotation": [
        "timestamp", "quotation_no", "quotation_date", "prepared_by",
        "company_name", "contact_name", "contact_no", "consignee_state",
        "payment_terms", "delivery", "freight", "taxes", "items",
        "grand_total", "pdf_url"
    ],
    "login": [
        "username", "password", "usertype" 
    ]
}

# 2. Schema Definition for LLM Context
# (We only include the allowed columns to save tokens and focus the LLM)
DB_SCHEMA = """
Table: fms_leads
Columns:
- created_at (TEXT): When lead was created. Stored as TEXT, cast to DATE: created_at::DATE.
- planned (TEXT): Planned date for first action. Stored as TEXT, cast: planned::DATE.
- actual (TEXT): Actual date of first action. Stored as TEXT, cast: actual::DATE.
- planned1 (TEXT): Planned date for second action/follow-up. Stored as TEXT.
- actual1 (TEXT): Actual date of second action. Stored as TEXT.
- lead_source (TEXT): Source of lead. Values: ['Indiamart', 'Direct Visit', 'Telephonic', 'Email', 'WHATSAPP', 'Referral']. Use TRIM() when grouping.
- status (TEXT): Lead heat/status. Values: ['Hot', 'Warm', 'Cold']. Use LOWER() for comparison.
- enquiry_received_status (TEXT): Status of enquiry receipt. Values: ['yes', 'expected', NULL].
- is_order_received (TEXT): Final order status. Values: ['yes', NULL]. (NULL implies No).

Table: enquiry_to_order
Columns:
- timestamp (TIMESTAMP): When enquiry was recorded. Actual TIMESTAMP type.
- planned (DATE): Planned follow-up date. Actual DATE type.
- actual (DATE): Actual follow-up date (completion). Actual DATE type.
- is_order_received (BOOLEAN): Whether enquiry converted. Values: [True, False, NULL].

Table: make_quotation
Columns:
- timestamp (TIMESTAMP): Creation time. Actual TIMESTAMP type.
- quotation_no (TEXT): Unique Quotation ID (QN-xxx).
- quotation_date (DATE): Date on the quotation. Actual DATE type.
- prepared_by (TEXT): User who made the quote (e.g., 'Aakash', 'SHEETAL PATEL'). Use TRIM() when grouping.
- company_name (TEXT): Customer company. Use TRIM() when grouping.
- contact_name (TEXT): Customer contact person.
- contact_no (TEXT): Customer phone.
- consignee_state (TEXT): Customer state (e.g., 'Chhattisgarh'). Use TRIM() when grouping.
- payment_terms (TEXT): Payment terms description (e.g., '100% advance').
- delivery (TEXT): Delivery terms.
- freight (TEXT): Freight charges/terms.
- taxes (TEXT): Tax info.
- items (JSONB): JSON list of items quoted (code, name, qty, rate).
- grand_total (NUMERIC): Total value of quotation.
- pdf_url (TEXT): Link to generated PDF.

Table: login
Columns:
- username (TEXT): User login ID.
- password (TEXT): User password (Plaintext).
- usertype (TEXT): usage role (e.g. admin).
"""
