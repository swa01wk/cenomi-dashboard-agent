"""DEF-0007 — make setup generates SESSION_SECRET (DEVENV §4)."""

from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKE_DIR = REPO_ROOT / "scripts" / "make"
_ENV_SECRET = re.compile(r"^SESSION_SECRET=(.+)$", re.MULTILINE)


def _load_invoke():
    spec = importlib.util.spec_from_file_location("make_invoke", MAKE_DIR / "invoke.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _read_session_secret(env_path: Path) -> str | None:
    if not env_path.is_file():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        match = _ENV_SECRET.match(line.strip())
        if match:
            return match.group(1).strip()
    return None


def test_ensure_session_secret_fills_empty_line(tmp_path: Path) -> None:
    invoke = _load_invoke()
    env_path = tmp_path / ".env"
    env_path.write_text(
        "CENOMI_ENV=dev\nSESSION_SECRET=\nAPI_INTERNAL_URL=http://localhost:8000\n",
        encoding="utf-8",
    )
    invoke.ensure_session_secret_in_dotenv(env_path)
    secret = _read_session_secret(env_path)
    assert secret is not None
    assert len(secret) >= 64
    assert secret.isascii()
    assert all(ch.isalnum() or ch in "-_" for ch in secret)
    text = env_path.read_text(encoding="utf-8")
    assert text.startswith("CENOMI_ENV=dev\n")
    assert "API_INTERNAL_URL=http://localhost:8000" in text


def test_ensure_session_secret_preserves_existing_value(tmp_path: Path) -> None:
    invoke = _load_invoke()
    env_path = tmp_path / ".env"
    existing = "existing-dev-secret-value-thirty-two-bytes!!"
    env_path.write_text(f"SESSION_SECRET={existing}\n", encoding="utf-8")
    invoke.ensure_session_secret_in_dotenv(env_path)
    assert _read_session_secret(env_path) == existing


@pytest.mark.skipif(shutil.which("make") is None, reason="make not available")
def test_make_setup_generates_session_secret_when_copied_from_example() -> None:
    env_path = REPO_ROOT / ".env"
    example = REPO_ROOT / ".env.example"
    backup: Path | None = None
    if env_path.is_file():
        backup = REPO_ROOT / ".env.def0007.bak"
        shutil.copyfile(env_path, backup)
        env_path.unlink()
    try:
        assert example.is_file()
        completed = subprocess.run(
            ["make", "setup", "BROWSERS=0"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        secret = _read_session_secret(env_path)
        assert secret is not None
        assert len(secret) >= 64
        assert secret not in (completed.stdout + completed.stderr)
    finally:
        if env_path.is_file():
            env_path.unlink()
        if backup is not None and backup.is_file():
            shutil.move(backup, env_path)


def test_make_setup_does_not_overwrite_existing_session_secret() -> None:
    env_path = REPO_ROOT / ".env"
    example = REPO_ROOT / ".env.example"
    backup: Path | None = None
    if env_path.is_file():
        backup = REPO_ROOT / ".env.def0007.bak"
        shutil.copyfile(env_path, backup)
    preserved = "preserved-session-secret-for-def0007-test-value!!"
    try:
        shutil.copyfile(example, env_path)
        env_path.write_text(
            env_path.read_text(encoding="utf-8").replace(
                "SESSION_SECRET=",
                f"SESSION_SECRET={preserved}",
                1,
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            ["make", "setup", "BROWSERS=0"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert _read_session_secret(env_path) == preserved
    finally:
        if backup is not None and backup.is_file():
            shutil.move(backup, env_path)
        elif env_path.is_file() and backup is None:
            pass
