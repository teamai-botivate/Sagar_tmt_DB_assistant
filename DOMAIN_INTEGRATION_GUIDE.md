# 🔌 Domain Integration Guide

**Version:** 2.2  
**Last Updated:** March 2026  
**Purpose:** Step-by-step guide to add new business domains to the DB Assistant

---

## 📋 Overview

This guide explains how to add a new **domain** (logical grouping of tables) to the Sagar TMT DB Assistant. Since all domains share a **single PostgreSQL database**, adding a new domain only requires:

1. Creating a domain module folder
2. Defining allowed tables and columns
3. Writing domain-specific prompts
4. Registering in the router

**No database migrations or new connections needed!**

---

## 🏗️ Architecture Recap

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE PostgreSQL DATABASE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│   │  HR DOMAIN      │  │  SALES DOMAIN   │  │  YOUR NEW      │  │
│   │  (checklist/)   │  │ (lead_to_order/)│  │  DOMAIN        │  │
│   │                 │  │                 │  │                │  │
│   │  18 tables      │  │  4 tables       │  │  N tables      │  │
│   └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                  │
│   Each domain sees ONLY its ALLOWED_TABLES                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Step 1: Create Domain Module Folder

Create a new folder under `Backend_New/app/domains/`:

```
Backend_New/
└── app/
    └── domains/
        ├── hr_operations/       # Existing
        ├── sales_crm/           # Existing
        ├── maintenance/         # Existing
        └── your_domain/         # NEW
            ├── __init__.py
            ├── config.py
            ├── connection.py
            ├── prompts.py
            └── workflow.py
```

---

## 📝 Step 2: Define Configuration (`config.py`)

```python
"""
Your Domain - Configuration

Domain Purpose: [Brief description of what this domain handles]
Tables: [List of tables]
"""

# ═══════════════════════════════════════════════════════════════════
# ALLOWED TABLES (Domain Isolation)
# ═══════════════════════════════════════════════════════════════════

ALLOWED_TABLES = [
    "your_table_1",
    "your_table_2",
    "your_table_3",
]

# ═══════════════════════════════════════════════════════════════════
# ALLOWED COLUMNS (Column-Level Security)
# ═══════════════════════════════════════════════════════════════════

ALLOWED_COLUMNS = {
    "your_table_1": [
        "column_a",
        "column_b",
        "column_c",
        # DO NOT include sensitive columns like passwords
    ],
    "your_table_2": [
        "column_x",
        "column_y",
    ],
}

# ═══════════════════════════════════════════════════════════════════
# ROUTER METADATA (For AI Routing)
# ═══════════════════════════════════════════════════════════════════

ROUTER_METADATA = {
    "name": "your_domain",
    "description": """
    [Domain Name] Management System - handles [purpose].
    
    Use this domain for queries about:
    - [Topic 1]
    - [Topic 2]
    - [Topic 3]
    
    DO NOT use for: [Topics that belong to other domains]
    """,
    "keywords": [
        "keyword1",
        "keyword2",
        # Add domain-specific keywords that help routing
    ],
}

# ═══════════════════════════════════════════════════════════════════
# SEMANTIC SCHEMA (Human-Readable for LLM)
# ═══════════════════════════════════════════════════════════════════

SEMANTIC_SCHEMA = """
=== YOUR_DOMAIN TABLES ===

TABLE: your_table_1
PURPOSE: [What this table stores]
COLUMNS:
  - column_a (VARCHAR): [Description]
  - column_b (INTEGER): [Description]
  - column_c (TIMESTAMP): [Description]

BUSINESS RULES:
  - [Rule 1]
  - [Rule 2]

EXAMPLE QUERIES:
  Q: "Show all items from last week"
  SQL: SELECT * FROM your_table_1 WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
"""
```

---

## 📝 Step 3: Create Connection Handler (`connection.py`)

```python
"""
Your Domain - Database Connection

All domains share the same DATABASE_URL.
Domain isolation is achieved via ALLOWED_TABLES filtering.
"""

from langchain_community.utilities import SQLDatabase
from app.core.config import settings
from .config import ALLOWED_TABLES

# ═══════════════════════════════════════════════════════════════════
# RESTRICTED DATABASE CLASS
# ═══════════════════════════════════════════════════════════════════

class RestrictedSQLDatabase(SQLDatabase):
    """
    Wraps SQLDatabase to only expose ALLOWED_TABLES.
    The agent cannot see or query tables outside this list.
    """
    
    def __init__(self, *args, include_tables=None, **kwargs):
        super().__init__(*args, include_tables=include_tables, **kwargs)
        self._allowed_tables = set(include_tables or [])
    
    def get_table_names(self):
        """Only return allowed tables."""
        all_tables = super().get_table_names()
        return [t for t in all_tables if t in self._allowed_tables]

# ═══════════════════════════════════════════════════════════════════
# DATABASE INSTANCE FACTORY
# ═══════════════════════════════════════════════════════════════════

_db_instance = None

def get_db_instance():
    """
    Returns a RestrictedSQLDatabase that only sees this domain's tables.
    Uses shared DATABASE_URL with table filtering.
    """
    global _db_instance
    
    if _db_instance is None:
        _db_instance = RestrictedSQLDatabase.from_uri(
            settings.DATABASE_URL,  # Shared connection
            include_tables=ALLOWED_TABLES,  # Domain isolation
            sample_rows_in_table_info=3,
            view_support=True,
        )
    
    return _db_instance
```

---

## 📝 Step 4: Create Prompts (`prompts.py`)

```python
"""
Your Domain - LLM Prompts

Three key prompts:
1. GENERATOR_PROMPT - Creates SQL from natural language
2. VALIDATOR_PROMPT - Validates SQL against rules
3. ANSWER_PROMPT - Synthesizes human-readable answers
"""

from .config import SEMANTIC_SCHEMA, ALLOWED_COLUMNS

# ═══════════════════════════════════════════════════════════════════
# SQL GENERATOR PROMPT
# ═══════════════════════════════════════════════════════════════════

GENERATOR_PROMPT = f"""
You are a PostgreSQL expert for the [Domain Name] system.

DATABASE SCHEMA:
{SEMANTIC_SCHEMA}

STRICT RULES:
1. ONLY use tables: {list(ALLOWED_COLUMNS.keys())}
2. ONLY use columns explicitly listed in ALLOWED_COLUMNS
3. Use LOWER() for all string comparisons
4. Return ONLY the SQL query, no explanations

Generate a PostgreSQL query for the user's question.
"""

# ═══════════════════════════════════════════════════════════════════
# SQL VALIDATOR PROMPT
# ═══════════════════════════════════════════════════════════════════

VALIDATOR_PROMPT = f"""
You are a SQL query validator for the [Domain Name] system.

ALLOWED TABLES AND COLUMNS:
{ALLOWED_COLUMNS}

VALIDATION RULES:
1. Query must ONLY use allowed tables
2. Query must ONLY use allowed columns
3. All string comparisons must use LOWER()
4. SELECT only, no INSERT/UPDATE/DELETE

If valid, respond with:
{{"status": "APPROVED", "confidence": 85}}

If invalid, respond with:
{{"status": "NEEDS_FIX", "reason": "...", "suggested_fix": "..."}}
"""

# ═══════════════════════════════════════════════════════════════════
# ANSWER SYNTHESIZER PROMPT
# ═══════════════════════════════════════════════════════════════════

ANSWER_PROMPT = """
You are a helpful assistant presenting database results.

Given the SQL query and results, provide a clear, human-readable answer.
If the result is empty, explain what was searched and that no matches were found.

Format tables nicely using markdown.
"""
```

---

## 📝 Step 5: Create Workflow (`workflow.py`)

```python
"""
Your Domain - LangGraph Workflow

6-node state machine for query processing:
list_tables → get_schema → store_schema → generate_query → validate_query → run_query
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from app.core.config import settings
from .connection import get_db_instance
from .prompts import GENERATOR_PROMPT, VALIDATOR_PROMPT, ANSWER_PROMPT
from .config import ALLOWED_TABLES

# ═══════════════════════════════════════════════════════════════════
# STATE DEFINITION
# ═══════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    question: str
    tables: List[str]
    schema: str
    generated_sql: str
    validation_result: dict
    sql_result: str
    answer: str
    attempt_count: int

# ═══════════════════════════════════════════════════════════════════
# NODE IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════

def list_tables(state: AgentState) -> AgentState:
    """List allowed tables for this domain."""
    db = get_db_instance()
    state["tables"] = db.get_table_names()
    return state

def get_schema(state: AgentState) -> AgentState:
    """Get schema for allowed tables."""
    db = get_db_instance()
    state["schema"] = db.get_table_info(table_names=state["tables"])
    return state

def generate_query(state: AgentState) -> AgentState:
    """Generate SQL using LLM."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
    
    prompt = f"{GENERATOR_PROMPT}\n\nQuestion: {state['question']}"
    response = llm.invoke(prompt)
    state["generated_sql"] = response.content.strip()
    state["attempt_count"] = state.get("attempt_count", 0) + 1
    return state

def validate_query(state: AgentState) -> AgentState:
    """Validate SQL using separate LLM."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
    
    prompt = f"{VALIDATOR_PROMPT}\n\nSQL: {state['generated_sql']}"
    response = llm.invoke(prompt)
    
    # Parse response (simplified)
    if "APPROVED" in response.content:
        state["validation_result"] = {"status": "APPROVED"}
    else:
        state["validation_result"] = {"status": "NEEDS_FIX", "feedback": response.content}
    
    return state

def run_query(state: AgentState) -> AgentState:
    """Execute validated SQL."""
    db = get_db_instance()
    try:
        state["sql_result"] = db.run(state["generated_sql"])
    except Exception as e:
        state["sql_result"] = f"Error: {str(e)}"
    return state

def generate_answer(state: AgentState) -> AgentState:
    """Generate human-readable answer."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0)
    
    prompt = f"""{ANSWER_PROMPT}
    
Question: {state['question']}
SQL: {state['generated_sql']}
Result: {state['sql_result']}
"""
    response = llm.invoke(prompt)
    state["answer"] = response.content
    return state

# ═══════════════════════════════════════════════════════════════════
# ROUTING LOGIC
# ═══════════════════════════════════════════════════════════════════

def should_retry(state: AgentState) -> str:
    """Decide whether to retry generation or proceed."""
    if state["validation_result"]["status"] == "APPROVED":
        return "run_query"
    elif state["attempt_count"] >= settings.MAX_VALIDATION_ATTEMPTS:
        return "run_query"  # Give up and try anyway
    else:
        return "generate_query"  # Retry

# ═══════════════════════════════════════════════════════════════════
# BUILD WORKFLOW GRAPH
# ═══════════════════════════════════════════════════════════════════

def build_workflow():
    """Construct the LangGraph workflow."""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("list_tables", list_tables)
    workflow.add_node("get_schema", get_schema)
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("validate_query", validate_query)
    workflow.add_node("run_query", run_query)
    workflow.add_node("generate_answer", generate_answer)
    
    # Add edges
    workflow.set_entry_point("list_tables")
    workflow.add_edge("list_tables", "get_schema")
    workflow.add_edge("get_schema", "generate_query")
    workflow.add_edge("generate_query", "validate_query")
    workflow.add_conditional_edges("validate_query", should_retry)
    workflow.add_edge("run_query", "generate_answer")
    workflow.add_edge("generate_answer", END)
    
    return workflow.compile()

# Export
compiled_workflow = build_workflow()
```

---

## 📝 Step 6: Register in Router

Edit `Backend_New/app/core/router.py`:

```python
# Add import
from app.databases.your_domain.config import (
    ROUTER_METADATA as YOUR_DOMAIN_META,
    SEMANTIC_SCHEMA as YOUR_DOMAIN_SCHEMA,
)
from app.databases.your_domain.workflow import compiled_workflow as your_domain_workflow

# Add to REGISTERED_DOMAINS list
REGISTERED_DOMAINS = [
    (CHECKLIST_META, CHECKLIST_SCHEMA),
    (L2O_META, L2O_SCHEMA),
    (SAGAR_META, SAGAR_SCHEMA),
    (YOUR_DOMAIN_META, YOUR_DOMAIN_SCHEMA),  # NEW
]

# Add to get_agent_for_database()
def get_agent_for_database(db_name: str):
    if db_name == "checklist":
        return checklist_workflow
    elif db_name == "lead_to_order":
        return l2o_workflow
    elif db_name == "sagar_db":
        return sagar_workflow
    elif db_name == "your_domain":  # NEW
        return your_domain_workflow
    else:
        raise ValueError(f"Unknown domain: {db_name}")
```

---

## 📝 Step 7: Create `__init__.py`

```python
"""
Your Domain Module

Handles [domain purpose] queries.
"""

from .workflow import compiled_workflow
from .connection import get_db_instance
from .config import ALLOWED_TABLES, ROUTER_METADATA

__all__ = [
    "compiled_workflow",
    "get_db_instance",
    "ALLOWED_TABLES",
    "ROUTER_METADATA",
]
```

---

## ✅ Verification Checklist

After adding your domain:

- [ ] Tables exist in the shared database
- [ ] `ALLOWED_TABLES` lists all required tables
- [ ] `ALLOWED_COLUMNS` excludes sensitive data
- [ ] `ROUTER_METADATA` clearly describes the domain
- [ ] Router imports and registers the domain
- [ ] Workflow compiles without errors

**Test commands:**

```bash
# Start backend
cd Backend_New
uvicorn main:app --reload

# Test routing
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Show data from your_domain", "session_id": "test"}'
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Table not found" | Add to `ALLOWED_TABLES` in domain config |
| Wrong domain selected | Improve `ROUTER_METADATA` description and keywords |
| Mixed-case column errors | Quote column names: `"Column_Name"` |
| Import errors | Check `__init__.py` exports |

---

## 📚 Related Documentation

- [README.md](README.md) — Project overview
- [SYSTEM_DOCUMENTATION.md](SYSTEM_DOCUMENTATION.md) — Full architecture details
- [BACKEND_NEW_WORKFLOW.md](BACKEND_NEW_WORKFLOW.md) — LangGraph workflow details
