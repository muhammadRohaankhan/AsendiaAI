import sqlite3
import json

class DBManager:
    def __init__(self, db_path='resumes.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Candidates table: we store a minimal set of fields for CSV rows.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                CandidateID TEXT PRIMARY KEY,
                Name TEXT,
                ResumeText TEXT
            )
        ''')
        # (Other tables for Experience, Education, Skills can be added similarly if needed.)
        self.conn.commit()

    def candidate_exists(self, candidate_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM candidates WHERE CandidateID = ?', (candidate_id,))
        return cursor.fetchone() is not None

    def insert_candidate(self, candidate_data: dict):
        """
        Inserts candidate data into the candidates table.
        candidate_data should be a dictionary with keys:
            CandidateID, Name, ResumeText
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO candidates (CandidateID, Name, ResumeText)
            VALUES (?, ?, ?)
        ''', (
            candidate_data.get("CandidateID"),
            candidate_data.get("Name", ""),
            candidate_data.get("ResumeText")
        ))
        self.conn.commit()

    def get_all_candidates(self):
        """
        Returns a list of tuples (CandidateID, ResumeText) from the candidates table.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT CandidateID, ResumeText FROM candidates')
        return cursor.fetchall()

    def get_candidate_by_id(self, candidate_id: str):
        """
        Returns candidate information (CandidateID, Name, ResumeText) for a given CandidateID.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT CandidateID, Name, ResumeText FROM candidates WHERE CandidateID = ?', (candidate_id,))
        return cursor.fetchone()
