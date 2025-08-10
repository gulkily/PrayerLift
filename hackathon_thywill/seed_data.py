import sqlite3
import uuid
from datetime import datetime

def seed_database():
    """Add sample prayer data for testing"""
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Sample users
    users = [
        {"id": str(uuid.uuid4()), "name": "Sarah M."},
        {"id": str(uuid.uuid4()), "name": "Michael K."},
        {"id": str(uuid.uuid4()), "name": "Jennifer L."},
    ]
    
    for user in users:
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, display_name) VALUES (?, ?)",
            (user["id"], user["name"])
        )
    
    # Sample prayers
    prayers = [
        {
            "id": str(uuid.uuid4()),
            "text": "Please pray for my grandmother who is in the hospital. She's been struggling with her health and the family could really use your support during this difficult time.",
            "author_id": users[0]["id"],
            "generated": "Heavenly Father, we lift up Sarah's grandmother to You in prayer. We ask for Your healing touch upon her body and Your peace to surround the entire family during this challenging time. Grant the medical team wisdom and skill, and let Your love be felt in that hospital room. Amen."
        },
        {
            "id": str(uuid.uuid4()),
            "text": "I'm starting a new job next week and feeling really anxious. Pray for confidence and wisdom as I begin this new chapter.",
            "author_id": users[1]["id"],
            "generated": "Lord, we pray for Michael as he steps into this new opportunity. Calm his anxious heart and fill him with confidence in Your plan for his life. Grant him wisdom in his decisions, favor with his colleagues, and peace that surpasses understanding. Guide his steps and let Your light shine through him. Amen."
        },
        {
            "id": str(uuid.uuid4()),
            "text": "Our community was hit by a severe storm last night. Many families lost their homes. Please pray for strength, comfort, and provision for all those affected.",
            "author_id": users[2]["id"],
            "generated": "Compassionate God, our hearts go out to this community in their time of need. Comfort those who have lost their homes and possessions. Provide shelter, safety, and hope in the midst of this devastation. Raise up helpers and resources, and bind this community together with love and support. Bring restoration and renewal in Your perfect timing. Amen."
        }
    ]
    
    for prayer in prayers:
        cursor.execute(
            "INSERT OR IGNORE INTO prayers (id, text, author_id, generated_prayer) VALUES (?, ?, ?, ?)",
            (prayer["id"], prayer["text"], prayer["author_id"], prayer["generated"])
        )
        
        # Add some prayer marks
        import random
        for user in users[:random.randint(1, 3)]:
            cursor.execute(
                "INSERT OR IGNORE INTO prayer_marks (user_id, prayer_id) VALUES (?, ?)",
                (user["id"], prayer["id"])
            )
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == "__main__":
    seed_database()