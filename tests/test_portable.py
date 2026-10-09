from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PortablePackageTests(unittest.TestCase):
    def test_public_config_has_no_account(self) -> None:
        config = json.loads((ROOT / "社媒自动化V4/config.v4.json").read_text(encoding="utf-8"))
        self.assertEqual(config["browser"], "safari")
        for platform in ("instagram", "facebook", "linkedin"):
            self.assertEqual(config["platforms"][platform]["expected_account"], "")

    def test_first_catalog_batch_has_twenty_unique_products(self) -> None:
        path = ROOT / "社媒自动化V4/scripts/download_materials.py"
        spec = importlib.util.spec_from_file_location("download_materials", path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        self.assertEqual(len(module.PRODUCT_CATALOG), 20)
        self.assertEqual(len(set(module.PRODUCT_CATALOG)), 20)
        self.assertEqual(len(module.selected_slugs(1, 20)), 20)

    def test_installer_creates_desktop_project_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "setup_teacher.py"),
                    "--desktop-root",
                    temporary,
                    "--skip-download",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            installed = Path(temporary) / "纺织社媒自动化"
            self.assertTrue((installed / ".codex/skills/textile-social-controller-v4/SKILL.md").is_file())
            self.assertTrue((installed / "社媒自动化V4/config.local.json").is_file())
            self.assertTrue((installed / "素材库").is_dir())
            self.assertIn("安装完成", result.stdout)


if __name__ == "__main__":
    unittest.main()

