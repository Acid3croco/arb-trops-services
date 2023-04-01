from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ProcessData:
    name: str
    pid: Optional[int] = None
    status: str = 'DOWN'
    last_status_change: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.last_status_change, str):
            self.last_status_change = float(self.last_status_change)
        if isinstance(self.last_status_change, float):
            self.last_status_change = datetime.fromtimestamp(
                self.last_status_change)
