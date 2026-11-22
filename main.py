#!/usr/bin/env python3
"""Golden Honey, Dripping — make.fun entry.

Writes one picture of a single ingredient — golden honeycomb dripping
with honey — to /output/entry.png.

The picture itself ships as asset.jpg next to this script (a JPEG,
1024x1024, well under the 1 MiB cap). This program, using only the
Python 3.13 standard library and no network, validates the asset and
copies it to the required output path.
"""

import hashlib
import os
import sys

ASSET_NAME = "asset.jpg"
OUTPUT_PATH = "/output/entry.png"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024


def asset_path():
    """Locate the bundled picture next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, ASSET_NAME)


def read_jpeg_dimensions(data):
    """Parse width/height out of a JPEG's SOF marker (stdlib only)."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("asset is not a JPEG (missing SOI marker)")
    pos = 2
    while pos + 9 < len(data):
        if data[pos] != 0xFF:
            raise ValueError("corrupt JPEG marker stream")
        marker = data[pos + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[pos + 5:pos + 7], "big")
            width = int.from_bytes(data[pos + 7:pos + 9], "big")
            return width, height
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            pos += 2
            continue
        size = int.from_bytes(data[pos + 2:pos + 4], "big")
        pos += 2 + size
    raise ValueError("no JPEG start-of-frame marker found")


def main():
    path = asset_path()
    with open(path, "rb") as handle:
        data = handle.read()
    if len(data) > MAX_BYTES:
        raise ValueError(
            "asset is %d bytes, over the %d byte cap" % (len(data), MAX_BYTES)
        )
    width, height = read_jpeg_dimensions(data)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            "asset is %dx%d, over the %d px cap"
            % (width, height, MAX_DIMENSION)
        )
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as handle:
        handle.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (OUTPUT_PATH, width, height, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
