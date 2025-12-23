"""Database management for BankPulse"""

import sqlite3
from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_PATH, DATA_DIR


class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.Session = sessionmaker(bind=self.engine)
    
    def init_database(self):
        """Initialize database schema"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS h8_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    value REAL,
                    bank_type TEXT,
                    asset_class TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(series_name, date)
                )
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_date ON h8_data(date)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_series ON h8_data(series_name)
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS data_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    update_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    records_added INTEGER,
                    status TEXT
                )
            """))
            conn.commit()
    
    def insert_data(self, df: pd.DataFrame):
        """Insert H8 data into database"""
        df.to_sql('h8_data', self.engine, if_exists='append', index=False)
    
    def get_data(self, series_name: Optional[str] = None, 
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None) -> pd.DataFrame:
        """Query H8 data from database"""
        query = "SELECT * FROM h8_data WHERE 1=1"
        params = {}
        
        if series_name:
            query += " AND series_name = :series_name"
            params['series_name'] = series_name
        
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        return pd.read_sql(query, self.engine, params=params)
    
    def get_latest_date(self) -> Optional[str]:
        """Get the latest date in the database"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(date) as max_date FROM h8_data"))
            row = result.fetchone()
            return row[0] if row else None
    
    def record_update(self, records_added: int, status: str):
        """Record data update information"""
        with self.engine.connect() as conn:
            conn.execute(
                text("INSERT INTO data_updates (records_added, status) VALUES (:records, :status)"),
                {"records": records_added, "status": status}
            )
            conn.commit()
