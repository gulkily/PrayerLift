from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import uuid
from datetime import datetime
import os
from ai_service import ai_service
from tts_service import tts_service
from auth import get_current_user_optional, get_or_create_session_user, require_auth, create_session, hash_password, verify_password

app = FastAPI(title="PrayerLift")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_PATH = "database.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            display_name TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create prayers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prayers (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            author_id TEXT REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generated_prayer TEXT
        )
    """)
    
    # Create prayer_marks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prayer_marks (
            user_id TEXT REFERENCES users(id),
            prayer_id TEXT REFERENCES prayers(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, prayer_id)
        )
    """)
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT REFERENCES users(id),
            expires_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_db():
    """Get database connection with thread-safe settings"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get("/", response_class=HTMLResponse)
async def prayer_feed(request: Request, session_id: str = Cookie(None), db = Depends(get_db)):
    """Display the main prayer feed with auto-session creation"""
    from fastapi import Response
    
    # Get or create user session
    current_user, session_id = get_or_create_session_user(session_id, db)
    
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.*, u.display_name, 
               COUNT(pm.prayer_id) as prayer_count,
               CASE WHEN upm.prayer_id IS NOT NULL THEN 1 ELSE 0 END as user_marked
        FROM prayers p 
        LEFT JOIN users u ON p.author_id = u.id
        LEFT JOIN prayer_marks pm ON p.id = pm.prayer_id
        LEFT JOIN prayer_marks upm ON p.id = upm.prayer_id AND upm.user_id = ?
        GROUP BY p.id
        ORDER BY p.created_at DESC
    """, (current_user["id"],))
    
    prayers = cursor.fetchall()
    
    response = templates.TemplateResponse("index.html", {
        "request": request, 
        "prayers": prayers,
        "current_user": current_user
    })
    
    # Set session cookie if new session was created
    if not request.cookies.get("session_id"):
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=30*24*60*60)
    
    return response

@app.post("/prayers")
async def submit_prayer(
    request: Request,
    prayer_text: str = Form(...),
    author_name: str = Form(...),
    session_id: str = Cookie(None),
    db = Depends(get_db)
):
    """Submit a new prayer request"""
    # Get or create user session
    current_user, _ = get_or_create_session_user(session_id, db)
    
    cursor = db.cursor()
    
    # Update user's name if it changed
    if author_name.strip() != current_user["display_name"]:
        try:
            cursor.execute(
                "UPDATE users SET display_name = ? WHERE id = ?",
                (author_name.strip(), current_user["id"])
            )
        except sqlite3.IntegrityError:
            # Name already taken, keep the old name
            author_name = current_user["display_name"]
    
    user_id = current_user["id"]
    
    # Create prayer
    prayer_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO prayers (id, text, author_id) VALUES (?, ?, ?)",
        (prayer_id, prayer_text, user_id)
    )
    
    db.commit()
    
    # Generate AI prayer response
    try:
        generated_prayer = ai_service.generate_prayer_response(prayer_text, author_name)
        if generated_prayer:
            cursor.execute(
                "UPDATE prayers SET generated_prayer = ? WHERE id = ?",
                (generated_prayer, prayer_id)
            )
            db.commit()
    except Exception as e:
        print(f"Failed to generate AI prayer: {e}")
    
    return RedirectResponse(url="/", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db)
):
    """Handle login"""
    cursor = db.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE display_name = ?", (username,))
    user = cursor.fetchone()
    
    if user and verify_password(password, user[1]):
        session_id = create_session(user[0], db)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=30*24*60*60)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": {"url": "/login"}, 
            "error": "Invalid username or password"
        })

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Display registration page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db = Depends(get_db)
):
    """Handle registration"""
    cursor = db.cursor()
    
    try:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        cursor.execute(
            "INSERT INTO users (id, display_name, password_hash) VALUES (?, ?, ?)",
            (user_id, username, password_hash)
        )
        db.commit()
        
        session_id = create_session(user_id, db)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=30*24*60*60)
        return response
        
    except sqlite3.IntegrityError:
        return templates.TemplateResponse("register.html", {
            "request": {"url": "/register"}, 
            "error": "Username already exists"
        })

@app.post("/logout")
async def logout(response: Response):
    """Handle logout"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("session_id")
    return response

@app.post("/mark/{prayer_id}")
async def mark_prayer(
    prayer_id: str,
    session_id: str = Cookie(None),
    db = Depends(get_db)
):
    """Mark that user has prayed for this prayer"""
    # Get or create user session  
    current_user, _ = get_or_create_session_user(session_id, db)
    
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO prayer_marks (user_id, prayer_id) VALUES (?, ?)",
            (current_user["id"], prayer_id)
        )
        db.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/mark/{prayer_id}")
async def unmark_prayer(
    prayer_id: str,
    session_id: str = Cookie(None),
    db = Depends(get_db)
):
    """Remove prayer mark"""
    # Get or create user session
    current_user, _ = get_or_create_session_user(session_id, db)
    
    cursor = db.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM prayer_marks WHERE user_id = ? AND prayer_id = ?",
            (current_user["id"], prayer_id)
        )
        db.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{prayer_id}")
async def get_prayer_audio(prayer_id: str, audio_type: str = "original", db = Depends(get_db)):
    """Generate and return audio for a prayer (original or generated)"""
    cursor = db.cursor()
    cursor.execute("SELECT text, generated_prayer FROM prayers WHERE id = ?", (prayer_id,))
    prayer = cursor.fetchone()
    
    if not prayer:
        raise HTTPException(status_code=404, detail="Prayer not found")
    
    # Choose text based on audio_type
    if audio_type == "generated" and prayer[1]:
        text = prayer[1]
    else:
        text = prayer[0]
    
    # Generate audio
    audio_base64 = tts_service.generate_audio_base64(text)
    
    if not audio_base64:
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    
    return {"audio": audio_base64, "type": "audio/mpeg"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)