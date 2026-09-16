import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import UUID
from src.config import SQLITE_DB_PATH
from src.storage.models import Prospect, EvidenceSource, Claim, StrategicGap, AuditEvent

class Database:
    def __init__(self, db_path: str = SQLITE_DB_PATH):
        self.db_path = db_path
        self._memory_conn = None
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        else:
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
        self.init_schema()

    def get_connection(self):
        if self._memory_conn:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def init_schema(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS prospects (
            prospect_id TEXT PRIMARY KEY,
            linkedin_url TEXT NOT NULL,
            slug TEXT NOT NULL,
            full_name TEXT NOT NULL,
            current_company TEXT,
            primary_role TEXT,
            location_country TEXT DEFAULT 'UAE',
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS evidence_sources (
            source_id TEXT PRIMARY KEY,
            prospect_id TEXT NOT NULL,
            url TEXT NOT NULL,
            domain TEXT NOT NULL,
            source_tier TEXT NOT NULL,
            http_status INTEGER,
            content_hash TEXT NOT NULL,
            raw_text_snippet TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id TEXT PRIMARY KEY,
            prospect_id TEXT NOT NULL,
            claim_text TEXT NOT NULL,
            category TEXT NOT NULL,
            materiality TEXT NOT NULL,
            status TEXT NOT NULL,
            primary_source_id TEXT,
            primary_source_url TEXT,
            secondary_source_id TEXT,
            secondary_source_url TEXT,
            check1_passed INTEGER DEFAULT 0,
            check2_passed INTEGER DEFAULT 0,
            contradiction_detected INTEGER DEFAULT 0,
            contradiction_details TEXT,
            refusal_code TEXT,
            refusal_reason TEXT,
            human_override INTEGER DEFAULT 0,
            override_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS strategic_gaps (
            gap_id TEXT PRIMARY KEY,
            prospect_id TEXT NOT NULL,
            rank INTEGER NOT NULL,
            dimension TEXT NOT NULL,
            title TEXT NOT NULL,
            observation TEXT NOT NULL,
            strategic_impact TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            event_id TEXT PRIMARY KEY,
            prospect_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            event_payload TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
        );
        """)
        conn.commit()

    def save_prospect(self, p: Prospect):
        conn = self.get_connection()
        conn.execute("""
        INSERT OR REPLACE INTO prospects (prospect_id, linkedin_url, slug, full_name, current_company, primary_role, location_country, status, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (str(p.prospect_id), p.linkedin_url, p.slug, p.full_name, p.current_company, p.primary_role, p.location_country, p.status.value))
        conn.commit()

    def save_sources(self, sources: List[EvidenceSource]):
        conn = self.get_connection()
        for s in sources:
            conn.execute("""
            INSERT OR REPLACE INTO evidence_sources (source_id, prospect_id, url, domain, source_tier, http_status, content_hash, raw_text_snippet)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(s.source_id), str(s.prospect_id), s.url, s.domain, s.source_tier.value, s.http_status, s.content_hash, s.raw_text_snippet))
        conn.commit()

    def save_claims(self, claims: List[Claim]):
        conn = self.get_connection()
        for c in claims:
            conn.execute("""
            INSERT OR REPLACE INTO claims (
                claim_id, prospect_id, claim_text, category, materiality, status,
                primary_source_id, primary_source_url, secondary_source_id, secondary_source_url,
                check1_passed, check2_passed, contradiction_detected, contradiction_details,
                refusal_code, refusal_reason, human_override, override_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(c.claim_id), str(c.prospect_id), c.claim_text, c.category.value, c.materiality.value, c.status.value,
                str(c.primary_source_id) if c.primary_source_id else None, c.primary_source_url,
                str(c.secondary_source_id) if c.secondary_source_id else None, c.secondary_source_url,
                1 if c.check1_passed else 0, 1 if c.check2_passed else 0,
                1 if c.contradiction_detected else 0, c.contradiction_details,
                c.refusal_code, c.refusal_reason, 1 if c.human_override else 0, c.override_notes
            ))
        conn.commit()

    def save_gaps(self, gaps: List[StrategicGap]):
        conn = self.get_connection()
        for g in gaps:
            conn.execute("""
            INSERT OR REPLACE INTO strategic_gaps (gap_id, prospect_id, rank, dimension, title, observation, strategic_impact, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(g.gap_id), str(g.prospect_id), g.rank, g.dimension.value, g.title, g.observation, g.strategic_impact, g.recommendation))
        conn.commit()

    def log_audit(self, event: AuditEvent):
        conn = self.get_connection()
        conn.execute("""
        INSERT INTO audit_log (event_id, prospect_id, event_type, actor, event_payload)
        VALUES (?, ?, ?, ?, ?)
        """, (str(event.event_id), str(event.prospect_id), event.event_type, event.actor, json.dumps(event.event_payload)))
        conn.commit()

    def get_prospect(self, prospect_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM prospects WHERE prospect_id = ?", (prospect_id,)).fetchone()
        return dict(row) if row else None

    def get_claims(self, prospect_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM claims WHERE prospect_id = ? ORDER BY created_at ASC", (prospect_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_gaps(self, prospect_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM strategic_gaps WHERE prospect_id = ? ORDER BY rank ASC", (prospect_id,)).fetchall()
        return [dict(r) for r in rows]

    def get_audit_log(self, prospect_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM audit_log WHERE prospect_id = ? ORDER BY timestamp ASC", (prospect_id,)).fetchall()
        return [dict(r) for r in rows]
