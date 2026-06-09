"""
esp.py — MARKETING email-service-provider adapters + segment routing.

The contact DB is the system of record; an ESP is a swappable OUTPUT. On
double-opt-in confirmation we push the contact to the ESP that matches its
segment:
  soft segment (crypto/esports/football news)  -> ESP_SOFT (e.g. Mailchimp)
  hard segment (casino/sports betting promos)   -> ESP_HARD (iGaming-tolerant)

NEVER route a hard/gambling segment to Mailchimp — it bans that content and
can terminate the account (and freeze the list).
"""
import os
import json
import hashlib
import asyncio
import logging
import urllib.request
import urllib.error

import emailcfg

logger = logging.getLogger(__name__)


class BaseESP:
    name = "base"
    async def push(self, rec: dict) -> bool:
        raise NotImplementedError


class NoopESP(BaseESP):
    """Dev / not-yet-configured. Records intent, sends nothing."""
    name = "noop"
    PUSHED: list = []
    async def push(self, rec: dict) -> bool:
        self.PUSHED.append({"email": rec.get("email"), "verticals": rec.get("verticals"),
                            "brand": rec.get("brand")})
        logger.info(f"[esp:noop] would push {rec.get('email')} ({rec.get('verticals')})")
        return True


class MailchimpESP(BaseESP):
    """Upsert a confirmed contact into a Mailchimp audience with interest tags.

    Use ONLY for the soft (non-gambling) segment. Marketing-Mailchimp prohibits
    gambling content.
    """
    name = "mailchimp"

    def __init__(self):
        self.key = emailcfg.MAILCHIMP_API_KEY
        self.list_id = emailcfg.MAILCHIMP_LIST_ID
        self.dc = emailcfg.MAILCHIMP_DC or (self.key.split("-")[-1] if "-" in self.key else "")

    def _ok(self) -> bool:
        return bool(self.key and self.list_id and self.dc)

    def _req(self, method, path, payload=None):
        url = f"https://{self.dc}.api.mailchimp.com/3.0{path}"
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Content-Type", "application/json")
        # Mailchimp uses HTTP basic auth: any user + apikey
        import base64
        token = base64.b64encode(f"anystring:{self.key}".encode()).decode()
        req.add_header("Authorization", f"Basic {token}")
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()

    def _push_sync(self, rec) -> bool:
        if not self._ok():
            logger.error("[esp:mailchimp] not configured (key/list/dc)")
            return False
        email = rec["email"]
        h = hashlib.md5(email.strip().lower().encode()).hexdigest()
        body = {
            "email_address": email,
            "status_if_new": "subscribed",
            "status": "subscribed",
            "merge_fields": {
                "BRAND": rec.get("brand", ""),
                "LANG": rec.get("lang", ""),
                "COUNTRY": rec.get("country", ""),
                "SOURCE": rec.get("source", ""),
                "WRAPPER": rec.get("wrapper", ""),
            },
        }
        try:
            self._req("PUT", f"/lists/{self.list_id}/members/{h}", body)
            # interest tags (verticals) — separate endpoint, tolerant of failure
            tags = [{"name": v, "status": "active"} for v in rec.get("verticals", [])]
            if tags:
                self._req("POST", f"/lists/{self.list_id}/members/{h}/tags", {"tags": tags})
            return True
        except urllib.error.HTTPError as e:
            logger.error(f"[esp:mailchimp] HTTP {e.code}: {e.read()[:200]}")
            return False
        except Exception as e:
            logger.error(f"[esp:mailchimp] error: {e}")
            return False

    async def push(self, rec) -> bool:
        return await asyncio.to_thread(self._push_sync, rec)


_REGISTRY = {"noop": NoopESP, "mailchimp": MailchimpESP}
_instances: dict = {}

def _get(name: str) -> BaseESP:
    name = name if name in _REGISTRY else "noop"
    if name not in _instances:
        _instances[name] = _REGISTRY[name]()
    return _instances[name]


async def push_contact(rec: dict) -> dict:
    """Route a confirmed contact to the ESP for its segment. Returns a small report."""
    seg = emailcfg.segment_for(rec.get("verticals"))
    esp_name = emailcfg.ESP_HARD if seg == "hard" else emailcfg.ESP_SOFT
    # Hard guard: never let a gambling segment go to Mailchimp.
    if seg == "hard" and esp_name == "mailchimp":
        logger.error("[esp] refusing to route hard/gambling segment to Mailchimp")
        esp_name = "noop"
    esp = _get(esp_name)
    ok = await esp.push(rec)
    return {"segment": seg, "esp": esp.name, "ok": ok}
