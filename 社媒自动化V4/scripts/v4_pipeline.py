#!/usr/bin/env python3
"""Prepare and validate platform-isolated V4 textile content packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
V4 = ROOT / "社媒自动化V4"
CONFIG = V4 / "config.v4.json"
LOCAL_CONFIG = V4 / "config.local.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def merge_dict(base: dict, override: dict) -> dict:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config() -> dict:
    config = load_json(CONFIG)
    if LOCAL_CONFIG.is_file():
        config = merge_dict(config, load_json(LOCAL_CONFIG))
    return config


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve()))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n"):
            return struct.unpack(">II", header[16:24])
        if header[:2] == b"\xff\xd8":
            handle.seek(2)
            while True:
                marker = handle.read(1)
                if not marker:
                    break
                if marker != b"\xff":
                    continue
                code = handle.read(1)
                while code == b"\xff":
                    code = handle.read(1)
                if code in {bytes([c]) for c in range(0xC0, 0xC4)} | {bytes([c]) for c in range(0xC5, 0xC8)} | {bytes([c]) for c in range(0xC9, 0xCC)} | {bytes([c]) for c in range(0xCD, 0xD0)}:
                    handle.read(3)
                    height, width = struct.unpack(">HH", handle.read(4))
                    return width, height
                length_raw = handle.read(2)
                if len(length_raw) != 2:
                    break
                length = struct.unpack(">H", length_raw)[0]
                handle.seek(max(0, length - 2), 1)
    raise ValueError(f"Unsupported image format: {path}")


def prepare(args):
    config = load_config()
    source = (ROOT / args.source).resolve()
    if not source.is_file() or ROOT.resolve() not in source.parents:
        raise SystemExit(f"Invalid source: {source}")
    sidecar = source.with_suffix(".txt")
    if not sidecar.is_file():
        raise SystemExit(f"Missing sidecar: {sidecar}")
    run_id = args.run_id or datetime.now(ZoneInfo(config["timezone"])).strftime("%Y%m%d-%H%M%S")
    platforms = list(config["platforms"]) if args.platform == "all" else [args.platform]
    now = datetime.now(ZoneInfo(config["timezone"])).isoformat()
    for platform in platforms:
        spec = config["platforms"][platform]
        out = ROOT / config["output_root"] / run_id / platform
        out.mkdir(parents=True, exist_ok=True)
        manifest = {
            "run_id": run_id,
            "platform": platform,
            "source_path": rel(source),
            "source_sha256": sha256(source),
            "sidecar_path": rel(sidecar),
            "facts": sidecar.read_text(encoding="utf-8").splitlines(),
            "created_at": now,
            "status": "draft"
        }
        write_json(out / "source-manifest.json", manifest)
        brief = {
            "platform": platform,
            "objective": "acquisition, qualified traffic, and conversion conversations",
            "audience": "TO_BE_COMPLETED_BY_STRATEGY_BRANCH",
            "canvas": {"width": spec["width"], "height": spec["height"], "aspect_ratio": spec["aspect_ratio"]},
            "research_reviewed_at": config["research_reviewed_at"],
            "sample_observations": [],
            "visual_direction": "TO_BE_COMPLETED_BY_STRATEGY_BRANCH",
            "caption_direction": "TO_BE_COMPLETED_BY_STRATEGY_BRANCH",
            "generation_prompts": {"human_context": "", "product_closeup": ""},
            "disclosure": "Concept visualization created from the supplied material reference."
        }
        write_json(out / "creative-brief.json", brief)
        print(out)


def validate(args):
    config = load_config()
    package = (ROOT / args.package).resolve()
    platform = args.platform
    spec = config["platforms"][platform]
    errors = []
    core_required = ["source-manifest.json", "creative-brief.json", "caption.txt", "usage.json"]
    for name in core_required:
        if not (package / name).is_file():
            errors.append(f"missing:{name}")
    if not errors:
        manifest = load_json(package / "source-manifest.json")
        brief = load_json(package / "creative-brief.json")
        usage = load_json(package / "usage.json")
        asset_mode = usage.get("asset_mode", "concept_carousel")
        if asset_mode == "real_product_single":
            media_required = ["product-original.jpg"]
        elif asset_mode == "concept_single":
            media_required = ["product-concept.png"]
        elif asset_mode == "concept_carousel":
            media_required = ["human-context.png", "product-closeup.png"]
        else:
            media_required = []
            errors.append(f"unknown_asset_mode:{asset_mode}")
        for name in media_required:
            if not (package / name).is_file():
                errors.append(f"missing:{name}")
        caption = (package / "caption.txt").read_text(encoding="utf-8").strip()
        if manifest.get("platform") != platform or brief.get("platform") != platform or usage.get("platform") != platform:
            errors.append("platform_mismatch")
        if usage.get("post_generation_crop") is not False:
            errors.append("post_generation_crop_must_be_false")
        if usage.get("source_sha256") != manifest.get("source_sha256"):
            errors.append("source_hash_mismatch")
        if "TO_BE_COMPLETED" in json.dumps(brief):
            errors.append("creative_brief_incomplete")
        if asset_mode == "concept_carousel" and not all(brief.get("generation_prompts", {}).values()):
            errors.append("generation_prompts_incomplete")
        if not brief.get("sample_observations"):
            errors.append("sample_observations_missing")
        if len(caption) > spec["caption_max_chars"]:
            errors.append("caption_too_long")
        if caption.count("#") > spec["hashtag_max"]:
            errors.append("too_many_hashtags")
        seen = {}
        for item in usage.get("images", []):
            seen[item.get("role")] = item
        if asset_mode == "real_product_single":
            item = seen.get("real_product")
            filename = "product-original.jpg"
            if usage.get("ai_generated") is not False:
                errors.append("real_product_must_not_be_ai_generated")
            if len(seen) != 1 or not item or Path(item.get("path", "")).name != filename:
                errors.append("exactly_one_real_product_image_required")
            elif (package / filename).is_file():
                width, height = image_size(package / filename)
                if (item.get("width"), item.get("height")) != (width, height):
                    errors.append(f"usage_dimension_mismatch:{filename}")
                output_hash = sha256(package / filename)
                if output_hash != manifest.get("source_sha256") or item.get("output_sha256") != output_hash:
                    errors.append("real_product_source_hash_mismatch")
        elif asset_mode == "concept_single":
            item = seen.get("product_concept")
            filename = "product-concept.png"
            if usage.get("ai_generated") is not True:
                errors.append("concept_single_must_be_ai_generated")
            if len(seen) != 1 or not item or Path(item.get("path", "")).name != filename:
                errors.append("exactly_one_product_concept_required")
            elif (package / filename).is_file():
                width, height = image_size(package / filename)
                if (width, height) != (spec["width"], spec["height"]):
                    errors.append(f"wrong_dimensions:{filename}:{width}x{height}")
                if (item.get("width"), item.get("height")) != (width, height):
                    errors.append(f"usage_dimension_mismatch:{filename}")
                output_hash = sha256(package / filename)
                if item.get("output_sha256") != output_hash:
                    errors.append("concept_output_hash_mismatch")
        elif asset_mode == "concept_carousel":
            expected = {"human_context": "human-context.png", "product_closeup": "product-closeup.png"}
            for role, filename in expected.items():
                item = seen.get(role)
                if not item or Path(item.get("path", "")).name != filename:
                    errors.append(f"usage_missing_role:{role}")
                    continue
                width, height = image_size(package / filename)
                if (width, height) != (spec["width"], spec["height"]):
                    errors.append(f"wrong_dimensions:{filename}:{width}x{height}")
                if (item.get("width"), item.get("height")) != (width, height):
                    errors.append(f"usage_dimension_mismatch:{filename}")
                if not item.get("angle_description"):
                    errors.append(f"angle_missing:{role}")
            if len(seen) != 2:
                errors.append("exactly_two_images_required")
            descriptions = [seen.get(role, {}).get("angle_description") for role in expected]
            if len(set(descriptions)) != 2:
                errors.append("angles_must_differ")
    result = {
        "platform": platform,
        "package": rel(package),
        "validated_at": datetime.now(ZoneInfo(config["timezone"])).isoformat(),
        "status": "passed" if not errors else "failed",
        "errors": errors
    }
    write_json(package / "validation.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


def stage(args):
    config = load_config()
    package = (ROOT / args.package).resolve()
    platform = args.platform
    if not package.is_dir() or ROOT.resolve() not in package.parents:
        raise SystemExit(f"Invalid package: {package}")

    validation_path = package / "validation.json"
    if not validation_path.is_file():
        raise SystemExit("Package has no validation.json")
    validation = load_json(validation_path)
    if validation.get("platform") != platform or validation.get("status") != "passed" or validation.get("errors"):
        raise SystemExit("Package validation is not a clean pass for the selected platform")

    manifest = load_json(package / "source-manifest.json")
    usage = load_json(package / "usage.json")
    if manifest.get("platform") != platform or usage.get("platform") != platform:
        raise SystemExit("Package platform mismatch")
    run_id = manifest.get("run_id")
    if not run_id:
        raise SystemExit("source-manifest.json has no run_id")

    asset_mode = usage.get("asset_mode", "concept_carousel")
    if asset_mode == "real_product_single":
        ordered = ["product-original.jpg"]
    elif asset_mode == "concept_single":
        ordered = ["product-concept.png"]
    elif asset_mode == "concept_carousel":
        ordered = ["human-context.png", "product-closeup.png"]
    else:
        raise SystemExit(f"Unknown asset mode: {asset_mode}")
    supporting = ["caption.txt", "source-manifest.json", "creative-brief.json", "usage.json", "validation.json"]
    required = ordered + supporting
    for name in required:
        if not (package / name).is_file():
            raise SystemExit(f"Missing staged file: {name}")

    ready_root = ROOT / config["publish_ready_root"] / platform / run_id
    if ready_root.exists() and any(ready_root.iterdir()):
        raise SystemExit(f"Publish-ready package already exists: {ready_root}")
    ready_root.mkdir(parents=True, exist_ok=True)

    files = []
    for position, name in enumerate(required, start=1):
        source = package / name
        target = ready_root / name
        shutil.copy2(source, target)
        item = {"name": name, "sha256": sha256(target)}
        if name in ordered:
            item["media_position"] = ordered.index(name) + 1
        files.append(item)

    ready = {
        "schema_version": 1,
        "status": "ready",
        "platform": platform,
        "run_id": run_id,
        "asset_mode": asset_mode,
        "ai_generated": usage.get("ai_generated", asset_mode in {"concept_single", "concept_carousel"}),
        "expected_account": config["platforms"][platform].get("expected_account"),
        "source_package": rel(package),
        "staged_at": datetime.now(ZoneInfo(config["timezone"])).isoformat(),
        "media_order": ordered,
        "carousel_order": ordered if len(ordered) > 1 else None,
        "caption_file": "caption.txt",
        "files": files
    }
    write_json(ready_root / "publish-ready.json", ready)
    print(json.dumps({"status": "ready", "path": rel(ready_root), "run_id": run_id}, ensure_ascii=False, indent=2))


def verify_ready(args):
    config = load_config()
    ready_root = (ROOT / args.ready_dir).resolve()
    if not ready_root.is_dir() or ROOT.resolve() not in ready_root.parents:
        raise SystemExit(f"Invalid publish-ready directory: {ready_root}")
    ready_path = ready_root / "publish-ready.json"
    if not ready_path.is_file():
        raise SystemExit("Missing publish-ready.json")
    ready = load_json(ready_path)
    platform = ready.get("platform")
    errors = []
    if platform not in config["platforms"]:
        errors.append("unknown_platform")
    if ready.get("status") != "ready":
        errors.append("not_ready")
    asset_mode = ready.get("asset_mode", "concept_carousel")
    media_order = ready.get("media_order") or ready.get("carousel_order")
    if asset_mode == "real_product_single":
        expected_order = ["product-original.jpg"]
        if ready.get("ai_generated") is not False:
            errors.append("real_product_must_not_be_ai_generated")
    elif asset_mode == "concept_single":
        expected_order = ["product-concept.png"]
        if ready.get("ai_generated") is not True:
            errors.append("concept_single_must_be_ai_generated")
    elif asset_mode == "concept_carousel":
        expected_order = ["human-context.png", "product-closeup.png"]
    else:
        expected_order = []
        errors.append(f"unknown_asset_mode:{asset_mode}")
    if media_order != expected_order:
        errors.append("wrong_media_order")
    for item in ready.get("files", []):
        path = ready_root / item.get("name", "")
        if not path.is_file():
            errors.append(f"missing:{item.get('name')}")
        elif sha256(path) != item.get("sha256"):
            errors.append(f"hash_mismatch:{item.get('name')}")
    if platform in config["platforms"]:
        spec = config["platforms"][platform]
        for name in expected_order:
            path = ready_root / name
            if path.is_file():
                width, height = image_size(path)
                if asset_mode in {"concept_single", "concept_carousel"} and (width, height) != (spec["width"], spec["height"]):
                    errors.append(f"wrong_dimensions:{name}:{width}x{height}")
        if asset_mode == "real_product_single":
            source_manifest = ready_root / "source-manifest.json"
            product = ready_root / "product-original.jpg"
            if source_manifest.is_file() and product.is_file():
                manifest = load_json(source_manifest)
                if sha256(product) != manifest.get("source_sha256"):
                    errors.append("real_product_source_hash_mismatch")
        caption = ready_root / "caption.txt"
        if caption.is_file():
            text = caption.read_text(encoding="utf-8").strip()
            if len(text) > spec["caption_max_chars"]:
                errors.append("caption_too_long")
            if text.count("#") > spec["hashtag_max"]:
                errors.append("too_many_hashtags")
    result = {
        "status": "passed" if not errors else "failed",
        "ready_dir": rel(ready_root),
        "platform": platform,
        "errors": errors
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--source", required=True)
    prep.add_argument("--platform", choices=["all", "instagram", "facebook", "linkedin"], default="all")
    prep.add_argument("--run-id")
    prep.set_defaults(func=prepare)
    check = sub.add_parser("validate")
    check.add_argument("--package", required=True)
    check.add_argument("--platform", choices=["instagram", "facebook", "linkedin"], required=True)
    check.set_defaults(func=validate)
    staged = sub.add_parser("stage")
    staged.add_argument("--package", required=True)
    staged.add_argument("--platform", choices=["instagram", "facebook", "linkedin"], required=True)
    staged.set_defaults(func=stage)
    ready = sub.add_parser("verify-ready")
    ready.add_argument("--ready-dir", required=True)
    ready.set_defaults(func=verify_ready)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
