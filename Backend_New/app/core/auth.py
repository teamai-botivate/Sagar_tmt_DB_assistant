"""
Authentication Module
=====================
JWT-based authentication for admin-only access.
Only AAKASH AGRAWAL (user_id=835) can access the system.
"""

import jwt
import datetime
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from app.core.config import settings

# JWT Configuration
JWT_SECRET = "sagar-tmt-db-assistant-secret-key-2026"
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_DAYS = 30  # Token expires after 30 days

security_scheme = HTTPBearer()


def authenticate_admin(email_or_username: str, password: str) -> dict:
    """
    Authenticate against the users table in checklist DB.
    Only allows admin role AND specifically AAKASH AGRAWAL (id=835).
    """
    engine = create_engine(settings.DB_CHECKLIST_URL)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, user_name, email_id, department, role
                    FROM users
                    WHERE (email_id = :login OR user_name = :login)
                      AND password = :password
                      AND role = 'admin'
                """),
                {"login": email_or_username, "password": password}
            )
            user = result.fetchone()
            
            if not user:
                return None
            
            # STRICT CHECK: Only AAKASH AGRAWAL is allowed
            if user[1].strip().upper() != "AAKASH AGRAWAL":
                return None
            
            return {
                "id": user[0],
                "user_name": user[1],
                "email_id": user[2],
                "department": user[3],
                "role": user[4]
            }
    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        return None
    finally:
        engine.dispose()


def create_jwt_token(user_data: dict) -> str:
    """Create a JWT token with 30-day expiry."""
    payload = {
        "user_id": user_data["id"],
        "user_name": user_data["user_name"],
        "email": user_data["email_id"],
        "role": user_data["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRY_DAYS),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Extra safety: only allow AAKASH AGRAWAL
        if payload.get("user_name", "").strip().upper() != "AAKASH AGRAWAL":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """FastAPI dependency to enforce admin authentication on routes."""
    token = credentials.credentials
    payload = verify_jwt_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please login again.")
    return payload
