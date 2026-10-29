#!/usr/bin/env python3
"""Build a clean .ankiaddon package from this repository's add-on source."""

import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "addon"
REQUIRED = (
    "__init__.py",
    "bridge.py",
    "judge0.py",
    "config.json",
    "config.md",
    "manifest.json",
    "README.md",
)


def main():

    manifest = json.loads((ADDON / "manifest.json").read_text(encoding="utf-8"))
    config = json.loads((ADDON / "config.json").read_text(encoding="utf-8"))

    if not manifest.get("package") or not manifest.get("name"):
        raise SystemExit("manifest.json must include package and name")
    if config.get("judge0_api_key"):
        raise SystemExit("Refusing to package a non-empty Judge0 API key")
    match = re.search(r'^VERSION\s*=\s*["\']([^"\']+)', (ADDON / "bridge.py").read_text(encoding="utf-8"), re.M)
    if not match:
        raise SystemExit("Could not determine the add-on version")

    output_dir = ROOT / "dist"
    output_dir.mkdir(exist_ok=True)
    output = output_dir / f"CodingPracticeJudge-{match.group(1)}.ankiaddon"

    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for name in REQUIRED:
            path = ADDON / name
            if not path.is_file():
                raise SystemExit(f"Required package file is missing: {path}")
            archive.write(path, name)
        license_file = ROOT / "LICENSE"
        if not license_file.is_file():
            raise SystemExit("Project LICENSE is missing")
        archive.write(license_file, "LICENSE")

    with ZipFile(output) as archive:
        names = archive.namelist()
        if any("/" in name or "__pycache__" in name or name.endswith(".pyc") for name in names):
            output.unlink()
            raise SystemExit("Package contains a nested path or Python cache file")
    print(f"Built {output}")


if __name__ == "__main__":
    main()
