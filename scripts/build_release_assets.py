#!/usr/bin/env python3
"""Build the downloadable files of a data release (standard library only).

    python scripts/build_release_assets.py --src <tree> --version 1.1.0 --out dist

<tree> is a checkout of the release tag. The script first checks the data and
validation tables against metadata/SHA256SUMS.txt (the checksums frozen with the
data; a mismatch stops the build), then writes

    opv-db-<version>-csv.zip      the release package: data/, validation/, metadata/, docs
    opv-db-<version>-sqlite.zip   the same tables in one SQLite database
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

csv.field_size_limit(sys.maxsize)
PACKAGE = ["README.md", "DATA_DICTIONARY.md", "LICENSE", "CITATION.cff", "THIRD_PARTY_ATTRIBUTION.md",
           "metadata/release_manifest.json", "metadata/SHA256SUMS.txt"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(src: Path) -> list[str]:
    listed = []
    for line in (src / "metadata" / "SHA256SUMS.txt").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.strip().lstrip("*")
        actual = sha256(src / name)
        if actual != digest:
            if name.startswith(("data/", "validation/")):
                sys.exit(f"{name}: SHA-256 {actual} does not match metadata/SHA256SUMS.txt ({digest})")
            # documentation (README, CITATION.cff, ...) was edited after the data were frozen
            print(f"note: {name} differs from the frozen checksum (documentation edited later)", file=sys.stderr)
        listed.append(name)
    return listed


def convert(value: str):
    if value == "":
        return None
    for kind in (int, float):
        try:
            return kind(value)
        except ValueError:
            pass
    return value


def build_sqlite(src: Path, tables: list[str], target: Path, version: str) -> None:
    target.unlink(missing_ok=True)
    db = sqlite3.connect(target)
    for rel in tables:
        name = Path(rel).stem
        with open(src / rel, newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            header = next(reader)
            cols = ", ".join(f'"{c}"' for c in header)
            db.execute(f'CREATE TABLE "{name}" ({cols})')
            marks = ", ".join("?" for _ in header)
            db.executemany(f'INSERT INTO "{name}" VALUES ({marks})',
                           ([convert(v) for v in row] for row in reader))
    db.execute("CREATE TABLE release_info (key TEXT PRIMARY KEY, value TEXT)")
    info = {"version": version, "source": "https://github.com/jongsu-king/opv-db-based-on-literature",
            "doi_concept": "10.5281/zenodo.23682463", "license": "CC BY 4.0 (derivative of OPV-DB, Qiu)",
            "csv_sha256": json.dumps({rel: sha256(src / rel) for rel in tables})}
    db.executemany("INSERT INTO release_info VALUES (?, ?)", info.items())
    db.commit()
    db.execute("VACUUM")
    db.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    listed = verify(a.src)
    a.out.mkdir(parents=True, exist_ok=True)
    root = f"opv-db-{a.version}"
    files = sorted(set(listed) | {p for p in PACKAGE if (a.src / p).exists()})
    with zipfile.ZipFile(a.out / f"{root}-csv.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel in files:
            zf.write(a.src / rel, f"{root}/{rel}")
    tables = [p for p in listed if p.endswith(".csv")]
    db = a.out / f"{root}.sqlite"
    build_sqlite(a.src, tables, db, a.version)
    with zipfile.ZipFile(a.out / f"{root}-sqlite.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(db, f"{root}/{db.name}")
        for rel in ("README.md", "DATA_DICTIONARY.md", "LICENSE", "CITATION.cff", "THIRD_PARTY_ATTRIBUTION.md"):
            if (a.src / rel).exists():
                zf.write(a.src / rel, f"{root}/{rel}")
    db.unlink()
    for p in sorted(a.out.iterdir()):
        print(f"{p.name}  {p.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
