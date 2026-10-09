#!/usr/bin/env python3
"""Install the portable project on the Desktop and fetch the first material batch."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent
PROJECT_NAME = "纺织社媒自动化"
SKIP_NAMES = {".git", ".DS_Store", "__pycache__"}
RUNTIME_DIRS = {
    Path("素材库"),
    Path("社媒自动化V4/outputs"),
    Path("社媒自动化V4/publish-ready"),
    Path("社媒自动化V4/state"),
}


def should_skip(relative: Path) -> bool:
    if any(part in SKIP_NAMES for part in relative.parts):
        return True
    return any(relative == runtime or runtime in relative.parents for runtime in RUNTIME_DIRS)


def copy_project(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for source in SOURCE_ROOT.rglob("*"):
        relative = source.relative_to(SOURCE_ROOT)
        if should_skip(relative):
            continue
        destination = target / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    for runtime in RUNTIME_DIRS:
        (target / runtime).mkdir(parents=True, exist_ok=True)


def ensure_local_config(target: Path) -> Path:
    local = target / "社媒自动化V4" / "config.local.json"
    if local.exists():
        return local
    example = target / "社媒自动化V4" / "config.local.example.json"
    shutil.copy2(example, local)
    return local


def write_install_record(target: Path, local_config: Path, skipped_download: bool) -> None:
    record = {
        "project_name": PROJECT_NAME,
        "installed_path": str(target),
        "local_config": str(local_config),
        "material_batch": None if skipped_download else 1,
        "material_batch_size": None if skipped_download else 20,
    }
    (target / ".teacher-install.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desktop-root", type=Path, default=Path.home() / "Desktop")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    target = args.desktop_root.expanduser().resolve() / PROJECT_NAME
    if target == SOURCE_ROOT:
        target.mkdir(parents=True, exist_ok=True)
    else:
        copy_project(target)
    local_config = ensure_local_config(target)

    if not args.skip_download:
        downloader = target / "社媒自动化V4" / "scripts" / "download_materials.py"
        subprocess.run(
            [sys.executable, str(downloader), "--batch", "1", "--batch-size", "20"],
            cwd=target,
            check=True,
        )

    write_install_record(target, local_config, args.skip_download)
    print("\n安装完成")
    print(f"项目目录: {target}")
    print(f"本机配置: {local_config}")
    if args.skip_download:
        print("素材下载: 已跳过")
    else:
        print(f"素材目录: {target / '素材库' / '第01批-20个'}")
    print("下一步: 用 Codex 打开项目目录，并在 Safari 登录三个平台。")


if __name__ == "__main__":
    main()

