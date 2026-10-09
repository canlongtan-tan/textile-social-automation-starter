#!/usr/bin/env python3
"""Download one verified batch of official Hysure fabric sample images."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import mimetypes
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
TIMEZONE = ZoneInfo("Asia/Shanghai")
BASE = "https://www.hysuretextile.com/product/"
SOURCE_SITE = "https://www.hysuretextile.com/"
SOURCE_CATEGORY = "https://www.hysuretextile.com/product-category/fabric-sample/"

# The first reviewed batch. Add later reviewed product slugs here; --batch slices
# the catalogue in groups of --batch-size without changing existing batches.
PRODUCT_CATALOG = [
    "bathrobe-fleece",
    "brushed-pattern-plush",
    "coral-fleece",
    "danish-mink-mink-and-european-mink-including-angora-style-mink-mink-blend-knitwear",
    "european-mink-fleece",
    "faux-fox-fur",
    "flannel",
    "fluffy-plush-double-sided-jacquard",
    "fluorescent-double-brushed-single-sided-fleece",
    "granular-fleece",
    "mi-diao-fleece",
    "peacock-fleece",
    "pearl-fleece",
    "pineapple-embossed-plush",
    "sherpa-fleece",
    "single-sided-cotton-fleece-weft-knitted-fabric",
    "striped-plush",
    "supersoft-fleece",
    "toscana-faux-fur",
    "turtle-fleece",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str) -> tuple[bytes, str]:
    parts = urllib.parse.urlsplit(url)
    safe_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, urllib.parse.quote(parts.path), parts.query, parts.fragment)
    )
    request = urllib.request.Request(
        safe_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; TextileSocialStarter/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read(), response.headers.get_content_type()


def text_only(value: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())


def parse_product_page(page: bytes, page_url: str) -> tuple[str, str]:
    source = page.decode("utf-8", errors="replace")
    title = re.search(r"<h1\b[^>]*>(.*?)</h1>", source, re.IGNORECASE | re.DOTALL)
    image = re.search(
        r'<img\b[^>]*\bid=["\']mainImg["\'][^>]*\bsrc=["\']([^"\']+)["\']',
        source,
        re.IGNORECASE,
    )
    if not title or not image:
        raise RuntimeError(f"官网页面缺少产品标题或主图: {page_url}")
    return text_only(title.group(1)), html.unescape(image.group(1))


def extension_for(image_url: str, content_type: str) -> str:
    suffix = Path(urllib.parse.urlsplit(image_url).path).suffix.lower()
    if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension(content_type) or ".bin"
    return ".jpg" if guessed == ".jpe" else guessed


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def selected_slugs(batch: int, batch_size: int) -> list[str]:
    if batch < 1 or batch_size < 1:
        raise SystemExit("batch 和 batch-size 必须大于 0")
    start = (batch - 1) * batch_size
    result = PRODUCT_CATALOG[start : start + batch_size]
    if len(result) != batch_size:
        available = (len(PRODUCT_CATALOG) + batch_size - 1) // batch_size
        raise SystemExit(f"当前已审核产品目录只支持 {available} 批；第 {batch} 批尚未配置")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--target-root", type=Path, default=ROOT / "素材库")
    args = parser.parse_args()

    slugs = selected_slugs(args.batch, args.batch_size)
    target = args.target_root.expanduser().resolve() / f"第{args.batch:02d}批-{args.batch_size}个"
    target.mkdir(parents=True, exist_ok=True)
    manifest_path = target / "manifest.json"
    downloaded_at = datetime.now(TIMEZONE).isoformat()
    items: list[dict[str, object]] = []
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()

    for position, slug in enumerate(slugs, start=1):
        page_url = f"{BASE}{slug}/"
        page, _ = fetch(page_url)
        product, image_url = parse_product_page(page, page_url)
        image, content_type = fetch(image_url)
        digest = sha256_bytes(image)
        if page_url in seen_urls or digest in seen_hashes:
            raise RuntimeError(f"本批次发现重复素材: {page_url}")
        seen_urls.add(page_url)
        seen_hashes.add(digest)

        suffix = extension_for(image_url, content_type)
        material_id = f"{position:02d}"
        image_path = target / f"{material_id}-{slug}{suffix}"
        sidecar_path = target / f"{material_id}-{slug}.txt"
        if image_path.exists():
            if sha256_file(image_path) != digest:
                raise RuntimeError(f"已有文件与官网内容不一致，停止覆盖: {image_path}")
            action = "verified"
        else:
            temporary = image_path.with_suffix(image_path.suffix + ".part")
            temporary.write_bytes(image)
            if sha256_file(temporary) != digest:
                temporary.unlink(missing_ok=True)
                raise RuntimeError(f"下载校验失败: {page_url}")
            temporary.replace(image_path)
            action = "downloaded"

        sidecar_path.write_text(
            "\n".join(
                [
                    f"Product: {product}",
                    f"Source: {page_url}",
                    f"Official image: {image_url}",
                    "Source category: Fabric Sample",
                    f"Checked: {downloaded_at}",
                    f"Content SHA-256: {digest}",
                    "Asset note: Official source image downloaded without image editing.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        try:
            source_path = str(image_path.relative_to(ROOT))
            sidecar_relative = str(sidecar_path.relative_to(ROOT))
        except ValueError:
            source_path = str(image_path)
            sidecar_relative = str(sidecar_path)
        items.append(
            {
                "id": material_id,
                "product": product,
                "slug": slug,
                "source_url": page_url,
                "image_url": image_url,
                "source_path": source_path,
                "sidecar_path": sidecar_relative,
                "sha256": digest,
                "bytes": len(image),
                "content_type": content_type,
            }
        )
        print(f"{material_id} {action}: {image_path.name}")

    write_json(
        manifest_path,
        {
            "schema_version": 1,
            "source_site": SOURCE_SITE,
            "source_category": SOURCE_CATEGORY,
            "batch": args.batch,
            "batch_size": args.batch_size,
            "checked_at": downloaded_at,
            "selection_rule": "Reviewed named Fabric Sample products; one official hero image per product.",
            "count": len(items),
            "items": items,
        },
    )
    print(f"manifest: {manifest_path}")
    print(f"完成: {len(items)} 个唯一素材")


if __name__ == "__main__":
    main()

