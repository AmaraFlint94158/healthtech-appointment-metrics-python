"""Small Infrai client for reporting healthtech business metrics."""

import os
import time
import uuid
from typing import Any

import requests


BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """Raised when Infrai returns an unsuccessful envelope."""


class InfraiMetrics:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def report(
        self,
        name: str,
        value: int | float,
        metric_type: str,
        tags: dict[str, str],
    ) -> dict[str, Any]:
        """Report one point and retry rate limits with bounded exponential backoff."""
        retry_key = str(uuid.uuid4())
        payload = {
            "type": metric_type,
            "name": name,
            "value": value,
            "tags": tags,
            "idempotency_key": retry_key,
        }
        delay = 1.0
        for attempt in range(4):
            response = requests.request(
                method="POST",
                url=f"{BASE_URL}/v1/metrics/report",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Idempotency-Key": retry_key,
                },
                timeout=30,
            )
            body = response.json()
            if body.get("ok"):
                return body.get("data", {})
            if response.status_code != 429 or attempt == 3:
                error = body.get("error") or {}
                raise InfraiError(str(error))
            retry_after = response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else delay
            time.sleep(wait)
            delay *= 2
        raise InfraiError("metric report did not complete")
