from dataclasses import dataclass
from typing import Any

@dataclass
class Notification:
    recipient: str
    subject: str
    body: str
    metadata: dict[str, Any] | None = None
    html_body: str | None = None