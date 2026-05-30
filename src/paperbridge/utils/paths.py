from __future__ import annotations

import shutil
from pathlib import Path


def prepare_output_dir(out_dir: Path, force: bool = False) -> None:
    out_dir = out_dir.resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        if not force:
            raise FileExistsError(f"Output directory is not empty: {out_dir}")
        if out_dir.anchor == str(out_dir) or len(out_dir.parts) < 3:
            raise ValueError(f"Refusing to remove unsafe output directory: {out_dir}")
        shutil.rmtree(out_dir)

    (out_dir / "assets" / "pages").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "figures").mkdir(parents=True, exist_ok=True)
    (out_dir / "assets" / "tables").mkdir(parents=True, exist_ok=True)
    (out_dir / "debug").mkdir(parents=True, exist_ok=True)


def relative_to_output(path: Path, out_dir: Path) -> str:
    return path.resolve().relative_to(out_dir.resolve()).as_posix()

