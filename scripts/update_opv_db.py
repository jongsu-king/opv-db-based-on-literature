#!/usr/bin/env python3
"""Download the latest OPV-DB release, verify it and keep a local copy current.

    python update_opv_db.py                       # CSV package into ./opv-db
    python update_opv_db.py --format sqlite       # one SQLite database instead
    python update_opv_db.py --dest data/opv-db    # another folder
    python update_opv_db.py --check               # exit 10 if a newer release exists

From Python (e.g. at the top of a notebook):

    from update_opv_db import ensure_latest
    folder = ensure_latest("opv-db")              # downloads only when outdated

Standard library only; copy this file into your project. The download is used
only if its SHA-256 equals the value in the release's SHA256SUMS.txt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

REPO = "jongsu-king/opv-db-based-on-literature"
API = f"https://api.github.com/repos/{REPO}/releases/latest"


def _get(url: str, accept: str = "application/octet-stream") -> bytes:
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": "update-opv-db"})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed https URLs
        return resp.read()


def latest() -> dict:
    return json.loads(_get(API, "application/vnd.github+json"))


def installed_version(dest: Path) -> str | None:
    try:
        return (dest / "VERSION").read_text().strip()
    except OSError:
        return None


def ensure_latest(dest: str | Path = "opv-db", fmt: str = "csv", quiet: bool = False) -> Path:
    """Make ``dest`` hold the newest release; return the folder."""
    dest = Path(dest)
    release = latest()
    version = release["tag_name"].lstrip("v")
    if installed_version(dest) == version:
        if not quiet:
            print(f"OPV-DB {version} is up to date in {dest}")
        return dest
    assets = {a["name"]: a["browser_download_url"] for a in release.get("assets", [])}
    name = f"opv-db-{version}-{fmt}.zip"
    if name not in assets or "SHA256SUMS.txt" not in assets:
        raise RuntimeError(f"release {version} has no {name} or SHA256SUMS.txt")
    sums = {}
    for line in _get(assets["SHA256SUMS.txt"]).decode().splitlines():
        parts = line.split()
        if len(parts) == 2:
            sums[parts[1].lstrip("*")] = parts[0].lower()
    payload = _get(assets[name])
    actual = hashlib.sha256(payload).hexdigest()
    if sums.get(name) != actual:
        raise RuntimeError(f"SHA-256 of {name} does not match SHA256SUMS.txt; nothing changed")
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / name
        archive.write_bytes(payload)
        with zipfile.ZipFile(archive) as zf:
            for member in zf.namelist():
                if member.startswith("/") or ".." in Path(member).parts:
                    raise RuntimeError(f"unsafe path in archive: {member}")
            zf.extractall(tmp)
        root = Path(tmp) / f"opv-db-{version}"
        (root / "VERSION").write_text(version + "\n")
        staged = dest.with_name(dest.name + ".new")
        shutil.rmtree(staged, ignore_errors=True)
        shutil.move(str(root), staged)
        shutil.rmtree(dest, ignore_errors=True)
        staged.rename(dest)
    if not quiet:
        print(f"OPV-DB {version} ({fmt}) installed in {dest}; SHA-256 {actual}")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dest", default="opv-db")
    ap.add_argument("--format", choices=("csv", "sqlite"), default="csv")
    ap.add_argument("--check", action="store_true", help="exit 10 if a newer release exists")
    a = ap.parse_args()
    if a.check:
        version = latest()["tag_name"].lstrip("v")
        current = installed_version(Path(a.dest))
        print(f"installed: {current or 'none'}   latest: {version}")
        return 0 if current == version else 10
    ensure_latest(a.dest, a.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
