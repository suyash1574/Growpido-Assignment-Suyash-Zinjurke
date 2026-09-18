import pytest
import sqlite3
import uuid
from datetime import datetime
from src.storage.db import Database
from src.storage.models import AuditEvent

def test_audit_log_engine_immutability():
    db = Database(db_path=":memory:")
    prospect_id = uuid.uuid4()
    
    event = AuditEvent(
        prospect_id=prospect_id,
        event_type="TEST_INIT",
        actor="System",
        event_payload={"test": "initial"}
    )
    db.log_audit(event)
    
    conn = db.get_connection()
    # Verify insert succeeded
    rows = conn.execute("SELECT * FROM audit_log WHERE prospect_id = ?", (str(prospect_id),)).fetchall()
    assert len(rows) == 1
    
    # Attempt direct UPDATE on audit_log - must be rejected by SQLite engine trigger
    with pytest.raises((sqlite3.OperationalError, sqlite3.IntegrityError)) as exc_update:
        conn.execute("UPDATE audit_log SET event_payload = 'tampered' WHERE prospect_id = ?", (str(prospect_id),))
    assert "IMMUTABLE_AUDIT_LOG" in str(exc_update.value)
    
    # Attempt direct DELETE on audit_log - must be rejected by SQLite engine trigger
    with pytest.raises((sqlite3.OperationalError, sqlite3.IntegrityError)) as exc_delete:
        conn.execute("DELETE FROM audit_log WHERE prospect_id = ?", (str(prospect_id),))
    assert "IMMUTABLE_AUDIT_LOG" in str(exc_delete.value)
