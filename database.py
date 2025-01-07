import requests
import sqlite3
import logging
from datetime import datetime
from config import DB_FILE

class DatabaseManager:
    @staticmethod
    def get_connection():
        """Create and return a database connection with error handling."""
        try:
            conn = sqlite3.connect(DB_FILE)
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            return None

    @staticmethod
    def init_db(initial_data=None):
        """Initialize database and populate with initial data if empty."""
        conn = DatabaseManager.get_connection()
        if not conn:
            logging.error("Failed to initialize database")
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    time INTEGER,
                    img TEXT
                )
            """)
            
            if initial_data:
                cursor.executemany(
                    "INSERT INTO events (type, time, img) VALUES (?, ?, ?)",
                    initial_data
                )
            
            conn.commit()
            logging.info("Database initialized successfully")
            return True
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def log_event(event_type, event_time, img_url):
        """Log a new event to the database."""
        conn = DatabaseManager.get_connection()
        if not conn:
            logging.error("Failed to log event - database connection failed")
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO events (type, time, img) VALUES (?, ?, ?)",
                (event_type, event_time, img_url)
            )
            conn.commit()
            logging.info(f"Event logged successfully: {event_type}")
            return True
        except sqlite3.Error as e:
            logging.error(f"Error logging event: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_last_event(event_type):
        """Get the most recent event of a specific type."""
        conn = DatabaseManager.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM events WHERE type = ? ORDER BY time DESC LIMIT 1",
                (event_type,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    @staticmethod
    def get_location_stats():
        """Get statistics about Pépito's locations."""
        conn = DatabaseManager.get_connection()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor()
            stats = {}
            
            # Get last known location and duration
            cursor.execute("""
                SELECT type, time 
                FROM events 
                ORDER BY time DESC 
                LIMIT 1
            """)
            last_event = cursor.fetchone()
            
            if last_event:
                stats['current_location'] = last_event[0]
                stats['current_duration'] = int(datetime.now().timestamp()) - last_event[1]
                
                opposite_type = 'out' if last_event[0] == 'in' else 'in'
                cursor.execute("""
                    SELECT time 
                    FROM events 
                    WHERE type = ? AND time < ? 
                    ORDER BY time DESC 
                    LIMIT 1
                """, (opposite_type, last_event[1]))
                
                prev_event = cursor.fetchone()
                if prev_event:
                    stats['last_transition_duration'] = last_event[1] - prev_event[0]
            
            return stats
        finally:
            conn.close()
