import json
from pathlib import Path
from typing import List, Dict, Any
from src.storage.models import Prospect, Claim, StrategicGap, AuditEvent

class Exporter:
    @classmethod
    def export_audit_json(
        cls,
        prospect: Prospect,
        claims: List[Claim],
        gaps: List[StrategicGap],
        audit_events: List[Dict[str, Any]],
        output_path: str
    ):
        payload = {
            "prospect": prospect.model_dump(mode="json"),
            "total_claims": len(claims),
            "claims": [c.model_dump(mode="json") for c in claims],
            "strategic_gaps": [g.model_dump(mode="json") for g in gaps],
            "audit_trail": audit_events
        }
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return output_path
