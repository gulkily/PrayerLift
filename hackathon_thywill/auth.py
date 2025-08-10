from fastapi import Request, HTTPException, status, Depends, Cookie
from typing import Optional
import sqlite3
import uuid
from datetime import datetime, timedelta
import hashlib

DATABASE_PATH = "database.db"

def get_db():
    """Get database connection with thread-safe settings"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_session(user_id: str, db) -> str:
    """Create a new session for user"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=30)
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at)
    )
    db.commit()
    return session_id

def get_current_user(session_id: Optional[str] = Cookie(None), db = Depends(get_db)) -> Optional[dict]:
    """Get current user from session"""
    if not session_id:
        return None
        
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.id, u.display_name, s.expires_at 
        FROM sessions s 
        JOIN users u ON s.user_id = u.id 
        WHERE s.id = ? AND s.expires_at > datetime('now')
    """, (session_id,))
    
    result = cursor.fetchone()
    if result:
        return {
            "id": result[0],
            "display_name": result[1],
            "expires_at": result[2]
        }
    return None

def get_current_user_optional(session_id: Optional[str] = Cookie(None), db = Depends(get_db)) -> Optional[dict]:
    """Get current user but don't require authentication"""
    return get_current_user(session_id, db)

def require_auth(user = Depends(get_current_user)) -> dict:
    """Require user to be authenticated"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user