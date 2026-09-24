import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config import settings

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_URL.replace("sqlite:///", "")
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clinics (
                    clinic_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    visit_id TEXT PRIMARY KEY,
                    clinic_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    date TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    doctor_id TEXT,
                    payment_mode TEXT NOT NULL,
                    amount_paid_paise INTEGER NOT NULL,
                    discount_paise INTEGER NOT NULL DEFAULT 0,
                    is_refund BOOLEAN NOT NULL DEFAULT 0,
                    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS line_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visit_id TEXT NOT NULL,
                    drug_name TEXT NOT NULL,
                    qty INTEGER NOT NULL,
                    unit_price_paise INTEGER NOT NULL,
                    FOREIGN KEY (visit_id) REFERENCES visits(visit_id) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clinic_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_rows INTEGER NOT NULL,
                    valid_rows INTEGER NOT NULL,
                    malformed_rows INTEGER NOT NULL,
                    errors_json TEXT
                );
            """)
            conn.commit()

    def save_visits_atomically(
        self,
        clinic_id: str,
        clinic_name: str,
        date_str: str,
        valid_visits: List[Dict[str, Any]],
        total_rows: int,
        malformed_count: int,
        errors: List[Dict[str, Any]]
    ) -> bool:
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO clinics (clinic_id, name) VALUES (?, ?) ON CONFLICT(clinic_id) DO UPDATE SET name = excluded.name",
                    (clinic_id, clinic_name)
                )

                cursor.execute(
                    "SELECT visit_id FROM visits WHERE clinic_id = ? AND date = ?",
                    (clinic_id, date_str)
                )
                existing_visit_ids = [row["visit_id"] for row in cursor.fetchall()]

                if existing_visit_ids:
                    placeholders = ",".join(["?"] * len(existing_visit_ids))
                    cursor.execute(f"DELETE FROM line_items WHERE visit_id IN ({placeholders})", existing_visit_ids)
                    cursor.execute("DELETE FROM visits WHERE clinic_id = ? AND date = ?", (clinic_id, date_str))

                for visit in valid_visits:
                    ts = visit["timestamp"]
                    ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
                    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    hour = dt.hour

                    cursor.execute("""
                        INSERT INTO visits (
                            visit_id, clinic_id, timestamp, date, hour,
                            doctor_id, payment_mode, amount_paid_paise,
                            discount_paise, is_refund
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        visit["visit_id"],
                        clinic_id,
                        ts_str,
                        date_str,
                        hour,
                        visit.get("doctor_id"),
                        visit["payment_mode"],
                        visit["amount_paid_paise"],
                        visit.get("discount_paise", 0),
                        1 if visit.get("is_refund", False) else 0
                    ))

                    for item in visit.get("line_items", []):
                        cursor.execute("""
                            INSERT INTO line_items (visit_id, drug_name, qty, unit_price_paise)
                            VALUES (?, ?, ?, ?)
                        """, (
                            visit["visit_id"],
                            item["drug_name"].strip().upper(),
                            item["qty"],
                            item["unit_price_paise"]
                        ))

                cursor.execute("""
                    INSERT INTO ingestion_logs (clinic_id, date, total_rows, valid_rows, malformed_rows, errors_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    clinic_id,
                    date_str,
                    total_rows,
                    len(valid_visits),
                    malformed_count,
                    json.dumps(errors)
                ))

            return True
        finally:
            conn.close()

    def get_visits(self, clinic_id: Optional[str] = None, date_str: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM visits WHERE 1=1"
            params = []
            if clinic_id:
                query += " AND clinic_id = ?"
                params.append(clinic_id)
            if date_str:
                query += " AND date = ?"
                params.append(date_str)
            query += " ORDER BY timestamp ASC"

            cursor.execute(query, params)
            visits = [dict(row) for row in cursor.fetchall()]

            for v in visits:
                cursor.execute("SELECT drug_name, qty, unit_price_paise FROM line_items WHERE visit_id = ?", (v["visit_id"],))
                v["line_items"] = [dict(item) for item in cursor.fetchall()]
                v["is_refund"] = bool(v["is_refund"])
            return visits
        finally:
            conn.close()

    def get_available_dates(self, clinic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            query = """
                SELECT v.date, v.clinic_id, c.name as clinic_name,
                       COUNT(*) as total_visits,
                       SUM(CASE WHEN v.is_refund = 0 THEN 1 ELSE 0 END) as sales_visits,
                       SUM(CASE WHEN v.is_refund = 1 THEN 1 ELSE 0 END) as refund_visits,
                       SUM(CASE WHEN v.is_refund = 0 THEN v.amount_paid_paise ELSE 0 END) as total_collected_paise
                FROM visits v
                LEFT JOIN clinics c ON v.clinic_id = c.clinic_id
            """
            params = []
            if clinic_id:
                query += " WHERE v.clinic_id = ?"
                params.append(clinic_id)
            query += " GROUP BY v.date, v.clinic_id ORDER BY v.date DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

db = Database()
