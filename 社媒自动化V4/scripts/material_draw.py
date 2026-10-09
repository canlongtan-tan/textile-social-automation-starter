#!/usr/bin/env python3
"""Manage a global no-repeat material draw pool with reserve/commit semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import secrets
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "素材库" / "第01批-20个" / "manifest.json"
DEFAULT_STATE = ROOT / "社媒自动化V4" / "state" / "material-draw-state.json"
TIMEZONE = ZoneInfo("Asia/Shanghai")


def now() -> str:
    return datetime.now(TIMEZONE).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(manifest: dict) -> None:
    items = manifest.get("items", [])
    if manifest.get("count") != 20 or len(items) != 20:
        raise SystemExit("Material manifest must contain exactly 20 items")
    urls = [item["source_url"] for item in items]
    hashes = [item["sha256"] for item in items]
    if len(urls) != len(set(urls)):
        raise SystemExit("Duplicate product URL in material manifest")
    if len(hashes) != len(set(hashes)):
        raise SystemExit("Duplicate SHA-256 in material manifest")
    for item in items:
        source = ROOT / item["source_path"]
        sidecar = ROOT / item["sidecar_path"]
        if not source.is_file() or not sidecar.is_file():
            raise SystemExit(f"Missing source or sidecar for material {item['id']}")
        if sha256_file(source) != item["sha256"]:
            raise SystemExit(f"SHA-256 mismatch for material {item['id']}")


def init_state(args: argparse.Namespace) -> None:
    manifest = load_json(args.manifest)
    validate_manifest(manifest)
    old = load_json(args.state) if args.state.is_file() else {"materials": {}}
    old_materials = old.get("materials", {})
    materials = {}
    for item in manifest["items"]:
        previous = old_materials.get(item["sha256"], {})
        materials[item["sha256"]] = {
            "id": item["id"],
            "product": item["product"],
            "source_path": item["source_path"],
            "sidecar_path": item["sidecar_path"],
            "source_url": item["source_url"],
            "status": previous.get("status", "available"),
            "draw_id": previous.get("draw_id"),
            "platform": previous.get("platform"),
            "reserved_at": previous.get("reserved_at"),
            "used_at": previous.get("used_at"),
        }
    state = {
        "schema_version": 1,
        "policy": "global-no-repeat-after-commit",
        "manifest": str(args.manifest.relative_to(ROOT)),
        "updated_at": now(),
        "materials": materials,
        "history": old.get("history", []),
    }
    write_json(args.state, state)
    print_status(state)


def print_status(state: dict) -> None:
    counts = {"available": 0, "reserved": 0, "used": 0}
    for item in state["materials"].values():
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print(json.dumps({"total": len(state["materials"]), **counts}, ensure_ascii=False, indent=2))


def draw(args: argparse.Namespace) -> None:
    state = load_json(args.state)
    choices = [(digest, item) for digest, item in state["materials"].items() if item["status"] == "available"]
    if not choices:
        raise SystemExit("No available materials remain")
    digest, item = random.Random(args.seed).choice(choices) if args.seed is not None else secrets.choice(choices)
    draw_id = args.draw_id or datetime.now(TIMEZONE).strftime("draw-%Y%m%d-%H%M%S")
    if any(event.get("draw_id") == draw_id for event in state.get("history", [])):
        raise SystemExit(f"Draw ID already exists: {draw_id}")
    item.update(
        {
            "status": "reserved",
            "draw_id": draw_id,
            "platform": args.platform,
            "reserved_at": now(),
            "used_at": None,
        }
    )
    event = {
        "action": "reserve",
        "draw_id": draw_id,
        "platform": args.platform,
        "sha256": digest,
        "material_id": item["id"],
        "at": item["reserved_at"],
    }
    state.setdefault("history", []).append(event)
    state["updated_at"] = now()
    write_json(args.state, state)
    print(json.dumps({"draw_id": draw_id, "sha256": digest, **item}, ensure_ascii=False, indent=2))


def transition(args: argparse.Namespace, action: str) -> None:
    state = load_json(args.state)
    matches = [(digest, item) for digest, item in state["materials"].items() if item.get("draw_id") == args.draw_id]
    if len(matches) != 1:
        raise SystemExit(f"Expected one material for draw ID {args.draw_id}, got {len(matches)}")
    digest, item = matches[0]
    expected = "reserved"
    if item["status"] != expected:
        raise SystemExit(f"Draw {args.draw_id} is {item['status']}, expected {expected}")
    if action == "commit":
        item["status"] = "used"
        item["used_at"] = now()
    else:
        item.update({"status": "available", "draw_id": None, "platform": None, "reserved_at": None, "used_at": None})
    state.setdefault("history", []).append(
        {"action": action, "draw_id": args.draw_id, "sha256": digest, "material_id": item["id"], "at": now()}
    )
    state["updated_at"] = now()
    write_json(args.state, state)
    print(json.dumps({"draw_id": args.draw_id, "sha256": digest, **item}, ensure_ascii=False, indent=2))


def status(args: argparse.Namespace) -> None:
    print_status(load_json(args.state))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.set_defaults(manifest=DEFAULT_MANIFEST, state=DEFAULT_STATE)
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init")
    init_parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    init_parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    init_parser.set_defaults(func=init_state)

    draw_parser = sub.add_parser("draw")
    draw_parser.add_argument("--platform", choices=["instagram", "facebook", "linkedin"], required=True)
    draw_parser.add_argument("--seed", type=int)
    draw_parser.add_argument("--draw-id")
    draw_parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    draw_parser.set_defaults(func=draw)

    for name in ("commit", "release"):
        transition_parser = sub.add_parser(name)
        transition_parser.add_argument("--draw-id", required=True)
        transition_parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
        transition_parser.set_defaults(func=lambda args, action=name: transition(args, action))

    status_parser = sub.add_parser("status")
    status_parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    status_parser.set_defaults(func=status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
