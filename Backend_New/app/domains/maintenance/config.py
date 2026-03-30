"""
Maintenance Domain - Configuration
===================================
Domain: sagar_db (Maintenance Operations)
Tables: 1 (maintenance_task_assign)

Part of Single Database, Multi-Domain Architecture (v2.2)
All domains share DATABASE_URL with isolation via ALLOWED_TABLES.

Note: Column names are lowercase in PostgreSQL.
"""

# 1. Table & Column Restrictions
ALLOWED_TABLES = ["maintenance_task_assign"]

# Router Metadata (Used for Auto-Discovery)
ROUTER_METADATA = {
    "name": "sagar_db",
    "description": "A specialized Maintenance & Facility Management System designed to track machine repairs and operational tasks. It records 'who' (doer_name) performed maintenance on 'what' (machine_name), 'when' it was scheduled (task_start_date), and 'when' it was actually completed (actual_date). Supports filtering by division (SMS, PIPE MILL, STRIP MILL), department (doer_department, machine_department), machine_area, and given_by (task assigner). Use this domain for questions regarding machine uptime, pending repairs, technician performance, maintenance schedules, and division-wise/department-wise analytics.",
    "keywords": [
        "maintenance", "machine", "repair", "task", "assign", "doer", 
        "start date", "actual date", "completion", "pending", "status", "sagar",
        "technician", "breakdown", "schedule", "facility", "division",
        "department", "given_by", "area", "part", "sms", "pipe mill", "strip mill"
    ]
}

COLUMNS_RESTRICTION = {
    "maintenance_task_assign": [
        "machine_name", 
        "doer_name", 
        "task_start_date", 
        "actual_date",
        "given_by",
        "doer_department",
        "machine_area",
        "machine_department",
        "division",
        "description",
        "part_name"
    ]
}

# 2. Schema Definition for LLM Context
DB_SCHEMA = """
Table: maintenance_task_assign
Columns:
- machine_name (VARCHAR): Name/Identifier of the machine being maintained.
- doer_name (VARCHAR): Person responsible for performing the task.
- task_start_date (DATE): Scheduled start date for the maintenance.
- actual_date (DATE): Actual date when the task was completed.
  (NOTE: If actual_date IS NULL, the task is PENDING. If NOT NULL, task is COMPLETED).
- given_by (VARCHAR): Person who assigned/created the task.
- doer_department (VARCHAR): Department of the doer. Values: CCM, SMS ELECTRICAL, SMS MAINTENANCE, PIPE MILL ELECTRICAL, PIPE MILL MAINTENANCE, PIPE MILL PRODUCTION, STRIP MILL ELECTRICAL, STRIP MILL MAINTENANCE, STRIP MILL PRODUCTION, WORKSHOP.
- machine_area (VARCHAR): Physical area/unit where machine is located. Values: Unit-1, Unit-2, PIPE MILL, Strip Mill, Workshop, etc.
- machine_department (VARCHAR): Department of the machine. Values: CCM, SMS ELECTRICAL, SMS MAINTENANCE, PIPE MILL ELECTRICAL, PIPE MILL MAINTENANCE, STRIP MILL ELECTRICAL, STRIP MILL PRODUCTION, WORKSHOP.
- division (VARCHAR): Division/Plant. Values: SMS, PIPE MILL, STRIP MILL.
- description (TEXT): Detailed description of the maintenance task.
- part_name (VARCHAR): Name of the part being maintained (e.g., Carbon brush, Motor, Lub oil).

BUSINESS RULES:
- Pending Tasks: actual_date IS NULL
- Completed Tasks: actual_date IS NOT NULL
- Division-wise analysis: GROUP BY division
- Department-wise analysis: GROUP BY doer_department or machine_department
"""
