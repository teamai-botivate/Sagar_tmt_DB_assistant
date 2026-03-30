"""
Central Router (Domain Router)
==============================
Routes user queries to the correct DOMAIN agent.

ARCHITECTURE: Single Database, Multiple Domains
================================================
All domains connect to the SAME PostgreSQL database.
The router determines WHICH DOMAIN should handle the query
based on semantic analysis of tables/columns.

Domains:
- hr_operations (checklist): employees, tasks, leaves, visitors, etc.
- sales_crm (lead_to_order): leads, quotations, sales pipeline
- maintenance (sagar_db): machine repairs, maintenance tasks
"""

from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from app.core.config import settings

# Import the workflow apps from the domain modules
from app.domains.hr_operations.workflow import workflow_app as checklist_app

# ============================================================================
# ROUTER LOGIC (AI-POWERED DOMAIN ROUTING)
# ============================================================================

from langchain_core.messages import SystemMessage, HumanMessage

# Initialize lightweight router LLM (cheap & fast model preferred)
router_llm = ChatOpenAI(
    model="gpt-4o-mini",  # Use fast model for routing
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY
)

# Import Metadata & Schema for Dynamic Discovery (from domain configs)
from app.domains.hr_operations.config import ROUTER_METADATA as HR_META, SEMANTIC_SCHEMA as HR_SCHEMA
from app.domains.sales_crm.config import ROUTER_METADATA as SALES_META, DB_SCHEMA as SALES_SCHEMA
from app.domains.maintenance.config import ROUTER_METADATA as MAINTENANCE_META, DB_SCHEMA as MAINTENANCE_SCHEMA

# Registry of Available Domains
# Structure: (Metadata Dict, Schema String)
# NOTE: All domains connect to the SAME database - routing is for TABLE isolation
REGISTERED_DOMAINS = [
    (HR_META, HR_SCHEMA),
    (SALES_META, SALES_SCHEMA),
    (MAINTENANCE_META, MAINTENANCE_SCHEMA)
]

# Legacy alias for backward compatibility
REGISTERED_DATABASES = REGISTERED_DOMAINS

def _build_router_prompt() -> str:
    """
    Dynamically constructs the router system prompt based on registered domains.
    Enforces Deep Semantic Analysis using actual DB Schemas.
    """
    domain_descriptions = ""
    for i, (meta, schema) in enumerate(REGISTERED_DOMAINS, 1):
        # Truncate schema slightly if it's too huge
        safe_schema = schema[:1500] + "..." if len(schema) > 1500 else schema
        
        domain_descriptions += f"""
{i}. DOMAIN: '{meta["name"]}'
   DESCRIPTION: {meta["description"]}
   ALLOWED TABLES/SCHEMA:
   {safe_schema}
   ------------------------------------------------
"""

    return f"""
You are the **Intelligent Domain Router**. Your goal is to route the User's Query to the correct DOMAIN by analyzing the match between the query and the DOMAIN SCHEMA.

NOTE: All domains are in the SAME database. Your job is to pick which DOMAIN (set of tables) handles this query.

### AVAILABLE DOMAINS (With Schema Context)
{domain_descriptions}

### ROUTING LOGIC (Deep Schema Analysis)
1. **Analyze:** Look at the user's terms (e.g. "leads", "machine", "task_id", "employee", "leave").
2. **Scan Schemas:** Check which DOMAIN actually contains tables/columns matching those terms.
   - User asks for "converted leads"? -> Sales CRM domain (lead_to_order)
   - User asks for "machine repairs"? -> Maintenance domain (sagar_db)
   - User asks for "pending tasks"? -> HR Operations domain (checklist)
   - User asks for "leave requests"? -> HR Operations domain (checklist)
3. **Detect Ambiguity (CRITICAL):**
   - If a term (like "status" or "tasks") appears conceptually in MULTIPLE domains, you **MUST** return AMBIGUOUS.
   - **Construct the Clarification Question based on the specific tables/concepts you found.**
     - BAD: "Did you mean X or Y?"
     - GOOD: "Did you mean **Employee Task Status** (from HR domain) or **Machine Repair Status** (from Maintenance domain)?"

### OUTPUT FORMAT (JSON ONLY)
Return a valid JSON object.
{{
  "database": "Target Domain Name (checklist/lead_to_order/sagar_db)" OR "AMBIGUOUS",
  "reason": "Explain which table/column matched the user's intent.",
  "clarification_question": "If AMBIGUOUS, ask a specific question comparing the domains."
}}
"""

def determine_database(query: str) -> tuple[str, str, str]:
    """
    Analyzes the user query using LLM to determine target DOMAIN.
    Returns: (domain_name, reasoning, clarification_question)
    
    NOTE: Named 'determine_database' for backward compatibility,
    but actually determines the DOMAIN (set of tables) to use.
    """
    try:
        # Generate prompt dynamically
        system_prompt = _build_router_prompt()
        
        response = router_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ])
        
        content = response.content.strip()
        
        # Clean markdown if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        import json
        data = json.loads(content)
        
        domain_name = data.get("database", "AMBIGUOUS").lower()
        reason = data.get("reason", "No reason provided.")
        clarification_question = data.get("clarification_question", "Could you please clarify which domain you mean?")
        
        # Check against registered domain names
        for meta, schema in REGISTERED_DOMAINS:
            if meta["name"] in domain_name:
                return meta["name"], reason, ""
            
        return "AMBIGUOUS", reason, clarification_question
        
    except Exception as e:
        print(f"[ROUTER ERROR] Failed to route query: {e}")
        return "checklist", "Router encountered an error, defaulting to HR Operations domain.", ""

def get_agent_for_database(db_name: str = "checklist"):
    """
    Factory function to return the correct compiled LangGraph agent for a domain.
    
    NOTE: Named for backward compatibility. All agents connect to SAME database,
    but each only queries its ALLOWED_TABLES.
    """
    if db_name == "lead_to_order":
        from app.domains.sales_crm.workflow import lead_to_order_app
        return lead_to_order_app
        
    if db_name == "sagar_db":
        from app.domains.maintenance.workflow import sagar_app
        return sagar_app
        
    # Default: HR Operations domain
    return checklist_app

# ============================================================================
# HELPER FOR STREAMING RESPONSES
# ============================================================================

# ============================================================================
# HELPER FOR STREAMING RESPONSES (GENERIC)
# ============================================================================

# Initialize a dedicated LLM to avoid import loops
answer_llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    temperature=0,
    openai_api_key=settings.OPENAI_API_KEY
)

def create_answer_generator(system_prompt: str):
    """
    Creates a generic async generator function for answer synthesis.
    Now accepts (query, sql_result, sql_query) to match legacy signature.
    """
    async def answer_gen(query: str, sql_result: str, sql_query: str):
        # ----------------------------------------------------
        # 1. MAIN ANSWER STREAM (The "What")
        # ----------------------------------------------------
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {query}\n\nSQL Query: {sql_query}\n\nSQL Result: {sql_result}")
        ]
        
        try:
            async for chunk in answer_llm.astream(messages):
                yield chunk.content
        except Exception as e:
            yield f"Error generating answer: {e}"

        # ----------------------------------------------------
        # 2. TECHNICAL NOTE (The "How")
        # ----------------------------------------------------
        # We append this at the end, just like the original system.
        note_prompt = f"""You are a SQL Expert. Explain the logic of the following SQL query in a single natural language note.

SQL Query: 
{sql_query}

INSTRUCTIONS:
- Output a single parenthetical note.
- Format: `(Note: ...)`
- Explain which tables were queried.
- **CRITICAL:** Explicitly name the columns used.
- Example: "(Note: To find this, I queried the `enquiry_to_order` table, filtered `timestamp` for last month...)"

Generate ONLY the note:"""

        try:
            yield "\n\n" # Spacing
            technical_note_msg = await answer_llm.ainvoke([HumanMessage(content=note_prompt)])
            yield technical_note_msg.content
        except Exception as e:
            print(f"[NOTE GEN ERROR] {e}")


    return answer_gen

def get_answer_generator(db_name: str = "checklist"):
    """
    Returns the specific answer generator function for the DB.
    Each DB might have different formatting styles.
    """
    if db_name == "lead_to_order":
        from app.domains.sales_crm.prompts import ANSWER_SYNTHESIS_SYSTEM_PROMPT
        return create_answer_generator(ANSWER_SYNTHESIS_SYSTEM_PROMPT)
    
    if db_name == "sagar_db":
        from app.domains.maintenance.prompts import ANSWER_SYNTHESIS_SYSTEM_PROMPT
        return create_answer_generator(ANSWER_SYNTHESIS_SYSTEM_PROMPT)
    
    # Default Checklist
    from app.domains.hr_operations.prompts import ANSWER_SYNTHESIS_SYSTEM_PROMPT
    return create_answer_generator(ANSWER_SYNTHESIS_SYSTEM_PROMPT)
