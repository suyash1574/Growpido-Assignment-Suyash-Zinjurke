from uuid import UUID
from typing import Dict, Any, Optional
from src.storage.db import Database
from src.storage.models import AuditEvent

class AuditLogger:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or Database()

    def log(self, prospect_id: UUID, event_type: str, payload: Dict[str, Any], actor: str = "SYSTEM_AGENT"):
        event = AuditEvent(
            prospect_id=prospect_id,
            event_type=event_type,
            actor=actor,
            event_payload=payload
        )
        self.db.log_audit(event)
        return event
