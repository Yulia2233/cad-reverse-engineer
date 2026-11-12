#!/usr/bin/env python3
"""Build the isolated SimpleCADAPI assembly skill extension."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "extensions" / "simplecadapi-assembly"
FILES = (
    Path("SKILL.md"),
    Path("references/workflow.md"),
    Path("references/assembly-ir.md"),
    Path("references/notebook-composition.md"),
)


def validate_source() -> dict[Path, str]:
    hashes = {}
    for relative in FILES:
        source = SOURCE / relative
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Missing or unsafe extension file: {source}")
        data = source.read_bytes()
        text = data.decode("utf-8")
        hashes[relative] = hashlib.sha256(data).hexdigest()
        if "{{" in text or "}}" in text:
            raise ValueError(f"Unresolved template marker in {relative}")
    skill = (SOURCE / "SKILL.md").read_text(encoding="utf-8")
    for required in (
        "name: simplecadapi-assembly",
        "sdk-version: 2.2.7",
        "stepir-version: v6.3",
        "single-part workflow",
        "source placement",
    ):
        if required not in skill.lower():
            raise ValueError(f"Assembly skill is missing required text: {required}")
    return hashes


def render_manifest(hashes: dict[Path, str]) -> str:
    return "".join(f"{digest}  {relative.as_posix()}\n" for relative, digest in sorted(hashes.items()))


def build(output: Path, hashes: dict[Path, str]) -> None:
    output = output.expanduser().absolute()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing build directory: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.parent.is_symlink():
        raise ValueError(f"Refusing symlinked build parent: {output.parent}")
    output.mkdir()
    try:
        for relative in FILES:
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / relative, target)
        (output / "MANIFEST.sha256").write_text(render_manifest(hashes), encoding="utf-8")
    except BaseException:
        shutil.rmtree(output)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate source files without building")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "builds" / "simplecadapi-assembly-opencode",
        help="new isolated assembly build directory",
    )
    args = parser.parse_args()
    hashes = validate_source()
    if args.check:
        print(f"Validated {len(hashes)} assembly extension files")
        return 0
    build(args.out, hashes)
    print(f"Built assembly extension: {args.out.expanduser().absolute()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
