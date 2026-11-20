#!/usr/bin/env python3
"""Entrypoint for make.fun's news-image-20261120 bounty.

The page was drawn at build time by tools/render.py and committed beside this
file as entry.png. The grader runs this program twice in a container with no
network, a read-only repository and a writable output directory, and requires
both runs to write the same bytes, so this program does one thing only: copy
the committed image to entry.png in the directory it is given.

    MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "entry.png"


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PAGE, out_dir / "entry.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
