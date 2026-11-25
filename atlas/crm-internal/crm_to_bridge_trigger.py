"""
CRM -> AtlasPayBridge Trigger (`crm.atlas-si.com` -> `pay.atlas-si.com`)
Permite que uma automação do Atlas-Crm-OS (ou operador comercial / Hermes-Agent)
libere ou revogue automaticamente acessos no AtlasClub Campus (`club.atlashub.si`)
quando um negócio no CRM muda de etapa (ex: GANHO ou REEMBOLSADO).

Zero dependências externas (Python 3.10+ stdlib).
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any


def trigger_bridge(
    bridge_url: str,
    admin_key: str,
    action: str,
    email: str,
    name: str,
    offer_code: str,
    unit: str,
    deal_id: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    endpoint = "/api/grants" if action == "grant" else "/api/revokes"
    url = f"{bridge_url.rstrip('/')}{endpoint}"
    payload: dict[str, Any] = {
        "email": email.strip().lower(),
        "full_name": name.strip(),
        "offer_code": offer_code.strip(),
        "source_channel": "crm_manual",
        "external_ref": deal_id or f"crm_{unit}_{secrets.token_hex(4)}",
        "crm_unit": unit,
    }
    if action == "revoke":
        payload["reason"] = f"crm_revoke:{deal_id or unit}"

    if dry_run:
        return {"dry_run": True, "target_url": url, "payload": payload}

    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Admin-Key": admin_key,
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AtlasPayBridge HTTP {exc.code}: {body}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Trigger AtlasClub access from Atlas-Crm-OS deal")
    parser.add_argument("--bridge-url", default=os.environ.get("ATLAS_PAY_BRIDGE_URL", "http://127.0.0.1:8790"))
    parser.add_argument("--admin-key", default=os.environ.get("ATLAS_PAY_BRIDGE_ADMIN_KEY", "atlas-dev-admin-key"))
    parser.add_argument("--action", choices=["grant", "revoke"], default="grant")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--offer", default="club_premium")
    parser.add_argument("--unit", default="AtlasClub-Commercial")
    parser.add_argument("--deal-id", default="")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    out = trigger_bridge(
        bridge_url=args.bridge_url,
        admin_key=args.admin_key,
        action=args.action,
        email=args.email,
        name=args.name,
        offer_code=args.offer,
        unit=args.unit,
        deal_id=args.deal_id,
        dry_run=args.dry_run,
    )
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
