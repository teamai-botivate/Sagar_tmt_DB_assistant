# 📖 Sagar TMT DB Assistant — Complete System Documentation

**Version:** 2.2  
**Last Updated:** March 2026  
**Type:** Intelligent Single-Database, Multi-Domain Natural Language Query System

---

## 📋 Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Directory Structure](#4-directory-structure)
5. [Domain Architecture](#5-domain-architecture)
6. [Routing System](#6-routing-system)
7. [LangGraph Agent Workflow](#7-langgraph-agent-workflow)
8. [Dual-LLM Validation Process](#8-dual-llm-validation-process)
9. [Complete Request Flow](#9-complete-request-flow)
10. [API Documentation](#10-api-documentation)
11. [Frontend Architecture](#11-frontend-architecture)
12. [Services & Components](#12-services--components)
13. [Security Features](#13-security-features)
14. [Configuration Guide](#14-configuration-guide)
15. [Deployment](#15-deployment)

---

## 1. System Overview

### What is this system?

The **Sagar TMT DB Assistant** is an AI-powered chatbot that allows users to query **multiple business domains** within a **single PostgreSQL database** using **natural language** (including Hindi/Hinglish). Instead of writing SQL manually, users can ask questions like:

- *"Show me pending tasks in PC department this month"*
- *"aaj ke pending tasks dikhao"* (Hindi)
- *"How many hot leads came from Indiamart?"*
- *"Which machine repairs are overdue?"*

### Architecture Evolution (v2.2)

```
┌───────────────────────────────────────────────────────────────────┐
│                     ARCHITECTURE EVOLUTION                         │
├───────────────────────────────────────────────────────────────────┤
│                                                                    │
│  v2.1 (OLD)                        v2.2 (NEW)                     │
│  ─────────────                     ─────────────                  │
│                                                                    │
│  ┌──────────┐                      ┌──────────────────────────┐   │
│  │ DB 1     │                      │   SINGLE DATABASE        │   │
│  │checklist │                      │                          │   │
│  └──────────┘                      │  ┌──────┐ ┌──────┐ ┌──┐  │   │
│  ┌──────────┐         ──►          │  │HR    │ │Sales │ │  │  │   │
│  │ DB 2     │                      │  │Domain│ │Domain│ │..│  │   │
│  │lead2order│                      │  └──────┘ └──────┘ └──┘  │   │
│  └──────────┘                      │                          │   │
│  ┌──────────┐                      └──────────────────────────┘   │
│  │ DB 3     │                                                     │
│  │sagar_db  │                      All tables in one DB,          │
│  └──────────┘                      isolated by ALLOWED_TABLES     │
│                                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### Key Capabilities

| Feature | Description |
|---------|-------------|
| 🧠 **Deep Schema Router** | AI analyzes actual table/column names to route to correct domain |
| 🗄️ **Single Database** | All domains share one PostgreSQL connection |
| 🔀 **Domain Isolation** | Each domain only sees its `ALLOWED_TABLES` |
| 🛡️ **Dual-LLM Validation** | Generator + Validator ensures query accuracy |
| 🌐 **Bilingual Support** | Hindi, Hinglish, and English queries |
| ⚡ **Semantic Caching** | Similar queries use cached results |
| 💬 **Context Awareness** | Understands follow-up questions |
| 🔒 **Security First** | SQL injection prevention, column restrictions |
| 📡 **Real-time Streaming** | Word-by-word response streaming |

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                        (Frontend - HTML/CSS/JS)                              │
│                                                                              │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│   │   Login     │    │   Chat UI   │    │  Sessions   │    │   Cache     │  │
│   │   Screen    │    │  Streaming  │    │   Sidebar   │    │   Stats     │  │
│   └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
                                          │ HTTP/SSE (POST /chat/stream)
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                    │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         API LAYER                                    │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│   │   │  Auth    │  │  Chat    │  │ Sessions │  │     Health       │   │   │
│   │   │ /auth/*  │  │ /chat/*  │  │  /chat/  │  │       /          │   │   │
│   │   │          │  │          │  │ sessions │  │                  │   │   │
│   │   └──────────┘  └────┬─────┘  └──────────┘  └──────────────────┘   │   │
│   └──────────────────────┼──────────────────────────────────────────────┘   │
│                          │                                                   │
│   ┌──────────────────────┼──────────────────────────────────────────────┐   │
│   │                      ▼         CORE LAYER                            │   │
│   │   ┌──────────────────────────────────────────────────────────────┐  │   │
│   │   │                    INTELLIGENT ROUTER                         │  │   │
│   │   │              (GPT-4o-mini powered routing)                    │  │   │
│   │   │                                                               │  │   │
│   │   │   Input: "Show pending machine repairs"                       │  │   │
│   │   │   Output: { domain: "sagar_db", reason: "..." }               │  │   │
│   │   └───────────────────────┬──────────────────────────────────────┘  │   │
│   │                           │                                          │   │
│   │         ┌─────────────────┼─────────────────┐                       │   │
│   │         ▼                 ▼                 ▼                       │   │
│   │   ┌───────────┐    ┌───────────┐    ┌───────────────┐              │   │
│   │   │    HR     │    │   Sales   │    │ Maintenance   │              │   │
│   │   │  Domain   │    │  Domain   │    │   Domain      │              │   │
│   │   │(18 tables)│    │ (4 tables)│    │  (1 table)    │              │   │
│   │   └─────┬─────┘    └─────┬─────┘    └───────┬───────┘              │   │
│   │         │                │                  │                       │   │
│   │         └────────────────┼──────────────────┘                       │   │
│   │                          ▼                                          │   │
│   │   ┌──────────────────────────────────────────────────────────────┐  │   │
│   │   │                  LANGGRAPH AGENT                              │  │   │
│   │   │                (6-Node State Machine)                         │  │   │
│   │   │                                                               │  │   │
│   │   │   list_tables → get_schema → store_schema                     │  │   │
│   │   │                                   ↓                           │  │   │
│   │   │                           generate_query (LLM 1)              │  │   │
│   │   │                                   ↓                           │  │   │
│   │   │                           validate_query (LLM 2)              │  │   │
│   │   │                                   ↓                           │  │   │
│   │   │                             run_query                         │  │   │
│   │   └──────────────────────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                       SERVICES LAYER                                 │   │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│   │   │   Cache     │  │   Context   │  │   Session   │  │    DB     │  │   │
│   │   │  (ChromaDB) │  │   Manager   │  │   Manager   │  │  Service  │  │   │
│   │   └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────┬───────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
          ┌─────────────────────────────────────────────────────────────┐
          │                   SINGLE PostgreSQL DATABASE                 │
          │                                                              │
          │    ┌───────────────────┐ ┌───────────────┐ ┌─────────────┐  │
          │    │   HR DOMAIN       │ │ SALES DOMAIN  │ │MAINTENANCE  │  │
          │    │   (18 tables)     │ │  (4 tables)   │ │  (1 table)  │  │
          │    │                   │ │               │ │             │  │
          │    │  • users          │ │  • fms_leads  │ │ •maintenance│  │
          │    │  • checklist      │ │  • enquiry_to │ │  _task_     │  │
          │    │  • delegation     │ │    _order     │ │   assign    │  │
          │    │  • leave_request  │ │  • make_      │ │             │  │
          │    │  • visitors       │ │    quotation  │ │             │  │
          │    │  • ticket_book    │ │  • login      │ │             │  │
          │    │  • request        │ │               │ │             │  │
          │    │  • resume_request │ │               │ │             │  │
          │    │  • + 10 more...   │ │               │ │             │  │
          │    └───────────────────┘ └───────────────┘ └─────────────┘  │
          │                                                              │
          │    Each domain sees ONLY its ALLOWED_TABLES via             │
          │    RestrictedSQLDatabase filtering                          │
          └──────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.10+ |
| **FastAPI** | Web framework | Latest |
| **LangChain** | LLM framework | Latest |
| **LangGraph** | Agent state machine | Latest |
| **OpenAI GPT** | LLM provider | gpt-4o-mini |
| **PostgreSQL** | Single database | 12+ |
| **ChromaDB** | Semantic cache | Latest |
| **SQLite** | Session storage | Built-in |
| **Pydantic** | Data validation | v2 |
| **Uvicorn** | ASGI server | Latest |

### Frontend

| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling |
| **JavaScript** | Interactivity |
| **Marked.js** | Markdown rendering |
| **Font Awesome** | Icons |
| **SSE (EventSource)** | Real-time streaming |

---

## 4. Directory Structure

```
Sagar_tmt_DB_assistant/
│
├── Backend_New/                          # 🔧 FastAPI Backend Application
│   ├── main.py                           # Application entry point
│   ├── requirements.txt                  # Python dependencies
│   ├── .env                              # Environment variables (secrets)
│   ├── .env.example                      # Environment template
│   ├── chat_sessions.db                  # SQLite session storage
│   ├── chroma_cache/                     # ChromaDB cache directory
│   │
│   └── app/                              # Application package
│       ├── __init__.py
│       │
│       ├── api/                          # 🌐 API Layer
│       │   ├── __init__.py
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── auth.py               # POST /auth/login
│       │       ├── chat.py               # POST /chat/stream (main endpoint)
│       │       ├── sessions.py           # Session CRUD operations
│       │       └── health.py             # Health checks
│       │
│       ├── core/                         # ⚙️ Core Configuration
│       │   ├── __init__.py
│       │   ├── config.py                 # Settings (Pydantic)
│       │   ├── router.py                 # AI-powered database router
│       │   ├── security.py               # SQL injection prevention
│       │   ├── auth.py                   # Authentication middleware
│       │   └── column_restrictions.py    # Column-level security
│       │
│       ├── domains/                      # 🗄️ Domain Modules (Share same DB)
│       │   │
│       │   ├── hr_operations/            # HR/Employee Domain
│       │   │   ├── config.py             # Schema, metadata, restrictions
│       │   │   ├── connection.py         # DB connection handler
│       │   │   ├── prompts.py            # LLM prompts
│       │   │   └── workflow.py           # LangGraph agent
│       │   │
│       │   ├── sales_crm/                # Sales CRM Domain
│       │   │   ├── config.py
│       │   │   ├── connection.py
│       │   │   ├── prompts.py
│       │   │   └── workflow.py
│       │   │
│       │   └── maintenance/              # Machine Maintenance Domain
│       │       ├── config.py
│       │       ├── connection.py
│       │       ├── prompts.py
│       │       └── workflow.py
│       │
│       ├── services/                     # 🔌 Shared Services
│       │   ├── __init__.py
│       │   ├── sql_agent.py              # Legacy SQL agent
│       │   ├── agent_nodes.py            # Graph node implementations
│       │   ├── cache_service.py          # ChromaDB semantic cache
│       │   ├── context_manager.py        # Conversation context
│       │   ├── db_service.py             # Database operations
│       │   └── session_manager.py        # Session CRUD
│       │
│       └── tools/                        # 🛠️ Utilities
│           └── db_inspector.py           # Schema inspection tool
│
├── Frontend/                             # 💻 Chat User Interface
│   ├── index.html                        # Main HTML page
│   ├── app.js                            # JavaScript logic
│   ├── styles.css                        # CSS styling
│   ├── logo.png                          # Company logo
│   └── vercel.json                       # Vercel deployment config
│
├── Database_Schemas/                     # 📊 Schema Documentation
│   ├── hr_operations/
│   │   ├── schema_report.md
│   │   └── metadata_analysis.json
│   ├── sales_crm/
│   └── maintenance/
│
├── README.md                             # Project overview
├── BACKEND_NEW_WORKFLOW.md               # Technical workflow docs
├── DOMAIN_INTEGRATION_GUIDE.md           # How to add new domains
└── SYSTEM_DOCUMENTATION.md               # This file
```

---

## 5. Domain Architecture

### Overview Diagram — Single Database, Multi-Domain

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SINGLE POSTGRESQL DATABASE                            │
│                         (DATABASE_URL)                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  All tables reside in ONE database. Domain isolation is achieved        │
│  through ALLOWED_TABLES configuration per domain module.                │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                     DOMAIN 1: HR OPERATIONS                        │ │
│  │                  (checklist/ - 18 tables)                          │ │
│  │                                                                    │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │   │    users     │  │  checklist   │  │  delegation  │            │ │
│  │   │──────────────│  │──────────────│  │──────────────│            │ │
│  │   │ user_name    │  │ name         │  │ name         │            │ │
│  │   │ department   │  │ department   │  │ given_by     │            │ │
│  │   │ role         │  │ task_desc    │  │ department   │            │ │
│  │   │ email_id     │  │ frequency    │  │ task_desc    │            │ │
│  │   │ number       │  │ task_start   │  │ planned_date │            │ │
│  │   │ status       │  │ submission   │  │ submission   │            │ │
│  │   └──────────────┘  │ status       │  └──────────────┘            │ │
│  │                     └──────────────┘                               │ │
│  │                                                                    │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │   │ ticket_book  │  │leave_request │  │   visitors   │            │ │
│  │   │──────────────│  │──────────────│  │──────────────│            │ │
│  │   │ person_name  │  │ employee_name│  │ visitor_name │            │ │
│  │   │ type_of_bill │  │ from_date    │  │ purpose      │            │ │
│  │   │ status       │  │ to_date      │  │ person_meet  │            │ │
│  │   │ bill_number  │  │ reason       │  │ date_of_visit│            │ │
│  │   │ total_amount │  │ request_stat │  │ time_entry   │            │ │
│  │   │ charges      │  │ approved_by  │  │ approval_stat│            │ │
│  │   └──────────────┘  │ hr_approval  │  └──────────────┘            │ │
│  │                     └──────────────┘                               │ │
│  │                                                                    │ │
│  │   ┌──────────────┐  ┌──────────────┐  + 10 more tables            │ │
│  │   │   request    │  │resume_request│  (master, all_loans, etc.)   │ │
│  │   │──────────────│  │──────────────│                              │ │
│  │   │ person_name  │  │candidate_name│                              │ │
│  │   │ type_travel  │  │applied_for   │                              │ │
│  │   │ from_city    │  │experience    │                              │ │
│  │   │ to_city      │  │interviewer_  │                              │ │
│  │   │ departure    │  │  status      │                              │ │
│  │   │ reason       │  │joined_status │                              │ │
│  │   └──────────────┘  └──────────────┘                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                   DOMAIN 2: SALES CRM                              │ │
│  │                (lead_to_order/ - 4 tables)                         │ │
│  │                                                                    │ │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │ │
│  │   │  fms_leads   │  │enquiry_to_   │  │make_quotation│            │ │
│  │   │──────────────│  │    order     │  │──────────────│            │ │
│  │   │ created_at   │  │──────────────│  │ quotation_no │            │ │
│  │   │ planned      │  │ timestamp    │  │ quotation_   │            │ │
│  │   │ actual       │  │ planned      │  │   date       │            │ │
│  │   │ lead_source  │  │ actual       │  │ prepared_by  │            │ │
│  │   │ status       │  │ is_order_    │  │ company_name │            │ │
│  │   │ enquiry_rcvd │  │   received   │  │ contact_name │            │ │
│  │   │ is_order_    │  └──────────────┘  │ grand_total  │            │ │
│  │   │   received   │                    │ items        │            │ │
│  │   └──────────────┘                    └──────────────┘            │ │
│  │                                                                    │ │
│  │   Status Values: 'Hot', 'Warm', 'Cold'                            │ │
│  │   Lead Sources: 'Indiamart', 'Direct Visit', 'Telephonic', 'Email'│ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                    DOMAIN 3: MAINTENANCE                           │ │
│  │                    (sagar_db/ - 1 table)                           │ │
│  │                                                                    │ │
│  │   ┌────────────────────────────────────────────────────────────┐  │ │
│  │   │              maintenance_task_assign                        │  │ │
│  │   │────────────────────────────────────────────────────────────│  │ │
│  │   │  "Machine_Name"    VARCHAR    (Mixed-Case - needs quotes)  │  │ │
│  │   │  "Doer_Name"       VARCHAR    (Technician name)            │  │ │
│  │   │  "Task_Start_Date" TIMESTAMP  (When assigned)              │  │ │
│  │   │  "Actual_Date"     TIMESTAMP  (When completed)             │  │ │
│  │   │                                                             │  │ │
│  │   │  ⚠️ Business Rules:                                        │  │ │
│  │   │  • Actual_Date IS NULL → Task is PENDING                   │  │ │
│  │   │  • Actual_Date IS NOT NULL → Task is COMPLETED             │  │ │
│  │   └────────────────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Domain Isolation Mechanism

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     HOW DOMAIN ISOLATION WORKS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Single DATABASE_URL connects to PostgreSQL                          │
│                                                                          │
│  2. Each domain module defines ALLOWED_TABLES:                          │
│                                                                          │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  checklist/config.py:                                         │    │
│     │  ALLOWED_TABLES = ["users", "checklist", "delegation", ...]  │    │
│     │                                                               │    │
│     │  lead_to_order/config.py:                                    │    │
│     │  ALLOWED_TABLES = ["fms_leads", "enquiry_to_order", ...]     │    │
│     │                                                               │    │
│     │  sagar_db/config.py:                                         │    │
│     │  ALLOWED_TABLES = ["maintenance_task_assign"]                │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  3. RestrictedSQLDatabase filters schema at connection time:            │
│                                                                          │
│     ┌──────────────────────────────────────────────────────────────┐    │
│     │  def get_db_instance():                                       │    │
│     │      return RestrictedSQLDatabase(                            │    │
│     │          connection_string=settings.DATABASE_URL,  # SHARED   │    │
│     │          include_tables=ALLOWED_TABLES,            # FILTERED │    │
│     │      )                                                        │    │
│     └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  4. Result: Each domain agent ONLY sees its allowed tables              │
│                                                                          │
│     ┌────────────────┐  ┌────────────────┐  ┌────────────────┐          │
│     │  HR Agent      │  │  Sales Agent   │  │ Maint. Agent   │          │
│     │  sees 18       │  │  sees 4        │  │  sees 1        │          │
│     │  tables        │  │  tables        │  │  table         │          │
│     └────────────────┘  └────────────────┘  └────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Routing System

### Router Architecture

```
                              USER QUERY
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTELLIGENT ROUTER                                  │
│                     (app/core/router.py)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                     REGISTERED DOMAINS                            │  │
│   │                                                                   │  │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │
│   │   │    HR       │  │   SALES     │  │ MAINTENANCE │              │  │
│   │   │   META +    │  │   META +    │  │   META +    │              │  │
│   │   │   SCHEMA    │  │   SCHEMA    │  │   SCHEMA    │              │  │
│   │   └─────────────┘  └─────────────┘  └─────────────┘              │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│                                  ▼                                       │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                      GPT-4o-mini LLM                              │  │
│   │                                                                   │  │
│   │   System Prompt:                                                  │  │
│   │   "Analyze query against domain schemas..."                       │  │
│   │                                                                   │  │
│   │   Input: "Show me pending machine repairs"                        │  │
│   │                                                                   │  │
│   │   Output (JSON):                                                  │  │
│   │   {                                                               │  │
│   │     "domain": "sagar_db",                                         │  │
│   │     "reason": "Query mentions 'machine repairs' which matches     │  │
│   │               maintenance_task_assign table in sagar_db",         │  │
│   │     "clarification_question": ""                                  │  │
│   │   }                                                               │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│                    ┌─────────────┴─────────────┐                        │
│                    ▼                           ▼                        │
│              CLEAR MATCH                   AMBIGUOUS                    │
│                    │                           │                        │
│                    ▼                           ▼                        │
│         Return (domain_name,           Return ("AMBIGUOUS",             │
│                 reason, "")                   reason,                   │
│                                              clarification_q)           │
└─────────────────────────────────────────────────────────────────────────┘
                    │                           │
                    ▼                           ▼
           GET AGENT FOR DOMAIN          ASK USER TO CLARIFY
           Execute Workflow              Stream Question Back
```

### Routing Decision Flow

```
                        ┌─────────────────┐
                        │   User Query    │
                        └────────┬────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Analyze Against All   │
                    │   Database Schemas     │
                    └────────────┬───────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌───────────────────┐      ┌───────────────────┐
        │  Single DB Match  │      │  Multiple Matches │
        │  (Clear Intent)   │      │   (Ambiguous)     │
        └─────────┬─────────┘      └─────────┬─────────┘
                  │                          │
                  ▼                          ▼
        ┌───────────────────┐      ┌───────────────────┐
        │ Route to Specific │      │ Ask Clarification │
        │   Database Agent  │      │ "Did you mean     │
        │                   │      │  Lead Status or   │
        │ • checklist       │      │  Repair Status?"  │
        │ • lead_to_order   │      └─────────┬─────────┘
        │ • sagar_db        │                │
        └─────────┬─────────┘                ▼
                  │                 ┌───────────────────┐
                  │                 │  User Clarifies   │
                  │                 │  (e.g., "repair") │
                  │                 └─────────┬─────────┘
                  │                           │
                  │          ┌────────────────┘
                  ▼          ▼
        ┌───────────────────────────────────────────────┐
        │          CONTEXT FUSION                        │
        │   Merge: Original Query + Clarification        │
        │   "Show status" + "repair" → "Show repair      │
        │    status from sagar_db"                       │
        └───────────────────────────────────────────────┘
```

---

## 7. LangGraph Agent Workflow

### State Machine Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LANGGRAPH AGENT WORKFLOW                             │
│                           (6-Node State Machine)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌─────────┐                                     │
│                              │  START  │                                     │
│                              └────┬────┘                                     │
│                                   │                                          │
│                                   ▼                                          │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                        NODE 1: list_tables                             │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: Get available table names from database                      │ │
│   │  Tool: sql_db_list_tables                                              │ │
│   │  Output: ["users", "checklist", "delegation", ...]                     │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      NODE 2: call_get_schema                           │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: Fetch complete schema with column restrictions               │ │
│   │  Tool: sql_db_schema                                                   │ │
│   │  Adds:                                                                 │ │
│   │    • Column types & samples                                            │ │
│   │    • ALLOWED columns per table                                         │ │
│   │    • Data type warnings (TEXT dates need ::DATE cast)                  │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                       NODE 3: store_schema                             │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: Store schema in state, reset counters                        │ │
│   │  Actions:                                                              │ │
│   │    • schema_info = schema content                                      │ │
│   │    • original_question = user question                                 │ │
│   │    • validation_attempts = 0                                           │ │
│   │    • last_feedback = ""                                                │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      NODE 4: generate_query                            │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: LLM 1 generates SQL query                                    │ │
│   │  Model: gpt-4o-mini                                                    │ │
│   │  Input:                                                                │ │
│   │    • User question                                                     │ │
│   │    • Schema + restrictions                                             │ │
│   │    • Previous feedback (if retry)                                      │ │
│   │  Output: SQL Query via tool_call                                       │ │
│   │  Updates: validation_attempts += 1                                     │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                         ┌─────────────┴─────────────┐                       │
│                         │  should_validate_or_execute                       │
│                         │      (Conditional Edge)                           │
│                         └─────────────┬─────────────┘                       │
│                                       │                                      │
│               ┌───────────────────────┼───────────────────────┐             │
│               ▼                       │                       ▼             │
│   ┌───────────────────┐               │         ┌───────────────────┐       │
│   │ First Attempt OR  │               │         │ Max Attempts (3)  │       │
│   │ Has Feedback      │               │         │ Reached           │       │
│   └─────────┬─────────┘               │         └─────────┬─────────┘       │
│             │                         │                   │                  │
│             ▼                         │                   │                  │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                      NODE 5: validate_query                            │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: LLM 2 validates the generated query                          │ │
│   │  Model: gpt-4o-mini                                                    │ │
│   │  Checks:                                                               │ │
│   │    ✓ Only allowed columns used                                         │ │
│   │    ✓ UNION ALL structure correct                                       │ │
│   │    ✓ Pending/completed logic correct                                   │ │
│   │    ✓ Date filters present                                              │ │
│   │    ✓ LOWER() for case-insensitive                                      │ │
│   │    ✓ SELECT only (no INSERT/UPDATE/DELETE)                             │ │
│   │                                                                        │ │
│   │  Output (JSON):                                                        │ │
│   │  {                                                                     │ │
│   │    "status": "APPROVED" | "NEEDS_FIX",                                │ │
│   │    "confidence": 85,                                                   │ │
│   │    "errors": [...],                                                    │ │
│   │    "improvement_steps": [...]                                          │ │
│   │  }                                                                     │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                         ┌─────────────┴─────────────┐                       │
│                         │ should_regenerate_or_approve                      │
│                         │      (Conditional Edge)                           │
│                         └─────────────┬─────────────┘                       │
│                                       │                                      │
│               ┌───────────────────────┼───────────────────────┐             │
│               ▼                       │                       ▼             │
│   ┌───────────────────┐               │         ┌───────────────────┐       │
│   │    NEEDS_FIX      │               │         │     APPROVED      │       │
│   │  (has feedback)   │◄──────────────┘         │  (no feedback)    │       │
│   └─────────┬─────────┘                         └─────────┬─────────┘       │
│             │                                             │                  │
│             │ Loop back to                                │                  │
│             │ generate_query                              │                  │
│             │ (max 3 times)                               │                  │
│             ▼                                             ▼                  │
│   ┌───────────────────────────────────────────────────────────────────────┐ │
│   │                        NODE 6: run_query                               │ │
│   │────────────────────────────────────────────────────────────────────────│ │
│   │  Purpose: Execute SQL against PostgreSQL                               │ │
│   │  Actions:                                                              │ │
│   │    1. Security validation (SQL injection check)                        │ │
│   │    2. Execute query via sql_db_query tool                              │ │
│   │    3. Return results as ToolMessage                                    │ │
│   └───────────────────────────────────┬───────────────────────────────────┘ │
│                                       │                                      │
│                                       ▼                                      │
│                              ┌───────────┐                                   │
│                              │    END    │                                   │
│                              └───────────┘                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### State Definition

```python
class EnhancedState(MessagesState):
    """State tracked across all nodes"""
    
    validation_attempts: int = 0      # Counter for retry loop
    last_feedback: str = ""           # Validator feedback for regeneration
    schema_info: str = ""             # Cached schema for LLMs
    original_question: str = ""       # User's original question
```

---

## 8. Dual-LLM Validation Process

### Why Two LLMs?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DUAL-LLM VALIDATION SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        LLM 1: GENERATOR                              │   │
│   │                                                                      │   │
│   │   Role: Creative SQL Writer                                          │   │
│   │   Task: Convert natural language → SQL query                         │   │
│   │   Focus: Understanding intent, handling ambiguity                    │   │
│   │                                                                      │   │
│   │   ❌ May make mistakes:                                              │   │
│   │      • Use forbidden columns                                         │   │
│   │      • Forget UNION ALL                                              │   │
│   │      • Wrong date logic                                              │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        LLM 2: VALIDATOR                              │   │
│   │                                                                      │   │
│   │   Role: Critical Reviewer / Quality Gate                             │   │
│   │   Task: Check query against strict rules                             │   │
│   │   Focus: Accuracy, compliance, security                              │   │
│   │                                                                      │   │
│   │   ✅ Validates:                                                      │   │
│   │      • Column restrictions                                           │   │
│   │      • Query structure                                               │   │
│   │      • Business logic                                                │   │
│   │      • SQL best practices                                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   RESULT: Higher accuracy, fewer errors, self-correcting system             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Validation Loop Example

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          VALIDATION LOOP EXAMPLE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User: "Show me pending tasks in PC department this month"                   │
│                                                                              │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  ATTEMPT 1:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LLM 1 (Generator):                                                   │    │
│  │                                                                      │    │
│  │ SELECT * FROM checklist                                              │    │
│  │ WHERE department = 'PC'                                              │    │
│  │   AND status = 'pending'                                             │    │
│  │   AND task_start_date >= '2026-03-01';                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LLM 2 (Validator):                                                   │    │
│  │                                                                      │    │
│  │ ❌ ERROR: 'status' column is FORBIDDEN                               │    │
│  │ ❌ ERROR: Missing delegation table (need UNION ALL)                  │    │
│  │ ⚠️ WARNING: Use submission_date IS NULL for pending                  │    │
│  │                                                                      │    │
│  │ Status: NEEDS_FIX                                                    │    │
│  │ Confidence: 40%                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                              LOOP BACK WITH FEEDBACK                         │
│                                      │                                       │
│  ═══════════════════════════════════════════════════════════════════════════│
│                                                                              │
│  ATTEMPT 2:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LLM 1 (Generator) - WITH FEEDBACK:                                   │    │
│  │                                                                      │    │
│  │ SELECT name, department, task_description, task_start_date           │    │
│  │ FROM checklist                                                       │    │
│  │ WHERE LOWER(department) = 'pc'                                       │    │
│  │   AND submission_date IS NULL                                        │    │
│  │   AND task_start_date >= '2026-03-01'                                │    │
│  │ UNION ALL                                                            │    │
│  │ SELECT name, department, task_description, planned_date::DATE        │    │
│  │ FROM delegation                                                      │    │
│  │ WHERE LOWER(department) = 'pc'                                       │    │
│  │   AND submission_date IS NULL                                        │    │
│  │   AND planned_date::DATE >= '2026-03-01';                            │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ LLM 2 (Validator):                                                   │    │
│  │                                                                      │    │
│  │ ✅ Correct columns used                                              │    │
│  │ ✅ UNION ALL present                                                 │    │
│  │ ✅ Pending logic correct (submission_date IS NULL)                   │    │
│  │ ✅ LOWER() for case-insensitive                                      │    │
│  │ ✅ Date filter present                                               │    │
│  │                                                                      │    │
│  │ Status: APPROVED                                                     │    │
│  │ Confidence: 92%                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│                                      ▼                                       │
│                              EXECUTE QUERY ✅                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Complete Request Flow

### End-to-End Sequence Diagram

```
┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐
│  User  │      │Frontend│      │FastAPI │      │LangGraph│     │PostgreSQL│
└───┬────┘      └───┬────┘      └───┬────┘      └───┬────┘      └────┬────┘
    │               │               │               │                 │
    │ Type message  │               │               │                 │
    │──────────────>│               │               │                 │
    │               │               │               │                 │
    │               │ POST /chat/stream             │                 │
    │               │ {question, session_id}        │                 │
    │               │──────────────>│               │                 │
    │               │               │               │                 │
    │               │               │ Create/Get Session              │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │               │ Context Fusion (if clarification reply)
    │               │               │<───────────────────│            │
    │               │               │                    │            │
    │               │ SSE: status   │                    │            │
    │               │<──────────────│                    │            │
    │ 🧠 Routing... │               │                    │            │
    │<──────────────│               │                    │            │
    │               │               │                    │            │
    │               │               │ determine_database(query)       │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │               │ (GPT-4o-mini routes)            │
    │               │               │<───────────────────│            │
    │               │               │                    │            │
    │               │ SSE: status   │                    │            │
    │               │<──────────────│                    │            │
    │ 🔀 Routing to │               │                    │            │
    │   checklist   │               │                    │            │
    │<──────────────│               │                    │            │
    │               │               │                    │            │
    │               │               │ Check Cache (ChromaDB)          │
    │               │               │───────────────────>│            │
    │               │               │<───────────────────│            │
    │               │               │                    │            │
    │               │               │ (If CACHE MISS)    │            │
    │               │               │                    │            │
    │               │               │ get_agent_for_database()        │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │               │    ┌───────────────────────────┐│
    │               │               │    │     LANGGRAPH WORKFLOW    ││
    │               │               │    │                           ││
    │               │ SSE: status   │    │ 1. list_tables            ││
    │               │<──────────────│────│──────────────────────────>││
    │ 📊 Loading... │               │    │                           ││
    │<──────────────│               │    │ 2. call_get_schema        ││
    │               │               │    │────────────────────────────>│
    │               │ SSE: status   │    │                           ││
    │               │<──────────────│────│                           ││
    │ 🔍 Fetching   │               │    │ 3. store_schema           ││
    │   schema...   │               │    │                           ││
    │<──────────────│               │    │ 4. generate_query (LLM 1) ││
    │               │ SSE: status   │    │                           ││
    │               │<──────────────│────│                           ││
    │ 🤖 Generating │               │    │ 5. validate_query (LLM 2) ││
    │   query...    │               │    │                           ││
    │<──────────────│               │    │    ┌─── Loop if NEEDS_FIX ││
    │               │ SSE: query    │    │    │                      ││
    │               │<──────────────│────│<───┘                      ││
    │ [SQL Query]   │               │    │                           ││
    │<──────────────│               │    │ 6. run_query              ││
    │               │ SSE: status   │    │────────────────────────────>│
    │               │<──────────────│────│                           ││
    │ ⚡ Executing  │               │    │       Execute SQL         │|
    │<──────────────│               │    │<────────────────────────────│
    │               │               │    │       Results             ││
    │               │               │    └───────────────────────────┘│
    │               │               │                    │            │
    │               │               │ Answer Synthesis (LLM 3)        │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │ SSE: chunk (streaming)             │            │
    │               │<──────────────│<───────────────────│            │
    │ "There are   │               │                    │            │
    │  27 pending  │               │                    │            │
    │  tasks..."   │               │                    │            │
    │<──────────────│               │                    │            │
    │               │               │                    │            │
    │               │ SSE: chunk (technical note)        │            │
    │               │<──────────────│                    │            │
    │ "(Note:...)" │               │                    │            │
    │<──────────────│               │                    │            │
    │               │               │                    │            │
    │               │               │ Cache Query (ChromaDB)          │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │               │ Store Session Message           │
    │               │               │───────────────────>│            │
    │               │               │                    │            │
    │               │ SSE: done     │                    │            │
    │               │<──────────────│                    │            │
    │ ✅ Complete   │               │                    │            │
    │<──────────────│               │                    │            │
    │               │               │               │                 │
```

### Phase Summary

| Phase | Component | Action |
|-------|-----------|--------|
| 1 | Frontend | User types question, sends POST request |
| 2 | API Layer | Create/get session, store user message |
| 3 | Context | Check if this is a clarification reply |
| 4 | Router | AI determines target database |
| 5 | Cache | Check semantic cache for similar query |
| 6 | Agent | Run 6-node LangGraph workflow |
| 7 | Validation | Dual-LLM validation loop (max 3 attempts) |
| 8 | Execution | Run SQL against PostgreSQL |
| 9 | Synthesis | LLM generates natural language answer |
| 10 | Streaming | SSE streams answer word-by-word |
| 11 | Caching | Cache successful query for future |
| 12 | Session | Store bot response in session |

---

## 10. API Documentation

### Authentication

#### POST `/auth/login`

Authenticate user and receive access.

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful"
}
```

---

### Chat

#### POST `/chat/stream`

Main chat endpoint with Server-Sent Events (SSE) streaming.

**Request:**
```json
{
  "question": "Show me pending tasks this month",
  "session_id": "optional-uuid"
}
```

**Response (SSE Stream):**
```
data: {"type": "status", "message": "🧠 Router Logic: ..."}

data: {"type": "status", "message": "🔀 Routing to checklist database..."}

data: {"type": "cache_hit", "value": false}

data: {"type": "status", "message": "🔄 Analyzing checklist schema..."}

data: {"type": "status", "message": "🤖 LLM 1: Generating query..."}

data: {"type": "query", "content": "SELECT ... FROM checklist ..."}

data: {"type": "status", "message": "🔍 LLM 2: Validating query..."}

data: {"type": "status", "message": "✅ Query approved!"}

data: {"type": "status", "message": "⚡ Executing query..."}

data: {"type": "status", "message": "💬 Generating answer..."}

data: {"type": "chunk", "content": "There "}

data: {"type": "chunk", "content": "are "}

data: {"type": "chunk", "content": "27 "}

data: {"type": "chunk", "content": "pending "}

data: {"type": "chunk", "content": "tasks..."}

data: {"type": "done"}
```

**SSE Event Types:**

| Type | Description |
|------|-------------|
| `status` | Progress update message |
| `cache_hit` | Whether cache was used (true/false) |
| `query` | Generated SQL query |
| `chunk` | Streaming answer content |
| `error` | Error message |
| `done` | Completion signal |

---

#### GET `/chat/cache/stats`

Get cache statistics.

**Response:**
```json
{
  "total_entries": 150,
  "cache_hits": 89,
  "cache_misses": 61,
  "hit_rate": 0.593,
  "similarity_threshold": 0.95,
  "enabled": true
}
```

---

#### POST `/chat/cache/clear`

Clear all cached queries.

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared"
}
```

---

### Sessions

#### GET `/chat/sessions`

List all chat sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "abc123",
      "title": "Pending tasks query",
      "created_at": "2026-03-30T08:00:00Z",
      "updated_at": "2026-03-30T08:15:00Z"
    }
  ]
}
```

---

#### GET `/chat/sessions/{session_id}/messages`

Get messages for a session.

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Show pending tasks",
      "timestamp": "2026-03-30T08:00:00Z"
    },
    {
      "role": "assistant", 
      "content": "There are 27 pending tasks...",
      "timestamp": "2026-03-30T08:00:05Z"
    }
  ]
}
```

---

#### DELETE `/chat/sessions/{session_id}`

Delete a chat session.

**Response:**
```json
{
  "status": "success",
  "message": "Session deleted"
}
```

---

### Health

#### GET `/`

API information.

**Response:**
```json
{
  "name": "DB Assistant API",
  "version": "2.0.0",
  "status": "active",
  "features": [
    "Dual-LLM Validation",
    "Human-in-the-Loop",
    "Streaming Responses",
    "Session Management",
    "Hardcoded Security"
  ]
}
```

---

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 11. Frontend Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND UI                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        LOGIN OVERLAY                                 │   │
│   │                                                                      │   │
│   │   ┌─────────────────────────────────────────────────────────────┐   │   │
│   │   │  [Logo]                                                      │   │   │
│   │   │                                                              │   │   │
│   │   │  Admin Login                                                 │   │   │
│   │   │  ──────────────────────                                      │   │   │
│   │   │  [Email/Username    ]                                        │   │   │
│   │   │  [Password          ]                                        │   │   │
│   │   │  [       Login      ]                                        │   │   │
│   │   │                                                              │   │   │
│   │   │  Powered by Botivate                                         │   │   │
│   │   └─────────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         MAIN APP                                     │   │
│   │                                                                      │   │
│   │   ┌─────────────┐  ┌─────────────────────────────────────────────┐  │   │
│   │   │   SIDEBAR   │  │              MAIN CONTENT                    │  │   │
│   │   │             │  │                                              │  │   │
│   │   │  [Logo]     │  │  ┌───────────────────────────────────────┐  │  │   │
│   │   │  [+ New]    │  │  │              HEADER                    │  │  │   │
│   │   │             │  │  │  [≡] [Logo] [Clear] [Delete]           │  │  │   │
│   │   │  Sessions:  │  │  └───────────────────────────────────────┘  │  │   │
│   │   │  ─────────  │  │                                              │  │   │
│   │   │  □ Session1 │  │  ┌───────────────────────────────────────┐  │  │   │
│   │   │  □ Session2 │  │  │           CHAT DISPLAY                 │  │  │   │
│   │   │  □ Session3 │  │  │                                        │  │  │   │
│   │   │             │  │  │  ┌─────────────────────────────────┐   │  │  │   │
│   │   │             │  │  │  │     WELCOME SCREEN              │   │  │  │   │
│   │   │             │  │  │  │  ○ (animated orb)               │   │  │  │   │
│   │   │             │  │  │  │  "Hello! I'm your AI..."        │   │  │  │   │
│   │   │             │  │  │  └─────────────────────────────────┘   │  │  │   │
│   │   │             │  │  │                                        │  │  │   │
│   │   │             │  │  │  ┌─────────────────────────────────┐   │  │  │   │
│   │   │             │  │  │  │ User: Show pending tasks        │   │  │  │   │
│   │   │             │  │  │  └─────────────────────────────────┘   │  │  │   │
│   │   │             │  │  │                                        │  │  │   │
│   │   │             │  │  │  ┌─────────────────────────────────┐   │  │  │   │
│   │   │             │  │  │  │ 🤖 There are 27 pending tasks...│   │  │  │   │
│   │   │             │  │  │  │ (typing animation)              │   │  │  │   │
│   │   │             │  │  │  └─────────────────────────────────┘   │  │  │   │
│   │   │             │  │  │                                        │  │  │   │
│   │   │─────────────│  │  └───────────────────────────────────────┘  │  │   │
│   │   │             │  │                                              │  │   │
│   │   │ [Cache Stats]│  │  ┌───────────────────────────────────────┐  │  │   │
│   │   │ [Logout]    │  │  │           INPUT FOOTER                 │  │  │   │
│   │   │             │  │  │  ┌─────────────────────────────────┐   │  │  │   │
│   │   └─────────────┘  │  │  │ Ask anything...              [↑]│   │  │  │   │
│   │                    │  │  └─────────────────────────────────┘   │  │  │   │
│   │                    │  │  [Session: New Session]                 │  │  │   │
│   │                    │  │  Powered by Botivate                    │  │  │   │
│   │                    │  └───────────────────────────────────────┘  │  │   │
│   │                    └─────────────────────────────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Implementation |
|---------|----------------|
| **SSE Streaming** | EventSource API for real-time responses |
| **Markdown Rendering** | marked.js library |
| **Session Persistence** | LocalStorage + API sync |
| **Typing Animation** | Word-by-word display with delay |
| **Responsive Design** | Mobile-friendly sidebar |
| **Cache Indicator** | Shows ⚡ when using cached query |

---

## 12. Services & Components

### Cache Service (`cache_service.py`)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SEMANTIC CACHE (ChromaDB)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Purpose: Cache similar queries to avoid redundant LLM calls        │
│                                                                      │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │                    CACHE WORKFLOW                              │ │
│   │                                                                │ │
│   │   New Query: "Show pending tasks"                              │ │
│   │                     │                                          │ │
│   │                     ▼                                          │ │
│   │   ┌─────────────────────────────────────────────────────────┐ │ │
│   │   │         EMBEDDING GENERATION (OpenAI)                    │ │ │
│   │   │                                                          │ │ │
│   │   │   "Show pending tasks" → [0.123, -0.456, 0.789, ...]    │ │ │
│   │   └────────────────────────────┬────────────────────────────┘ │ │
│   │                                │                               │ │
│   │                                ▼                               │ │
│   │   ┌─────────────────────────────────────────────────────────┐ │ │
│   │   │          SIMILARITY SEARCH (ChromaDB)                    │ │ │
│   │   │                                                          │ │ │
│   │   │   Compare against cached embeddings                      │ │ │
│   │   │   Threshold: 95% similarity                              │ │ │
│   │   └────────────────────────────┬────────────────────────────┘ │ │
│   │                                │                               │ │
│   │              ┌─────────────────┴─────────────────┐            │ │
│   │              ▼                                   ▼            │ │
│   │   ┌─────────────────┐               ┌─────────────────┐       │ │
│   │   │   CACHE HIT     │               │  CACHE MISS     │       │ │
│   │   │   (≥95% match)  │               │  (<95% match)   │       │ │
│   │   └────────┬────────┘               └────────┬────────┘       │ │
│   │            │                                  │                │ │
│   │            ▼                                  ▼                │ │
│   │   Return cached SQL                  Run full LangGraph       │ │
│   │   Execute directly                   workflow, cache result   │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   Storage: Per-database scoping (checklist, lead_to_order, sagar_db)│
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Context Manager (`context_manager.py`)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CONTEXT MANAGER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Purpose: Track conversation context for follow-up questions        │
│                                                                      │
│   Features:                                                          │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  1. ENTITY EXTRACTION                                          │ │
│   │     "Show John's tasks" → stores { name: "John" }              │ │
│   │                                                                │ │
│   │  2. PRONOUN RESOLUTION                                         │ │
│   │     Previous: "Show John's tasks"                              │ │
│   │     Current: "What about his pending ones?"                    │ │
│   │     Resolved: "What about John's pending tasks?"               │ │
│   │                                                                │ │
│   │  3. TABLE/COLUMN TRACKING                                      │ │
│   │     Remembers which tables were queried                        │ │
│   │                                                                │ │
│   │  4. CLARIFICATION FUSION                                       │ │
│   │     Original: "Show status"                                    │ │
│   │     Clarification: "Lead status"                               │ │
│   │     Fused: "Show status (Context: Lead status)"                │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Session Manager (`session_manager.py`)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SESSION MANAGER (SQLite)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Database: chat_sessions.db                                         │
│                                                                      │
│   Tables:                                                            │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  sessions                                                      │ │
│   │  ─────────────────────────────────────────────────────────────│ │
│   │  session_id    VARCHAR(36)  PRIMARY KEY                       │ │
│   │  title         VARCHAR(255)                                   │ │
│   │  created_at    TIMESTAMP                                      │ │
│   │  updated_at    TIMESTAMP                                      │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  messages                                                      │ │
│   │  ─────────────────────────────────────────────────────────────│ │
│   │  id            INTEGER      PRIMARY KEY AUTOINCREMENT         │ │
│   │  session_id    VARCHAR(36)  FOREIGN KEY                       │ │
│   │  role          VARCHAR(20)  ('user' | 'assistant')            │ │
│   │  content       TEXT                                           │ │
│   │  timestamp     TIMESTAMP                                      │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
│   Operations:                                                        │
│   • create_session(session_id, title)                               │
│   • get_sessions() → List[Session]                                  │
│   • get_session_messages(session_id) → List[Message]                │
│   • add_message(session_id, role, content)                          │
│   • delete_session(session_id)                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 13. Security Features

### SQL Injection Prevention (`security.py`)

```
┌─────────────────────────────────────────────────────────────────────┐
│                       SECURITY VALIDATION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Function: validate_sql_security(query)                             │
│   Returns: (is_valid: bool, error_msg: str, sanitized_query: str)   │
│                                                                      │
│   Checks:                                                            │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │                                                                │ │
│   │  ✓ STATEMENT TYPE                                              │ │
│   │    Only SELECT and WITH allowed                                │ │
│   │    ❌ INSERT, UPDATE, DELETE, DROP, TRUNCATE                   │ │
│   │                                                                │ │
│   │  ✓ QUERY LENGTH                                                │ │
│   │    Maximum: 50,000 characters                                  │ │
│   │                                                                │ │
│   │  ✓ MULTIPLE STATEMENTS                                         │ │
│   │    ❌ No semicolons in middle of query                         │ │
│   │                                                                │ │
│   │  ✓ INJECTION PATTERNS                                          │ │
│   │    ❌ -- (SQL comment)                                         │ │
│   │    ❌ /* */ (block comment)                                    │ │
│   │    ❌ UNION SELECT (injection attempt)                         │ │
│   │    ❌ OR 1=1, OR 'a'='a'                                       │ │
│   │    ❌ xp_, sp_ (stored procedures)                             │ │
│   │    ❌ EXEC, EXECUTE                                            │ │
│   │                                                                │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Column Restrictions

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COLUMN-LEVEL SECURITY                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Each table has explicitly defined ALLOWED columns.                 │
│   The Validator LLM enforces these restrictions.                     │
│                                                                      │
│   Example (checklist table):                                         │
│   ┌───────────────────────────────────────────────────────────────┐ │
│   │  ALLOWED:                                                      │ │
│   │  • name                                                        │ │
│   │  • department                                                  │ │
│   │  • task_description                                            │ │
│   │  • frequency                                                   │ │
│   │  • task_start_date                                             │ │
│   │  • submission_date                                             │ │
│   │                                                                │ │
│   │  FORBIDDEN:                                                    │ │
│   │  ❌ status (use submission_date IS NULL instead)               │ │
│   │  ❌ id, created_at, internal fields                            │ │
│   └───────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 14. Configuration Guide

### Environment Variables (`.env`)

```properties
# ═══════════════════════════════════════════════════════════════════
# LLM CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
OPENAI_API_KEY=sk-...your-api-key...
MODEL_NAME=gpt-4o-mini

# ═══════════════════════════════════════════════════════════════════
# DATABASE CONNECTION (SINGLE DATABASE)
# ═══════════════════════════════════════════════════════════════════

# All domains share ONE database connection
DATABASE_URL=postgresql://user:pass@host:5432/main_database

# OR use component-style:
DB_HOST=your-db-host.rds.amazonaws.com
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=main_database
DB_PORT=5432

# ═══════════════════════════════════════════════════════════════════
# VALIDATION SETTINGS
# ═══════════════════════════════════════════════════════════════════
MAX_VALIDATION_ATTEMPTS=3        # Max LLM retry loops
CONFIDENCE_THRESHOLD=70          # Min confidence to approve

# ═══════════════════════════════════════════════════════════════════
# CACHE SETTINGS
# ═══════════════════════════════════════════════════════════════════
CACHE_SIMILARITY_THRESHOLD=0.95  # 95% similarity for cache hit
```

### Settings Class (`config.py`)

```python
class Settings(BaseSettings):
    # App
    APP_NAME: str = "DB Assistant API"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    
    # ═══════════════════════════════════════════════════════════════
    # SINGLE DATABASE - All domains connect to ONE database
    # ═══════════════════════════════════════════════════════════════
    DATABASE_URL: str  # Primary connection string
    
    # Legacy aliases (for backwards compatibility)
    # These all return DATABASE_URL
    @property
    def DB_CHECKLIST_URL(self) -> str:
        return self.DATABASE_URL
    
    @property
    def DB_LEAD_TO_ORDER_URL(self) -> str:
        return self.DATABASE_URL
    
    @property
    def DB_SAGAR_URL(self) -> str:
        return self.DATABASE_URL
    
    # Security
    MAX_QUERY_LENGTH: int = 50000
    MAX_RESULT_ROWS: int = 200
    
    # Validation
    MAX_VALIDATION_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: int = 70
```

### Domain Configuration (per domain)

Each domain module (`app/domains/<domain>/config.py`) defines:

```python
# Example: checklist/config.py

ALLOWED_TABLES = [
    "users", "checklist", "delegation", "leave_request",
    "visitors", "ticket_book", "request", "resume_request",
    # ... more tables
]

ALLOWED_COLUMNS = {
    "users": ["user_name", "department", "role", "email_id", "status"],
    "checklist": ["name", "department", "task_description", "submission_date", "status"],
    # ... per-table column restrictions
}

ROUTER_METADATA = {
    "name": "checklist",
    "description": "HR & Employee Operations...",
    "keywords": ["employee", "task", "leave", "visitor", ...],
}
```

---

## 15. Deployment

### Local Development

```bash
# 1. Clone repository
git clone <repo_url>
cd Sagar_tmt_DB_assistant

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
cd Backend_New
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# 5. Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 6. Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Frontend: http://localhost:8000/app
```

### Production Deployment

```bash
# Using Gunicorn with Uvicorn workers
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📊 Quick Reference

### System Stats

| Metric | Value |
|--------|-------|
| Total Databases | 3 |
| Total Tables | 13+ |
| API Endpoints | 10+ |
| LLM Calls per Query | 2-4 |
| Max Validation Attempts | 3 |
| Cache Similarity | 95% |

### Technology Summary

| Layer | Technologies |
|-------|-------------|
| Frontend | HTML, CSS, JS, SSE |
| API | FastAPI, Pydantic |
| Agent | LangChain, LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Database | PostgreSQL |
| Cache | ChromaDB |
| Sessions | SQLite |

---

**Document Version:** 1.0  
**Last Updated:** March 2026  
**Author:** System Documentation Generator
