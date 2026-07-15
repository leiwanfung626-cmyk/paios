"""
Smoke tests for PAIOS automation scripts.

These tests verify that scripts parse correctly and can be imported
(or at least that their syntax is valid). They do not execute real
workflows — run these after any script change.
"""

import ast
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "05_SCRIPTS"
SCRIPT_GLOB = "*.py"


def test_all_scripts_parse():
    """Every .py script in 05_SCRIPTS/ must be syntactically valid."""
    failures = []
    for pyfile in sorted(SCRIPTS_DIR.glob(SCRIPT_GLOB)):
        try:
            with open(pyfile, encoding="utf-8") as f:
                ast.parse(f.read(), filename=str(pyfile))
        except SyntaxError as e:
            failures.append(f"{pyfile.name}: {e}")

    assert not failures, "\n".join(failures)


def test_all_scripts_have_shebang():
    """Every executable script should have a shebang."""
    for pyfile in sorted(SCRIPTS_DIR.glob(SCRIPT_GLOB)):
        content = pyfile.read_text(encoding="utf-8")
        assert content.startswith("#!/usr/bin/env python3"), (
            f"{pyfile.name} missing shebang"
        )


def test_collect_manifest_dry_run():
    """
    Very basic smoke: ensure collect_manifest can handle --help
    without crashing (does not run against real workspace).
    """
    import subprocess
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "collect_manifest.py"), "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower() or "用法" in result.stdout
