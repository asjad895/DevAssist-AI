import sqlite3
from datetime import datetime, timedelta
import uuid
import json
import os


DB_PATH = os.getenv("DB_PATH", "chat_sessions.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def initialize_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        created_at DATETIME,
        expires_at DATETIME,
        status TEXT
    )
    ''')

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Session_Data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp DATETIME,
        FOREIGN KEY (session_id) REFERENCES Sessions (session_id)
    )
    ''')

    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON Session_Data (session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON Sessions (user_id);")

    conn.commit()
    conn.close()

def serialize_content(content):
    return json.dumps(content)


def deserialize_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content


class SessionManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def create_session(self, session_id=None, duration_hours=.3):
        """Create a new session only if the session_id doesn't already exist in the database."""
        
        # If session_id is provided, use it; otherwise, create a new session ID.
        if not session_id:
            session_id = str(uuid.uuid4())  # Generate a new session_id if not provided

        # Check if session_id already exists in the database
        if self.is_session_exists(session_id):
            print(f"Session ID {session_id} already exists. Returning the existing session ID.")
            return session_id  

        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=duration_hours)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Sessions (session_id, created_at, expires_at, status)
        VALUES (?, ?, ?, 'active')
        ''', (session_id, created_at, expires_at))
        conn.commit()
        conn.close()

        return session_id

    def is_session_exists(self, session_id):
        """Check if a session already exists in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM Sessions WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def is_session_active(self, session_id):
        """Check if a session is active or expired."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT expires_at, status FROM Sessions WHERE session_id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return False  # Session not found

        expires_at, status = result
        if status != "active" or datetime.now() > datetime.fromisoformat(expires_at):
            self.expire_session(session_id)
            return False
        return True

    def expire_session(self, session_id):
        """Mark a session as expired."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Sessions SET status = 'inactive' WHERE session_id = ?
        ''', (session_id,))
        conn.commit()
        conn.close()

    def batch_expire_sessions(self):
        """Expire all sessions past their expiry time."""
        now = datetime.now()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Sessions SET status = 'inactive' WHERE expires_at < ? AND status = 'active'
        ''', (now,))
        conn.commit()
        conn.close()


class ChatHistoryManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def add_message(self, session_id, role, content):
        """Add a message to a session."""
        session_manager = SessionManager(self.db_path)
        if not session_manager.is_session_active(session_id):
            raise ValueError("Session has expired or does not exist.")

        timestamp = datetime.now()
        serialized_content = serialize_content(content)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Session_Data (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (session_id, role, serialized_content, timestamp))
        conn.commit()
        conn.close()

    def get_chat_history(self, session_id):
        """Retrieve all messages for a session."""
        session_manager = SessionManager(self.db_path)
        if not session_manager.is_session_active(session_id):
            raise ValueError("Session has expired or does not exist.")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT role, content, timestamp FROM Session_Data WHERE session_id = ?', (session_id,))
        rows = cursor.fetchall()
        conn.close()
        print(rows)
        history = []
        for role, content, timestamp in rows:
            history.append({
                "role": role,
                "content": deserialize_content(content)
            })
        return history


if __name__ == "__main__":
    initialize_db()

    session_manager = SessionManager()
    chat_manager = ChatHistoryManager()

    session_id = session_manager.create_session(session_id="user123")
    print(f"Session Created: {session_id}")


    try:
        chat_manager.add_message(session_id, "user", ["Hello", "How are you?"])
        chat_manager.add_message(session_id, "assistant", {"response": "I'm fine, thank you!"})
    except ValueError as e:
        print(e)

    try:
        history = chat_manager.get_chat_history(session_id)
        print("Chat History:")
        for message in history:
            print(message)
    except ValueError as e:
        print(e)

    session_manager.batch_expire_sessions()


