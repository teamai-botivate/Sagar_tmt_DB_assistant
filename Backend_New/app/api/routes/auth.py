"""
Authentication Routes
=====================
Login endpoint for admin authentication.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.auth import authenticate_admin, create_jwt_token, verify_jwt_token

router = APIRouter()


class LoginRequest(BaseModel):
    login: str  # email or username
    password: str


class TokenVerifyRequest(BaseModel):
    token: str


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate admin user and return JWT token."""
    user = authenticate_admin(request.login, request.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Access denied. Only authorized admin can access this system."
        )
    
    token = create_jwt_token(user)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "name": user["user_name"],
            "email": user["email_id"],
            "department": user["department"],
            "role": user["role"]
        },
        "expires_in_days": 30
    }


@router.post("/verify-token")
async def verify_token(request: TokenVerifyRequest):
    """Verify if a stored token is still valid."""
    payload = verify_jwt_token(request.token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Token expired or invalid. Please login again.")
    
    return {
        "valid": True,
        "user": {
            "name": payload.get("user_name"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    }
