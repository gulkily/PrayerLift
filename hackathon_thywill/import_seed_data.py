#!/usr/bin/env python3
"""
Import seed data from ThyWill archive into PrayerLift database
"""

import sqlite3
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

# Database path
DATABASE_PATH = "database.db"

def parse_prayer_file(file_path):
    """Parse a prayer file and extract structured data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.strip().split('\n')
    
    # Parse header line: "Prayer <id> by <author>"
    header_match = re.match(r'Prayer (\w+) by (.+)', lines[0])
    if not header_match:
        return None
    
    prayer_id = header_match.group(1)
    author = header_match.group(2)
    
    # Parse submitted line: "Submitted Month DD YYYY at HH:MM"
    submitted_match = re.match(r'Submitted (.+ \d{4} at \d{2}:\d{2})', lines[1])
    if not submitted_match:
        return None
    
    timestamp_str = submitted_match.group(1)
    # Convert to datetime
    created_at = datetime.strptime(timestamp_str, '%B %d %Y at %H:%M').isoformat()
    
    # Find the original prayer text (line 3 until "Generated Prayer:")
    prayer_text = ""
    generated_prayer = ""
    activity = []
    
    i = 3
    # Get original prayer text
    while i < len(lines) and not lines[i].startswith('Generated Prayer:'):
        if lines[i].strip():
            prayer_text += lines[i].strip() + " "
        i += 1
    
    prayer_text = prayer_text.strip()
    
    # Skip "Generated Prayer:" line
    if i < len(lines) and lines[i].startswith('Generated Prayer:'):
        i += 1
        # Get generated prayer text until "Activity:" line
        while i < len(lines) and not lines[i].startswith('Activity:'):
            if lines[i].strip():
                generated_prayer += lines[i].strip() + " "
            i += 1
    
    generated_prayer = generated_prayer.strip()
    
    # Parse activity
    if i < len(lines) and lines[i].startswith('Activity:'):
        i += 1
        while i < len(lines):
            if lines[i].strip():
                activity.append(lines[i].strip())
            i += 1
    
    return {
        'id': prayer_id,
        'author': author,
        'text': prayer_text,
        'generated_prayer': generated_prayer,
        'created_at': created_at,
        'activity': activity
    }

def create_or_get_user(cursor, display_name):
    """Create user if doesn't exist, return user ID"""
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE display_name = ?", (display_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new user
    user_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO users (id, display_name, created_at)
        VALUES (?, ?, ?)
    """, (user_id, display_name, datetime.now().isoformat()))
    
    return user_id

def parse_activity_for_marks(activity, prayer_id, cursor):
    """Parse activity lines to create prayer marks"""
    marks = []
    
    for line in activity:
        # Parse: "Month DD YYYY at HH:MM - username prayed this prayer"
        match = re.match(r'(.+ \d{4} at \d{2}:\d{2}) - (.+) prayed this prayer', line)
        if match:
            timestamp_str = match.group(1)
            username = match.group(2)
            
            # Convert timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, '%B %d %Y at %H:%M').isoformat()
                user_id = create_or_get_user(cursor, username)
                marks.append((user_id, prayer_id, timestamp))
            except ValueError:
                # Skip invalid timestamps
                continue
    
    return marks

def import_prayers_from_directory(prayers_dir, cursor):
    """Import all prayers from the prayers directory"""
    prayers_path = Path(prayers_dir)
    prayer_files = list(prayers_path.rglob("*.txt"))
    
    imported_count = 0
    
    for file_path in prayer_files:
        print(f"Processing: {file_path.name}")
        
        prayer_data = parse_prayer_file(file_path)
        if not prayer_data:
            print(f"  Skipped: Could not parse {file_path.name}")
            continue
        
        # Create or get author user
        author_id = create_or_get_user(cursor, prayer_data['author'])
        
        # Insert prayer
        cursor.execute("""
            INSERT OR REPLACE INTO prayers (id, text, author_id, created_at, generated_prayer)
            VALUES (?, ?, ?, ?, ?)
        """, (
            prayer_data['id'],
            prayer_data['text'],
            author_id,
            prayer_data['created_at'],
            prayer_data['generated_prayer'] if prayer_data['generated_prayer'] else None
        ))
        
        # Parse and insert prayer marks
        marks = parse_activity_for_marks(prayer_data['activity'], prayer_data['id'], cursor)
        
        for user_id, prayer_id, created_at in marks:
            cursor.execute("""
                INSERT OR REPLACE INTO prayer_marks (user_id, prayer_id, created_at)
                VALUES (?, ?, ?)
            """, (user_id, prayer_id, created_at))
        
        imported_count += 1
        
        if imported_count % 10 == 0:
            print(f"  Imported {imported_count} prayers so far...")
    
    return imported_count

def main():
    """Main import function"""
    archive_path = "../complete_site_archive"
    prayers_dir = os.path.join(archive_path, "prayers")
    
    if not os.path.exists(prayers_dir):
        print(f"Error: Prayers directory not found at {prayers_dir}")
        print("Make sure the archive is extracted in the parent directory")
        return
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        print("Starting import of seed data...")
        print(f"Archive path: {archive_path}")
        
        # Import prayers
        imported_count = import_prayers_from_directory(prayers_dir, cursor)
        
        # Commit all changes
        conn.commit()
        
        print(f"\n✅ Import completed!")
        print(f"   Imported {imported_count} prayers")
        
        # Show some stats
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prayers")
        prayer_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM prayer_marks")
        mark_count = cursor.fetchone()[0]
        
        print(f"   Total users: {user_count}")
        print(f"   Total prayers: {prayer_count}")
        print(f"   Total prayer marks: {mark_count}")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        conn.rollback()
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()