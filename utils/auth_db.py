import os
import sqlite3
import bcrypt
from datetime import datetime
from typing import Optional, Dict

# Get project root (one level up from utils)
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(UTILS_DIR)

class UserDatabase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = os.path.join(PROJECT_ROOT, "data/users.db")
        else:
            self.db_path = db_path
            
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the users database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print(f"✅ User database initialized at {self.db_path}")
    
    def create_user(self, email: str, password: str, full_name: str) -> Dict:
        """
        Create a new user account
        
        Args:
            email: User's email address (unique)
            password: Plain text password (will be hashed)
            full_name: User's full name
            
        Returns:
            Dict with user info (without password)
            
        Raises:
            ValueError: If email already exists
        """
        # Normalize email
        email = email.lower().strip()
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (email, password_hash, full_name)
                VALUES (?, ?, ?)
            """, (email, password_hash, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            print(f"✅ User created: {email}")
            
            return {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "created_at": datetime.now().isoformat()
            }
            
        except sqlite3.IntegrityError:
            raise ValueError(f"User with email {email} already exists")
    
    def verify_user(self, email: str, password: str) -> Optional[Dict]:
        """
        Verify user credentials
        
        Args:
            email: User's email
            password: Plain text password to verify
            
        Returns:
            User dict if credentials are valid, None otherwise
        """
        email = email.lower().strip()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, password_hash, full_name, created_at
            FROM users
            WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        user_id, email, password_hash, full_name, created_at = row
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            # Update last login
            self._update_last_login(email)
            
            return {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "created_at": created_at
            }
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user details by email (without password)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, full_name, created_at, last_login
            FROM users
            WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "created_at": row[3],
                "last_login": row[4]
            }
        
        return None
    
    def _update_last_login(self, email: str):
        """Update the last login timestamp for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE email = ?
        """, (email,))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self) -> list:
        """Get all users (admin function, without passwords)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, full_name, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "created_at": row[3],
                "last_login": row[4]
            }
            for row in rows
        ]
