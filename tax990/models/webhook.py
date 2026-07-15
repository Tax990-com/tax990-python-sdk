from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WebhookVerifyOptions:
    secret: str
    payload: str
    signature: str
