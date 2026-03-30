# 🤖 Intelligent Multi-Domain Database Assistant

**Version 2.2 — Single Database, Multi-Domain Architecture | Bilingual Support**

An advanced AI-powered system designed to interact with **multiple business domains** within a **single PostgreSQL database** using natural language. The system uses a **Domain Router + Dual-LLM Validation Architecture** to understand context, handle ambiguity across domains, and self-correct SQL errors.

> 🆕 **v2.2 Architecture Update**: Migrated from multiple databases to a **Single Database, Multi-Domain** architecture. All tables now reside in one PostgreSQL instance with domain-based isolation via `ALLOWED_TABLES`.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE PostgreSQL DATABASE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│   │  HR OPERATIONS  │  │   SALES CRM     │  │  MAINTENANCE   │  │
│   │    DOMAIN       │  │    DOMAIN       │  │    DOMAIN      │  │
│   │                 │  │                 │  │                │  │
│   │ • checklist     │  │ • fms_leads     │  │ • maintenance_ │  │
│   │ • delegation    │  │ • enquiry_to_   │  │   task_assign  │  │
│   │ • users         │  │   order         │  │                │  │
│   │ • leave_request │  │ • make_quotation│  │                │  │
│   │ • visitors      │  │ • login         │  │                │  │
│   │ • ticket_book   │  │                 │  │                │  │
│   │ • request       │  │                 │  │                │  │
│   │ • resume_request│  │                 │  │                │  │
│   │ • + 10 more...  │  │                 │  │                │  │
│   └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  DOMAIN ROUTER    │
                    │ (AI-Powered)      │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        HR Agent        Sales Agent    Maintenance Agent
     (sees 18 tables)  (sees 4 tables)  (sees 1 table)
```

---

## 🌟 Key Features

### 🧠 1. Intelligent Domain Router

* **Schema-Aware Routing**: The router analyzes the **actual table & column names** of each domain, not just keywords.
* **Single Connection**: All domains share the **same database connection**, reducing complexity.
* **Ambiguity Protocol**: If a query term appears in multiple domains, the agent **pauses** and asks for clarification.
* **Clarification Memory**: Once clarified, it merges context with the original question.

### 🛡️ 2. Self-Correcting SQL Agents (Dual-LLM)

* **Generate-Validate-Regenerate Loop**:
  1. **Generator (LLM 1)**: Writes SQL using semantic schema + business rules.
  2. **Validator (LLM 2)**: Checks against column restrictions, intent matching, LOWER() enforcement.
  3. **Refiner**: Auto-rewrites with feedback (max 3 attempts).
* **Domain Isolation**: Each agent only sees its `ALLOWED_TABLES`.

### 🌐 3. Hindi / Hinglish Bilingual Support

* Understands mixed Hindi-English queries:
  - `"aaj ke pending tasks dikhao"` → Show today's pending tasks
  - `"jinka leave approve nhi hua unka naam batao"` → Names with unapproved leave
  - `"sabka travel data do"` → Show everyone's travel data

---

## 📊 Domain Structure

### 📋 Domain 1: **HR Operations** (`checklist`)

Employee & HR management covering tasks, leaves, travel, hiring, and visitors.

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `checklist` | Daily/routine tasks | name, department, task_description, submission_date, status |
| `delegation` | One-time assigned tasks | name, given_by, planned_date, submission_date |
| `users` | Employee info & login | user_name, department, role, email_id, status |
| `leave_request` | Leave management | employee_name, from_date, to_date, request_status, approved_by |
| `visitors` | Visitor gate pass | visitor_name, purpose_of_visit, person_to_meet, approval_status |
| `ticket_book` | Travel bills | person_name, type_of_bill, total_amount, charges |
| `request` | Travel requests | person_name, type_of_travel, from_city, to_city |
| `resume_request` | Hiring pipeline | candidate_name, experience, interviewer_status, joined_status |
| + 10 more | Finance, subscriptions, documents | ... |

### 💼 Domain 2: **Sales CRM** (`lead_to_order`)

Full-cycle sales: Lead → Enquiry → Quotation → Order.

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `fms_leads` | Lead tracking | lead_source, status (Hot/Warm/Cold), is_order_received |
| `enquiry_to_order` | Conversion tracking | timestamp, planned, actual, is_order_received |
| `make_quotation` | Quotation management | quotation_no, prepared_by, company_name, grand_total |
| `login` | CRM user accounts | username, password, usertype |

### ⚙️ Domain 3: **Maintenance** (`sagar_db`)

Machine repairs and maintenance tasks.

| Table | Purpose | Key Columns |
|:------|:--------|:------------|
| `maintenance_task_assign` | Maintenance tasks | Machine_Name, Doer_Name, Task_Start_Date, Actual_Date |

**Business Rules:**
- `Actual_Date IS NULL` → Task is **PENDING**
- `Actual_Date IS NOT NULL` → Task is **COMPLETED**
- ⚠️ Uses Mixed-Case columns (requires quoting in SQL)

---

## 🛠️ System Architecture

```mermaid
flowchart TD
    U("👤 User")
    RT{"🔀 Domain Router"}
    
    subgraph DB ["📊 Single PostgreSQL Database"]
        D1["📋 HR Domain<br/>18 Tables"]
        D2["💼 Sales Domain<br/>4 Tables"]
        D3["⚙️ Maintenance Domain<br/>1 Table"]
    end
    
    subgraph AGENT ["🤖 Dual-LLM Agent"]
        SG["SQL Generator<br/>LLM 1"]
        SV{"Validator<br/>LLM 2"}
        EX["Executor"]
    end
    
    SY["📝 Answer Synthesizer"]
    
    U --> RT
    RT -->|"HR Intent"| D1
    RT -->|"Sales Intent"| D2  
    RT -->|"Maintenance Intent"| D3
    
    D1 --> AGENT
    D2 --> AGENT
    D3 --> AGENT
    
    SG --> SV
    SV -->|"❌ Reject"| SG
    SV -->|"✅ Approve"| EX
    EX --> SY
    SY --> U
```

---

## 📂 Project Structure

```text
Sagar_tmt_DB_assistant/
├── Backend_New/                    # FastAPI Python Backend
│   ├── main.py                     # Application entry point
│   ├── .env                        # Environment variables
│   ├── app/
│   │   ├── core/
│   │   │   ├── router.py           # Domain Router (AI-powered)
│   │   │   ├── config.py           # Single DATABASE_URL + settings
│   │   │   ├── security.py         # SQL injection prevention
│   │   │   └── auth.py             # Authentication
│   │   ├── domains/                # 🔌 Domain Modules (share same DB)
│   │   │   ├── hr_operations/      # HR Operations Domain
│   │   │   │   ├── config.py       # ALLOWED_TABLES, ALLOWED_COLUMNS
│   │   │   │   ├── connection.py   # Uses shared DATABASE_URL
│   │   │   │   ├── prompts.py      # Domain-specific prompts
│   │   │   │   └── workflow.py     # LangGraph workflow
│   │   │   ├── sales_crm/          # Sales CRM Domain
│   │   │   └── maintenance/        # Maintenance Domain
│   │   ├── services/
│   │   │   ├── cache_service.py    # Semantic query cache (ChromaDB)
│   │   │   ├── context_manager.py  # Conversation context
│   │   │   └── session_manager.py  # Multi-user sessions
│   │   └── api/routes/
│   │       └── chat.py             # Chat streaming endpoint (SSE)
├── Frontend/                       # Chat UI (HTML/JS)
├── Database_Schemas/               # Schema documentation
├── SYSTEM_DOCUMENTATION.md         # Complete system docs
├── DOMAIN_INTEGRATION_GUIDE.md     # How to add new domains
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* PostgreSQL Database (single instance with all tables)
* OpenAI API Key
* pip (Python package manager)

### Installation

1. **Clone & Setup**:

   ```bash
   git clone <repo_url>
   cd Sagar_tmt_DB_assistant
   ```

2. **Create Virtual Environment**:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   cd Backend_New
   pip install -r requirements.txt
   ```

   Key dependencies:
   - `fastapi` + `uvicorn` — API server
   - `langchain-community` + `langchain-openai` — LLM framework
   - `langgraph` — Agent state machine
   - `psycopg2-binary` — PostgreSQL driver
   - `chromadb` — Semantic cache
   - `python-dotenv` + `pydantic-settings` — Configuration

4. **Environment Variables**:
   Create a `.env` file in `Backend_New/`:

   ```properties
   # ============================================
   # SINGLE DATABASE CONNECTION
   # ============================================
   # One PostgreSQL database with multiple domains
   DATABASE_URL=postgresql://user:pass@host:5432/main_database

   # ============================================
   # LLM Configuration
   # ============================================
   OPENAI_API_KEY=sk-...
   LLM_MODEL=gpt-4o-mini

   # ============================================
   # Optional Tuning
   # ============================================
   MAX_VALIDATION_ATTEMPTS=3
   CONFIDENCE_THRESHOLD=70
   CACHE_SIMILARITY_THRESHOLD=0.92
   ```

5. **Run the Backend**:

   ```bash
   cd Backend_New
   uvicorn main:app --reload
   ```

   The API will start at `http://127.0.0.1:8000`.

6. **Open the Frontend**:

   Open `Frontend/index.html` in your browser or navigate to `http://localhost:8000/app`.

---

## 🔧 Developer Guide

### How to Add a New Domain

Since all domains share the same database, adding a new domain only requires:

1. **Create Domain Module**: Create a folder under `app/domains/your_new_domain/` with:
   - `config.py` — `ROUTER_METADATA`, `ALLOWED_TABLES`, `ALLOWED_COLUMNS`, `SEMANTIC_SCHEMA`
   - `connection.py` — Uses shared `settings.DATABASE_URL` + `RestrictedSQLDatabase`
   - `prompts.py` — Generator, Validator, and Answer Synthesis prompts
   - `workflow.py` — LangGraph agent workflow

2. **Register in Router**: Import your metadata in `app/core/router.py`:
   ```python
   from app.databases.your_new_domain.config import ROUTER_METADATA, SEMANTIC_SCHEMA
   
   REGISTERED_DOMAINS = [
       ...
       (YOUR_DOMAIN_META, YOUR_DOMAIN_SCHEMA),
   ]
   ```

3. **Connection Template** (`connection.py`):
   ```python
   from app.core.config import settings
   
   def get_db_instance():
       return RestrictedSQLDatabase(
           connection_string=settings.DATABASE_URL,
           schema="public",
           include_tables=ALLOWED_TABLES,
       )
   ```

See `DOMAIN_INTEGRATION_GUIDE.md` for a full step-by-step walkthrough.

### Adding New Tables to an Existing Domain

1. Add to `ALLOWED_TABLES` in `app/domains/<domain>/config.py`
2. Add to `ALLOWED_COLUMNS` in `app/domains/<domain>/config.py`
3. Add to `SEMANTIC_SCHEMA` in `app/domains/<domain>/config.py`
4. Update `target_tables` in `app/domains/<domain>/workflow.py`
5. Update prompts in `app/domains/<domain>/prompts.py`

### Key Concept: Domain Isolation

Each domain module defines its own `ALLOWED_TABLES`:

```python
# HR Domain (checklist/config.py)
ALLOWED_TABLES = ["checklist", "delegation", "users", "leave_request", ...]

# Sales Domain (lead_to_order/config.py)
ALLOWED_TABLES = ["fms_leads", "enquiry_to_order", "make_quotation", "login"]

# Maintenance Domain (sagar_db/config.py)
ALLOWED_TABLES = ["maintenance_task_assign"]
```

The `RestrictedSQLDatabase` class filters the schema to only show allowed tables, even though all tables exist in the same database.

### Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| "Ambiguous Query" loop | Router metadata descriptions too similar | Make `ROUTER_METADATA` descriptions more distinct |
| "Column does not exist" | PostgreSQL mixed-case columns | Add quotes in config (e.g., `"Machine_Name"`) |
| Agent sees wrong tables | `ALLOWED_TABLES` not updated | Add table name to domain's config.py |
| "No result returned" | Empty query results or graph error | Check debug logs; empty results now handled gracefully |
| Hindi words used as filter | Glossary incomplete | Add new words to HINDI GLOSSARY in prompts.py |
| Excessive validation loops | Validator too strict | Review validator prompt strictness settings |

---

## 🆕 Changelog

### v2.2 — Single Database, Multi-Domain Architecture (Current)

**Architecture Changes:**
- ✅ Migrated from 3 separate databases to **single PostgreSQL database**
- ✅ All domain modules now use shared `DATABASE_URL` connection
- ✅ Domain isolation via `ALLOWED_TABLES` per domain module
- ✅ Simplified configuration — one connection string instead of three
- ✅ Updated terminology: "databases" → "domains" throughout codebase

**Files Modified:**
- `Backend_New/app/core/config.py` — Single `DATABASE_URL` with legacy aliases
- `Backend_New/app/core/router.py` — Renamed to `REGISTERED_DOMAINS`
- `Backend_New/app/domains/*/connection.py` — All use `settings.DATABASE_URL`
- `Backend_New/.env.example` — New single-database configuration

### v2.1 — HR Module Expansion

**New Tables Integrated:**
- `ticket_book` — Ticket bookings & travel bills
- `leave_request` — Employee leave management with multi-level approval
- `visitors` — Visitor gate pass tracking with inline UI image rendering
- `request` — Employee travel requests
- `resume_request` — Candidate resume intake & hiring pipeline

**Improvements:**
- Empty Result Handling — Empty SQL results now generate AI-powered friendly messages
- Hindi/Hinglish Glossary — Bilingual word recognition in prompts
- Negation-Aware Intent Rules — "not approved", "not completed" mapped correctly
- Column-Level Security — Each table has explicit allowed/forbidden columns
- LOWER() Enforcement — Case-insensitive matching across all tables

---

## 📞 Support

For bugs or feature requests, check the debug logs in the terminal output or contact the development team.

---

## 📝 Related Documentation

- **[SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md)** — Complete system architecture and workflow diagrams
- **[DOMAIN_INTEGRATION_GUIDE.md](DOMAIN_INTEGRATION_GUIDE.md)** — Step-by-step guide to add new domains
- **[BACKEND_NEW_WORKFLOW.md](BACKEND_NEW_WORKFLOW.md)** — LangGraph workflow details
