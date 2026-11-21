#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Writes the invented passport spread for the Republic of Krzvania — a desert
caravan-route republic — to /output/entry.png (1024x1024).

Holder: Amina Rashid, licensed caravan guide, licence C-0917. Every date is
internally consistent: issued 12 FEB 2024, every stamp after issue, expiry
11 FEB 2034 (issue + 10 years), MRZ check digits per ICAO 9303, stamps paired
arrival/departure on matching dates, visa valid 01-30 SEP 2025 covering the
09-27 SEP 2025 Mirazh trip.

The spread is rendered at build time and bundled as entry.png beside this
file; this program copies it to the output directory using only the Python
standard library, so it runs in any stock python:3.13 sandbox with no extra
packages, no fonts and no network.
"""

import hashlib
import os
import shutil
from pathlib import Path

IMAGE_NAME = "entry.png"
BASE_DIR = Path(__file__).resolve().parent
SRC = BASE_DIR / IMAGE_NAME
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    destination = OUT_DIR / IMAGE_NAME
    shutil.copyfile(SRC, destination)
    if not destination.exists():
        raise ValueError("Destination does not exist")
    size = destination.stat().st_size
    if size != SRC.stat().st_size:
        raise ValueError("Destination size differs from source")
    with SRC.open("rb") as source_file:
        source_sha256 = hashlib.file_digest(source_file, "sha256").hexdigest()
    with destination.open("rb") as destination_file:
        sha256 = hashlib.file_digest(destination_file, "sha256").hexdigest()
    if sha256 != source_sha256:
        raise ValueError("Destination SHA-256 differs from source")
    return destination, size, sha256


if __name__ == "__main__":
    destination, size, sha256 = main()
    print(f"{destination.name}: {size} bytes, SHA-256 {sha256}")
