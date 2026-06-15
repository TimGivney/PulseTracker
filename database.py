import sqlite3
import os
import pandas as pd
from datetime import datetime
import shutil

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.attachments_dir = os.path.join(os.path.dirname(db_path), "attachments")
        os.makedirs(self.attachments_dir, exist_ok=True)
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Equipment Table - Refactored for v5.0+ Deep Data Collection
            # Removed all Python-style comments from inside the SQL string to fix "unrecognized token: #" error
            cursor.execute("""CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                
                manufacture_date DATE,
                manufacture_location TEXT,
                batch_id TEXT,
                batch_size INTEGER DEFAULT 1,
                job_number TEXT,
                qa_status TEXT,
                
                sale_status TEXT,
                sale_date DATE,
                invoice_number TEXT,
                warranty_end DATE,
                install_date DATE,
                status TEXT DEFAULT 'Active',
                
                owner_individual TEXT,
                owner_company TEXT,
                owner_notes TEXT,
                location TEXT,
                
                billing_address TEXT,
                billing_suburb TEXT,
                billing_state TEXT,
                billing_postcode TEXT,
                billing_country TEXT,
                payment_methods TEXT,
                
                shipping_address TEXT,
                shipping_suburb TEXT,
                shipping_state TEXT,
                shipping_postcode TEXT,
                shipping_country TEXT,
                parts_destination TEXT,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )""")

            # 2. Attachments
            cursor.execute("""CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                filetype TEXT,
                description TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id) ON DELETE CASCADE
            )""")

            # 3. High Scores Table
            cursor.execute("""CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT DEFAULT 'Pilot',
                score INTEGER NOT NULL,
                round INTEGER,
                achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")

            # 4. Settings
            cursor.execute("""CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )""")
            
            conn.commit()

    def add_equipment(self, data):
        """Add equipment with full v5.0+ details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            keys = data.keys()
            columns = ', '.join(keys)
            placeholders = ', '.join(['?' for _ in keys])
            sql = f"INSERT INTO equipment ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            conn.commit()
            return cursor.lastrowid

    def get_all_equipment(self):
        """Get all equipment for the main list"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment ORDER BY created_at DESC")
            return cursor.fetchall()

    def get_equipment_by_id(self, equip_id):
        """Get full details for a single asset"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment WHERE id = ?", (equip_id,))
            return cursor.fetchone()

    def add_attachment(self, equipment_id, filename, filepath, filetype="", description=""):
        """Link a file to an asset"""
        dest_path = os.path.join(self.attachments_dir, f"{equipment_id}_{filename}")
        shutil.copy2(filepath, dest_path)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO attachments (equipment_id, filename, filepath, filetype, description)
                            VALUES (?, ?, ?, ?, ?)""", (equipment_id, filename, dest_path, filetype, description))
            conn.commit()
            return cursor.lastrowid

    def get_attachments(self, equipment_id):
        """Get all files for an asset"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attachments WHERE equipment_id = ?", (equipment_id,))
            return cursor.fetchall()

    def save_high_score(self, score, round_num):
        """Save a new high score"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO high_scores (score, round) VALUES (?, ?)", (score, round_num))
            conn.commit()

    def get_top_scores(self, limit=5):
        """Get top high scores"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT score, round, achieved_at FROM high_scores ORDER BY score DESC LIMIT ?", (limit,))
            return cursor.fetchall()

    def get_owner_stats(self):
        """Get statistics for the pie charts"""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT owner_individual, owner_company FROM equipment", conn)
            return df
