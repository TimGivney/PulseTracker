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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

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
            keys = list(data.keys())
            columns = ', '.join(keys)
            placeholders = ', '.join(['?' for _ in keys])
            sql = f"INSERT INTO equipment ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, [data[k] for k in keys])
            conn.commit()
            return cursor.lastrowid

    def update_equipment(self, equip_id, data):
        """Update an existing equipment record"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            values = list(data.values()) + [equip_id]
            sql = f"UPDATE equipment SET {set_clause} WHERE id = ?"
            cursor.execute(sql, values)
            conn.commit()

    def delete_equipment(self, equip_id):
        """Delete an equipment record and its associated attachments/files"""
        attachments = self.get_attachments(equip_id)
        for att in attachments:
            filepath = att['filepath'] if isinstance(att, sqlite3.Row) else att[3]
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attachments WHERE equipment_id = ?", (equip_id,))
            cursor.execute("DELETE FROM equipment WHERE id = ?", (equip_id,))
            conn.commit()

    def search_equipment(self, query=None, status_filter=None):
        """Search and filter equipment records"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM equipment WHERE 1=1"
            params = []
            if query:
                q = f"%{query.strip()}%"
                sql += " AND (name LIKE ? OR serial_number LIKE ? OR owner_individual LIKE ? OR owner_company LIKE ? OR location LIKE ? OR job_number LIKE ?)"
                params.extend([q, q, q, q, q, q])
            if status_filter and status_filter != "All":
                sql += " AND status = ?"
                params.append(status_filter)
            sql += " ORDER BY created_at DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()

    def get_all_equipment(self):
        """Get all equipment for the main list"""
        return self.search_equipment()

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

    def delete_attachment(self, attachment_id):
        """Delete a single attachment record and file"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filepath FROM attachments WHERE id = ?", (attachment_id,))
            row = cursor.fetchone()
            if row:
                filepath = row['filepath'] if isinstance(row, sqlite3.Row) else row[0]
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
                conn.commit()

    def get_attachments(self, equipment_id):
        """Get all files for an asset"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM attachments WHERE equipment_id = ?", (equipment_id,))
            return cursor.fetchall()

    def save_high_score(self, score, round_num, player_name="Pilot"):
        """Save a new high score"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO high_scores (player_name, score, round) VALUES (?, ?, ?)", (player_name, score, round_num))
            conn.commit()

    def get_top_scores(self, limit=5):
        """Get top high scores"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT player_name, score, round, achieved_at FROM high_scores ORDER BY score DESC LIMIT ?", (limit,))
            return cursor.fetchall()

    def get_owner_stats(self):
        """Get statistics for the pie charts"""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT owner_individual, owner_company FROM equipment", conn)
            return df

    def export_all_equipment(self):
        """Retrieve all equipment data as a pandas DataFrame for export"""
        with self._get_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM equipment ORDER BY id ASC", conn)
            return df
