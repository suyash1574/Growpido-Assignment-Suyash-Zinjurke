import sqlite3
import json
import hashlib
from datetime import datetime
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
            sector TEXT DEFAULT 'Executive Leadership',
            track_b_compliant INTEGER DEFAULT 1,
            compliance_notes TEXT,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        try:
            cur.execute("ALTER TABLE prospects ADD COLUMN sector TEXT DEFAULT 'Executive Leadership'")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE prospects ADD COLUMN track_b_compliant INTEGER DEFAULT 1")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE prospects ADD COLUMN compliance_notes TEXT")
        except Exception:
            pass
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
            prev_hash TEXT NOT NULL DEFAULT 'GENESIS',
            event_hash TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(prospect_id) REFERENCES prospects(prospect_id)
        );
        """)
        try:
            cur.execute("ALTER TABLE audit_log ADD COLUMN prev_hash TEXT NOT NULL DEFAULT 'GENESIS'")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE audit_log ADD COLUMN event_hash TEXT NOT NULL DEFAULT ''")
        except Exception:
            pass

        # Engine-level SQLite immutability triggers: physically prohibit UPDATE or DELETE
        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_audit_log_prevent_update
        BEFORE UPDATE ON audit_log
        BEGIN
            SELECT RAISE(ABORT, 'IMMUTABLE_AUDIT_LOG: Direct updates are strictly prohibited on append-only cryptographic audit log');
        END;
        """)
        cur.execute("""
        CREATE TRIGGER IF NOT EXISTS trg_audit_log_prevent_delete
        BEFORE DELETE ON audit_log
        BEGIN
            SELECT RAISE(ABORT, 'IMMUTABLE_AUDIT_LOG: Direct deletions are strictly prohibited on append-only cryptographic audit log');
        END;
        """)
        conn.commit()

    def save_prospect(self, p: Prospect):
        conn = self.get_connection()
        conn.execute("""
        INSERT OR REPLACE INTO prospects (
            prospect_id, linkedin_url, slug, full_name, current_company, primary_role,
            location_country, sector, track_b_compliant, compliance_notes, status, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(p.prospect_id), p.linkedin_url, p.slug, p.full_name, p.current_company, p.primary_role,
            p.location_country, getattr(p, "sector", "Executive Leadership"),
            1 if getattr(p, "track_b_compliant", True) else 0,
            getattr(p, "compliance_notes", None),
            p.status.value
        ))
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
        """
        Appends an audit event to the cryptographically verifiable, immutable SHA-256 hash chain.
        """
        conn = self.get_connection()
        # Find head hash of the existing chain for this prospect
        row = conn.execute(
            "SELECT event_hash FROM audit_log WHERE prospect_id = ? ORDER BY rowid DESC LIMIT 1",
            (str(event.prospect_id),)
        ).fetchone()

        prev_hash = row[0] if (row and row[0]) else "GENESIS"
        canonical_payload = json.dumps(event.event_payload, sort_keys=True)
        ts_str = event.timestamp.isoformat()
        to_hash = f"{prev_hash}|{str(event.prospect_id)}|{event.event_type}|{event.actor}|{canonical_payload}|{ts_str}"
        event_hash = hashlib.sha256(to_hash.encode("utf-8")).hexdigest()

        event.prev_hash = prev_hash
        event.event_hash = event_hash

        conn.execute("""
        INSERT INTO audit_log (event_id, prospect_id, event_type, actor, event_payload, timestamp, prev_hash, event_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(event.event_id), str(event.prospect_id), event.event_type, event.actor, canonical_payload, ts_str, prev_hash, event_hash))
        conn.commit()

    def verify_audit_trail(self, prospect_id: str) -> Dict[str, Any]:
        """
        Cryptographically verifies the immutable SHA-256 hash chain for a prospect's audit log.
        """
        conn = self.get_connection()
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE prospect_id = ? ORDER BY rowid ASC",
            (str(prospect_id),)
        ).fetchall()

        if not rows:
            return {
                "valid": True,
                "total_events": 0,
                "head_hash": "GENESIS",
                "details": "No audit records found."
            }

        expected_prev = "GENESIS"
        for idx, r in enumerate(rows):
            prev_h = r["prev_hash"] if "prev_hash" in r.keys() else ""
            curr_h = r["event_hash"] if "event_hash" in r.keys() else ""
            if not curr_h or not prev_h:
                return {
                    "valid": False,
                    "total_events": len(rows),
                    "failed_at_index": idx,
                    "reason": f"Broken audit integrity at event {r['event_id']}: missing cryptographic hash. Unhashed or legacy blocks are strictly prohibited."
                }

            if prev_h != expected_prev:
                return {
                    "valid": False,
                    "total_events": len(rows),
                    "failed_at_index": idx,
                    "reason": f"Broken chain at event {r['event_id']}: expected prev_hash '{expected_prev}', found '{prev_h}'"
                }

            to_hash = f"{prev_h}|{r['prospect_id']}|{r['event_type']}|{r['actor']}|{r['event_payload']}|{r['timestamp']}"
            recomputed = hashlib.sha256(to_hash.encode("utf-8")).hexdigest()
            if recomputed != curr_h:
                return {
                    "valid": False,
                    "total_events": len(rows),
                    "failed_at_index": idx,
                    "reason": f"Hash mismatch at event {r['event_id']}: expected '{recomputed}', found '{curr_h}'"
                }
            expected_prev = curr_h

        return {
            "valid": True,
            "total_events": len(rows),
            "head_hash": expected_prev,
            "details": f"Cryptographically verified chain of {len(rows)} immutable audit events."
        }

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

    def update_claim_status(self, claim_id: str, new_status: str, notes: str = "") -> bool:
        conn = self.get_connection()
        cur = conn.execute("""
        UPDATE claims 
        SET status = ?, human_override = 1, override_notes = ?
        WHERE claim_id = ?
        """, (new_status, notes, claim_id))
        conn.commit()
        return cur.rowcount > 0

    def update_prospect_status(self, prospect_id: str, new_status: str) -> bool:
        conn = self.get_connection()
        cur = conn.execute("""
        UPDATE prospects
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE prospect_id = ?
        """, (new_status, prospect_id))
        conn.commit()
        return cur.rowcount > 0

    def get_claim(self, claim_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM claims WHERE claim_id = ?", (claim_id,)).fetchone()
        return dict(row) if row else None

    def get_audit_log(self, prospect_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM audit_log WHERE prospect_id = ? ORDER BY timestamp ASC", (prospect_id,)).fetchall()
        return [dict(r) for r in rows]
