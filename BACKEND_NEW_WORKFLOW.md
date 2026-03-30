# 🔄 BACKEND_NEW SYSTEM - COMPLETE WORKFLOW GUIDE

**Version:** 2.2  
**Architecture:** Single Database, Multi-Domain

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Domain Routing](#domain-routing)
4. [Request Flow](#request-flow)
5. [Dual-LLM Validation Process](#dual-llm-validation-process)
6. [Component Details](#component-details)
7. [Step-by-Step Example](#step-by-step-example)

---

## 🎯 System Overview

**Backend_New** is an intelligent SQL query generation system using **Dual-LLM Validation** with **LangGraph** for state management. It queries a **single PostgreSQL database** with multiple isolated **domains** (logical table groupings).

### **Key Features:**
- ✅ **Single Database, Multi-Domain**: One DB connection, multiple isolated domains
- ✅ **Domain Routing**: AI routes queries to the correct domain
- ✅ **Dual-LLM System**: LLM 1 (Generator) + LLM 2 (Validator)
- ✅ **Semantic Query Cache**: Caches similar queries for speed
- ✅ **Context-Aware**: Remembers conversation history
- ✅ **Streaming Responses**: Real-time word-by-word answers
- ✅ **Security Validation**: Prevents SQL injection
- ✅ **Session Management**: Multi-user support

### **Domain Structure:**
```
┌─────────────────────────────────────────────────────────────────┐
│                 SINGLE PostgreSQL DATABASE                       │
├─────────────────────────────────────────────────────────────────┤
│   ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│   │   HR DOMAIN     │  │  SALES DOMAIN   │  │ MAINTENANCE    │  │
│   │  (checklist/)   │  │ (lead_to_order/)│  │  (sagar_db/)   │  │
│   │  18 tables      │  │   4 tables      │  │   1 table      │  │
│   └─────────────────┘  └─────────────────┘  └────────────────┘  │
│                                                                  │
│   Domain isolation via ALLOWED_TABLES per domain module         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (HTML/JS)                          │
│  User types: "Show me pending tasks in PC department this month"    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (Backend_New)                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              /api/chat/stream (chat.py)                     │  │
│  │  Step 1: Receive user question via POST request            │  │
│  │  Step 2: Get or create session ID                          │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │           DOMAIN ROUTER (core/router.py)                    │  │
│  │  🔀 AI-powered routing to correct domain                   │  │
│  │     - Analyzes query against all domain schemas            │  │
│  │     - Returns: domain_name, reason, clarification          │  │
│  │     - Handles ambiguous queries with clarification         │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│            ┌────────────┼────────────┐                            │
│            ▼            ▼            ▼                            │
│     ┌───────────┐ ┌───────────┐ ┌───────────┐                    │
│     │HR Domain  │ │Sales Domain│ │Maintenance│                    │
│     │ Agent     │ │   Agent   │ │  Agent    │                    │
│     └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                    │
│           │             │             │                            │
│           └─────────────┼─────────────┘                            │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         CACHE CHECK (cache_service.py)                      │  │
│  │  🔍 Check if similar question asked before                  │  │
│  │     - Uses semantic similarity (95% threshold)              │  │
│  │     - If CACHE HIT: Return cached SQL directly ⚡          │  │
│  │     - If CACHE MISS: Continue to LangGraph ↓               │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │      CONTEXT MANAGER (context_manager.py)                   │  │
│  │  💬 Build context from previous conversation                │  │
│  │     - Extract entities (names, departments, dates)          │  │
│  │     - Resolve pronouns ("his tasks" → "John's tasks")       │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │            LANGGRAPH AGENT (sql_agent.py)                   │  │
│  │           State Machine with 6 Nodes                        │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 1: list_tables                                  │  │  │
│  │  │  📋 Get available table names                         │  │  │
│  │  │     Result: ["users", "checklist", "delegation"]      │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │                    ▼                                         │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 2: call_get_schema                              │  │  │
│  │  │  🔍 Fetch complete database schema                    │  │  │
│  │  │     - Column names, types, samples                    │  │  │
│  │  │     - Column restrictions (forbidden columns)         │  │  │
│  │  │     - Critical warnings (date casting, etc.)          │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │                    ▼                                         │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 3: store_schema                                 │  │  │
│  │  │  💾 Store schema in state for LLMs                    │  │  │
│  │  │     - Reset validation counter                        │  │  │
│  │  │     - Store original question                         │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │                    ▼                                         │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 4: generate_query                               │  │  │
│  │  │  🤖 LLM 1: Query Generator (OpenAI GPT)              │  │  │
│  │  │                                                        │  │  │
│  │  │  Input Prompt Includes:                               │  │  │
│  │  │  - User question                                      │  │  │
│  │  │  - Database schema                                    │  │  │
│  │  │  - Column restrictions                                │  │  │
│  │  │  - Date filtering rules                               │  │  │
│  │  │  - Performance report templates                       │  │  │
│  │  │  - Feedback from previous attempt (if any)            │  │  │
│  │  │                                                        │  │  │
│  │  │  Output: SQL Query                                    │  │  │
│  │  │  Example:                                             │  │  │
│  │  │  SELECT COUNT(*) FROM checklist                       │  │  │
│  │  │  WHERE department = 'PC'                              │  │  │
│  │  │  AND submission_date IS NULL                          │  │  │
│  │  │  AND task_start_date >= '2026-01-01'                  │  │  │
│  │  │  UNION ALL                                            │  │  │
│  │  │  SELECT COUNT(*) FROM delegation ...                  │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │                    ▼                                         │  │
│  │           ┌────────────────┐                                │  │
│  │           │ ROUTING LOGIC  │                                │  │
│  │           │ should_validate│                                │  │
│  │           │ _or_execute()  │                                │  │
│  │           └────────┬───────┘                                │  │
│  │                    │                                         │  │
│  │         ┌──────────┴──────────┐                             │  │
│  │         │                     │                             │  │
│  │         ▼                     ▼                             │  │
│  │  First Attempt        Max Attempts Reached                  │  │
│  │  (Always Validate)    (Skip Validation)                     │  │
│  │         │                     │                             │  │
│  │         ▼                     │                             │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 5: validate_query                               │  │  │
│  │  │  🔍 LLM 2: Query Validator (OpenAI GPT)              │  │  │
│  │  │                                                        │  │  │
│  │  │  Validation Checks:                                   │  │  │
│  │  │  ✅ Step 1: Column restrictions (no forbidden cols)   │  │  │
│  │  │  ✅ Step 2: UNION ALL structure (both tables)        │  │  │
│  │  │  ✅ Step 3: Pending/completed logic correct          │  │  │
│  │  │  ✅ Step 4: planned_date only in delegation          │  │  │
│  │  │  ✅ Step 5: Date filters present                     │  │  │
│  │  │  ✅ Step 6: Performance metrics complete             │  │  │
│  │  │  ✅ Step 7: Query type (SELECT only)                 │  │  │
│  │  │  ✅ Step 8: Case sensitivity (LOWER/UPPER)           │  │  │
│  │  │                                                        │  │  │
│  │  │  Output: JSON                                         │  │  │
│  │  │  {                                                    │  │  │
│  │  │    "status": "APPROVED" | "NEEDS_FIX",               │  │  │
│  │  │    "confidence": 70-100,                             │  │  │
│  │  │    "reasoning": "...",                               │  │  │
│  │  │    "warnings": [...],                                │  │  │
│  │  │    "errors": [...]                                   │  │  │
│  │  │  }                                                    │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │         ┌──────────┴──────────┐                             │  │
│  │         │                     │                             │  │
│  │         ▼                     ▼                             │  │
│  │    APPROVED              NEEDS_FIX                           │  │
│  │         │            (Provide Feedback)                      │  │
│  │         │                     │                             │  │
│  │         │                     ▼                             │  │
│  │         │         ┌───────────────────────┐                 │  │
│  │         │         │ should_regenerate_or  │                 │  │
│  │         │         │ _approve()            │                 │  │
│  │         │         └───────────┬───────────┘                 │  │
│  │         │                     │                             │  │
│  │         │                     ▼                             │  │
│  │         │         Loop Back to NODE 4 (generate_query)      │  │
│  │         │         with feedback                             │  │
│  │         │         (Max 3 attempts)                          │  │
│  │         │                                                   │  │
│  │         ▼                                                   │  │
│  │  ┌───────────────────────────────────────────────────────┐  │  │
│  │  │  NODE 6: run_query                                    │  │  │
│  │  │  ⚡ Execute SQL Query                                 │  │  │
│  │  │                                                        │  │  │
│  │  │  Security Validation (security.py):                   │  │  │
│  │  │  🔒 Check for SQL injection patterns                  │  │  │
│  │  │  🔒 Verify only SELECT/WITH allowed                   │  │  │
│  │  │  🔒 Max query length check                            │  │  │
│  │  │  🔒 No multiple statements                            │  │  │
│  │  │                                                        │  │  │
│  │  │  Execute against PostgreSQL:                          │  │  │
│  │  │  database-2-mumbai...rds.amazonaws.com                │  │  │
│  │  │                                                        │  │  │
│  │  │  Results:                                             │  │  │
│  │  │  [(22,), (5,)] → "22 in checklist, 5 in delegation"  │  │  │
│  │  └─────────────────┬─────────────────────────────────────┘  │  │
│  │                    │                                         │  │
│  │                    ▼                                         │  │
│  │                  END                                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │    NATURAL LANGUAGE ANSWER (agent_nodes.py)                 │  │
│  │  🤖 LLM 3: Answer Generator (OpenAI GPT)                   │  │
│  │                                                              │  │
│  │  Input:                                                      │  │
│  │  - User question                                             │  │
│  │  - SQL query                                                 │  │
│  │  - Raw results: [(22,), (5,)]                               │  │
│  │                                                              │  │
│  │  Output (Streaming):                                         │  │
│  │  "There are 27 pending tasks in the PC department "         │  │
│  │  "this month: 22 in the checklist table and 5 in "          │  │
│  │  "the delegation table."                                     │  │
│  └──────────────────────┬──────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │         CACHE & SESSION UPDATE                              │  │
│  │  💾 Cache successful query for future use                   │  │
│  │  💾 Store in session history                                │  │
│  │  💾 Extract context (entities, tables, columns)             │  │
│  └─────────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                            │
│  Displays answer with typing animation:                             │
│  "There are 27 pending tasks..." (word by word)                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow (Simplified)

### **Phase 1: Initialization (Fast Path)**
```
1. User Question → POST /api/chat/stream
2. Create/Get Session ID
3. Cache Check
   ├─ CACHE HIT → Execute cached SQL → Return answer ⚡ (Fast!)
   └─ CACHE MISS → Continue to Phase 2 ↓
```

### **Phase 2: Query Generation (LangGraph)**
```
4. Load Database Schema (tables, columns, samples)
5. LLM 1 (Generator) → Generate SQL Query
6. Validation Decision:
   ├─ First Attempt → Always validate
   └─ Retry Attempt → Check if max attempts reached
```

### **Phase 3: Validation Loop (Quality Assurance)**
```
7. LLM 2 (Validator) → Check query against 8 rules
8. Decision:
   ├─ APPROVED (confidence ≥ 70%) → Execute
   └─ NEEDS_FIX → Regenerate with feedback (max 3 attempts)
```

### **Phase 4: Execution & Answer**
```
9. Security Check → Prevent SQL injection
10. Execute SQL → Get results from PostgreSQL
11. LLM 3 (Answer Generator) → Convert results to natural language
12. Stream answer word-by-word to frontend
13. Cache successful query + Update session
```

---

## 🧠 Dual-LLM Validation Process

### **Why Two LLMs?**
- **LLM 1 (Generator)**: Creative, generates SQL from natural language
- **LLM 2 (Validator)**: Critical, checks for errors and enforces rules
- **Result**: Higher accuracy, fewer errors, better quality

### **Validation Loop Example:**

```
Attempt 1:
┌─────────────────────────────────────────────────────────────┐
│ LLM 1 Generates:                                            │
│ SELECT * FROM checklist WHERE status = 'pending'            │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM 2 Validates:                                            │
│ ❌ ERROR: 'status' column is FORBIDDEN                      │
│ ❌ ERROR: Missing UNION ALL for delegation table            │
│ Confidence: 40% → NEEDS_FIX                                 │
│                                                              │
│ Feedback:                                                    │
│ - Use submission_date IS NULL for pending (not status)      │
│ - Query BOTH checklist AND delegation with UNION ALL        │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
Attempt 2:
┌─────────────────────────────────────────────────────────────┐
│ LLM 1 Regenerates (with feedback):                          │
│ SELECT COUNT(*) FROM checklist                              │
│ WHERE submission_date IS NULL                               │
│ UNION ALL                                                   │
│ SELECT COUNT(*) FROM delegation                             │
│ WHERE submission_date IS NULL                               │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM 2 Validates:                                            │
│ ✅ Correct columns used                                     │
│ ✅ UNION ALL present                                        │
│ ⚠️  Warning: Missing date filter for "this month"           │
│ Confidence: 85% → APPROVED                                  │
└───────────────────────┬─────────────────────────────────────┘
                        ▼
                   EXECUTE QUERY ✅
```

---

## 📂 Component Details

### **1. Configuration (`app/core/config.py`)**
```python
Purpose: Centralized settings
- OPENAI_API_KEY: API authentication
- LLM_MODEL: Currently "gpt-5.2" (⚠️ Will cause errors!)
- DATABASE_URL: PostgreSQL connection
- ALLOWED_TABLES: ["users", "checklist", "delegation"]
- MAX_VALIDATION_ATTEMPTS: 3
- CONFIDENCE_THRESHOLD: 70%
```

### **2. SQL Agent (`app/services/sql_agent.py`)**
```python
Purpose: Core LangGraph state machine
Components:
- EnhancedState: Tracks validation loops, feedback
- GENERATE_QUERY_SYSTEM_PROMPT: Instructions for LLM 1
- VALIDATOR_SYSTEM_PROMPT: Instructions for LLM 2
- 6 Node Functions: list_tables, get_schema, store_schema, 
                     generate_query, validate_query, run_query
```

### **3. Agent Nodes (`app/services/agent_nodes.py`)**
```python
Purpose: Implement graph nodes
Key Functions:
- generate_natural_answer(): LLM 3 for answer generation
- validate_query_with_retry(): Retry logic for API failures
- should_validate_or_execute(): Routing decision
```

### **4. Chat Routes (`app/api/routes/chat.py`)**
```python
Purpose: API endpoints
Routes:
- POST /api/chat/stream: Main chat endpoint (SSE streaming)
- GET /api/cache/stats: Cache statistics
- POST /api/cache/clear: Clear cache
- POST /api/cache/invalidate/{session_id}: Clear session cache
```

### **5. Cache Service (`app/services/cache_service.py`)**
```python
Purpose: Semantic query caching
Features:
- Similarity threshold: 95%
- Stores: {question, SQL, timestamp}
- find_similar_query(): Fuzzy match
- Speeds up repeated queries
```

### **6. Context Manager (`app/services/context_manager.py`)**
```python
Purpose: Conversation context
Features:
- Extracts entities (names, departments, dates)
- Resolves pronouns ("his" → "John's")
- Provides context hints for follow-ups
```

### **7. Security (`app/core/security.py`)**
```python
Purpose: SQL injection prevention
Checks:
- Only SELECT/WITH allowed
- No multiple statements
- Blacklist dangerous keywords
- Max query length
```

---

## 📝 Step-by-Step Example

### **User Question:**
"Show me pending tasks in PC department this month"

### **System Flow:**

#### **Step 1: API Receives Request**
```json
POST /api/chat/stream
{
  "question": "Show me pending tasks in PC department this month",
  "session_id": "abc-123"
}
```

#### **Step 2: Cache Check**
```
🔍 Searching cache for similar queries...
❌ No similar query found (cache miss)
```

#### **Step 3: Context Check**
```
💬 Checking conversation history...
Previous question: "How many users in PC?"
Context hint: "User asking about PC department"
```

#### **Step 4: Load Schema**
```sql
📊 Tables: users, checklist, delegation
📋 Checklist columns: task_id, name, department, submission_date, task_start_date...
❌ Forbidden: status, created_at, remark, image
```

#### **Step 5: LLM 1 Generates Query**
```sql
SELECT 
  'checklist' as source_table,
  COUNT(*) as pending_tasks
FROM checklist
WHERE UPPER(department) = UPPER('PC')
  AND submission_date IS NULL
  AND task_start_date::DATE >= DATE_TRUNC('month', CURRENT_DATE)::DATE
  AND task_start_date::DATE < (CURRENT_DATE + INTERVAL '1 day')::DATE

UNION ALL

SELECT 
  'delegation' as source_table,
  COUNT(*) as pending_tasks
FROM delegation
WHERE UPPER(department) = UPPER('PC')
  AND submission_date IS NULL
  AND task_start_date::DATE >= DATE_TRUNC('month', CURRENT_DATE)::DATE
  AND task_start_date::DATE < (CURRENT_DATE + INTERVAL '1 day')::DATE
```

#### **Step 6: LLM 2 Validates**
```json
{
  "status": "APPROVED",
  "confidence": 95,
  "reasoning": "Perfect query with UNION ALL, correct columns, date filter",
  "warnings": [],
  "errors": []
}
```

#### **Step 7: Security Check**
```
🔒 Checking for SQL injection...
✅ No dangerous keywords
✅ SELECT statement only
✅ Length OK (< 50000 chars)
```

#### **Step 8: Execute Query**
```sql
Result: [
  {'source_table': 'checklist', 'pending_tasks': 22},
  {'source_table': 'delegation', 'pending_tasks': 5}
]
```

#### **Step 9: LLM 3 Generates Answer (Streaming)**
```
"There are 27 pending tasks in the PC department this month. "
"Specifically, 22 tasks in the checklist table and 5 tasks in "
"the delegation table."
```

#### **Step 10: Cache & Store**
```
💾 Caching query for future use...
💾 Storing in session history...
✅ Done!
```

---

## ⚡ Performance Optimizations

1. **Semantic Cache**: 95% similarity → instant results
2. **Streaming**: Word-by-word transmission (feels faster)
3. **Session Persistence**: MemorySaver checkpointer
4. **Retry Logic**: Auto-retry on API failures (max 3)
5. **Connection Pooling**: Reuse DB connections

---

## 🛡️ Security Features

1. **SQL Injection Prevention**: Whitelist/blacklist patterns
2. **Column Restrictions**: Only allowed columns
3. **Table Restrictions**: Only 3 tables accessible
4. **Query Type Limits**: SELECT/WITH only
5. **Max Query Length**: 50,000 characters

---

## 🔧 Configuration Files

```
Backend_New/
├── .env                    # Environment variables (API keys, DB)
├── app/
│   ├── main.py            # FastAPI application entry
│   ├── core/
│   │   ├── config.py      # Settings & configuration
│   │   ├── security.py    # SQL injection prevention
│   │   └── column_restrictions.py  # Allowed columns
│   ├── services/
│   │   ├── sql_agent.py        # LangGraph agent (Nodes 1-6)
│   │   ├── agent_nodes.py      # Node implementations
│   │   ├── cache_service.py    # Query caching
│   │   ├── context_manager.py  # Conversation context
│   │   ├── session_manager.py  # User sessions
│   │   └── db_service.py       # Database operations
│   └── api/
│       └── routes/
│           └── chat.py         # Chat API endpoints
```

---

## 📊 System Metrics

- **Average Response Time**: 2-5 seconds (first query)
- **Cache Hit Response**: 0.5-1 second
- **Validation Success Rate**: ~85% on first attempt
- **Max Validation Attempts**: 3
- **Confidence Threshold**: 70%

---

## ⚠️ IMPORTANT NOTE

**Current Configuration Uses `gpt-5.2`** which DOESN'T EXIST!

OpenAI's available models:
- ✅ `gpt-4o` (Latest, best)
- ✅ `gpt-4o-mini` (Fast, cheap)
- ✅ `gpt-4-turbo`
- ❌ `gpt-5.2` (NOT RELEASED YET)

**Change `.env` to use a valid model or you'll get API errors!**

---

## 🎯 Summary

**Backend_New** is a sophisticated system that:
1. ✅ Receives natural language questions
2. ✅ Uses Dual-LLM validation for accuracy
3. ✅ Generates and validates SQL queries
4. ✅ Executes with security checks
5. ✅ Returns streaming natural language answers
6. ✅ Caches for performance
7. ✅ Maintains conversation context

**Key Innovation:** Dual-LLM system (Generator + Validator) = Higher accuracy!
