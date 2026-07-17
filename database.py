import os
import sqlite3
import json
from datetime import datetime

# Resolve DB path relative to this script's directory
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "meetings.db")

def get_connection():
    """Establish a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables access by column name
    return conn

def init_db():
    """Create the meetings table if it does not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL,
            audio_path TEXT,
            transcript_json TEXT NOT NULL,
            analysis_json TEXT NOT NULL,
            context_doc_name TEXT,
            context_doc_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_meeting(title, date, duration_seconds, audio_path, transcript, analysis, context_doc_name=None, context_doc_text=None):
    """
    Saves a meeting record into the database.
    transcript and analysis parameters should be python objects (list/dict), they will be saved as JSON.
    Returns the id of the saved meeting.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    transcript_str = json.dumps(transcript)
    analysis_str = json.dumps(analysis)
    
    cursor.execute("""
        INSERT INTO meetings (
            title, date, duration_seconds, audio_path, transcript_json, analysis_json, context_doc_name, context_doc_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, date, duration_seconds, audio_path, transcript_str, analysis_str, context_doc_name, context_doc_text))
    
    meeting_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meeting_id

def get_all_meetings():
    """
    Retrieves all meetings from the database, sorted by creation date descending.
    Returns a list of dictionaries with meeting details.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, date, duration_seconds, context_doc_name, created_at 
        FROM meetings 
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    meetings = []
    for row in rows:
        meetings.append(dict(row))
    return meetings

def get_meeting_details(meeting_id):
    """
    Retrieves full details of a specific meeting.
    Returns a dictionary or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        meeting = dict(row)
        # Deserialize JSON fields
        meeting["transcript"] = json.loads(meeting["transcript_json"])
        meeting["analysis"] = json.loads(meeting["analysis_json"])
        return meeting
    return None

def delete_meeting(meeting_id):
    """Deletes a meeting by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
    conn.commit()
    conn.close()
