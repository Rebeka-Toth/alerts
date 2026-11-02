"""Channel abstraction. To add a channel: subclass Channel, decorate with @register."""
import json
import os
import urllib.request
from abc import ABC, abstractmethod

REGISTRY: dict[str, "Channel"] = {}


def register(cls):
    inst = cls()
    REGISTRY[inst.name] = inst
    return cls


class Channel(ABC):
    name: str

    @abstractmethod
    def send(self, user: dict, event: dict) -> None:
        """Deliver the event. Must raise on failure; never swallow errors."""


@register
class EmailChannel(Channel):
    name = "email"

    def send(self, user, event):
        # Demo: console "outbox". A real SMTP/SES sender would replace this body only.
        print(f"[EMAIL to {user['email']}] [{event['category']}/{event['severity']}] {event['title']}")


@register
class SlackChannel(Channel):
    name = "slack"

    def send(self, user, event):
        url = user.get("slack_webhook") or os.environ.get("SLACK_WEBHOOK_URL")
        if not url:
            raise RuntimeError("no Slack webhook configured for this user")
        text = f"*[{event['category']} | severity {event['severity']}]* {event['title']}\n{event['body']}"
        req = urllib.request.Request(
            url,
            data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status >= 300:
                raise RuntimeError(f"slack returned HTTP {resp.status}")
