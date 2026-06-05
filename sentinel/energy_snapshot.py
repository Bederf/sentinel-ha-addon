from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EnergySnapshot:
    entity_id: str
    metric_type: str
    state: str
    attributes: dict | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "metric_type": self.metric_type,
            "state": self.state,
            "attributes": self.attributes or {},
            "timestamp": self.timestamp,
        }
