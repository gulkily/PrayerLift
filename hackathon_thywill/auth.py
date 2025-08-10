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

def create_anonymous_user(db) -> str:
    """Create anonymous user for session tracking"""
    user_id = str(uuid.uuid4())
    anonymous_name = f"Anonymous_{user_id[:8]}"
    
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (id, display_name) VALUES (?, ?)",
        (user_id, anonymous_name)
    )
    db.commit()
    return user_id

def get_or_create_session_user(session_id: Optional[str] = Cookie(None), db = Depends(get_db)) -> tuple[Optional[dict], str]:
    """Get current user or create anonymous session, returning (user, session_id)"""
    current_user = get_current_user(session_id, db) if session_id else None
    
    if current_user:
        return current_user, session_id
    
    # Create anonymous user and session
    user_id = create_anonymous_user(db)
    new_session_id = create_session(user_id, db)
    
    # Get the newly created user
    cursor = db.cursor()
    cursor.execute("SELECT id, display_name FROM users WHERE id = ?", (user_id,))
    user_data = cursor.fetchone()
    
    anonymous_user = {
        "id": user_data[0],
        "display_name": user_data[1],
        "is_anonymous": True
    }
    
    return anonymous_user, new_session_id

def require_auth(user = Depends(get_current_user)) -> dict:
    """Require user to be authenticated"""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user