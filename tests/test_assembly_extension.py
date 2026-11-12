from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "extensions" / "simplecadapi-assembly"
BUILDER = ROOT / "tools" / "assembly_skillbuild.py"
EXPECTED = (
    Path("SKILL.md"),
    Path("references/workflow.md"),
    Path("references/assembly-ir.md"),
    Path("references/notebook-composition.md"),
)


def build_hashes(directory: Path) -> dict[str, str] | None:
    if not directory.exists():
        return None
    return {
        file.relative_to(directory).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(directory.rglob("*"))
        if file.is_file()
    }


class AssemblyExtensionTests(unittest.TestCase):
    def test_extension_is_opt_in_and_single_part_route_stays_explicit(self) -> None:
        skill = (SOURCE / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("assembly-only", skill)
        self.assertIn("single solid", skill)
        self.assertIn("unchanged workflow", skill)
        self.assertIn("stepir v6.3", skill)
        self.assertIn("simplecadapi 2.2.7", skill)

    def test_all_referenced_extension_files_exist(self) -> None:
        for relative in EXPECTED:
            self.assertTrue((SOURCE / relative).is_file(), relative.as_posix())
        for relative in EXPECTED:
            text = (SOURCE / relative).read_text(encoding="utf-8")
            for target in __import__("re").findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text):
                self.assertTrue((SOURCE / relative.parent / target).resolve().is_file(), target)

    def test_build_is_isolated_and_has_stable_hash_manifest(self) -> None:
        default_build = ROOT / "builds" / "simplecadapi-assembly-opencode"
        existing_build = build_hashes(default_build)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "simplecadapi-assembly-opencode"
            subprocess.run(
                [sys.executable, str(BUILDER), "--out", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            lines = (output / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), len(EXPECTED))
            for relative in EXPECTED:
                source_hash = hashlib.sha256((SOURCE / relative).read_bytes()).hexdigest()
                self.assertEqual((output / relative).read_bytes(), (SOURCE / relative).read_bytes())
                self.assertIn(f"{source_hash}  {relative.as_posix()}", lines)
            self.assertEqual(build_hashes(default_build), existing_build)

    def test_builder_refuses_to_overwrite_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "existing"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--out", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
