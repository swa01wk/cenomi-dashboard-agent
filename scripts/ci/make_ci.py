"""Run Make targets for a CI job (specs/engineering/ci_checks.yaml)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml

CI_CHECKS = REPO_ROOT / "specs/engineering/ci_checks.yaml"

FORBIDDEN_TARGETS = frozenset({"db-downgrade", "agent-test-live"})
STATUS_PATH = REPO_ROOT / "tests/reports/status.jsonl"


def _status_line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(
        1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


def trim_specs_status_after_tooling_backend_test(path: Path, lines_before: int) -> None:
    """DEF-0002 (issue #21): drop nested Make records from tooling backend-test."""
    if not path.is_file():
        raise RuntimeError(f"expected status log after backend-test: {path}")
    lines = [
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    if not lines:
        raise RuntimeError("status.jsonl empty after specs backend-test")
    record = json.loads(lines[-1])
    if record.get("item") != "backend-test" or record.get("kind") != "target":
        raise RuntimeError(
            "last status line after specs backend-test must be backend-test target; "
            f"got {record!r}"
        )
    kept = lines[:lines_before] + [lines[-1]]
    path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def load_ci_checks() -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(CI_CHECKS.read_text(encoding="utf-8")))


def caller_is_real_ci(environ: dict[str, str] | None = None) -> bool:
    env = environ if environ is not None else dict(os.environ)
    if env.get("GITHUB_ACTIONS", "").strip().lower() == "true":
        return True
    return env.get("CENOMI_ENV", "").strip() == "ci"


def sanitized_job_env(job_env: dict[str, Any], real_ci: bool) -> dict[str, str]:
    """Job env from ci_checks.yaml must not self-authorize CI or destructive confirms."""
    out: dict[str, str] = {}
    for key, value in job_env.items():
        val = str(value)
        if key == "CENOMI_ENV" and val == "ci":
            if real_ci:
                out[key] = val
            continue
        if key == "CONFIRM" and val == "yes" and not real_ci:
            continue
        out[key] = val
    return out


def validate_target(
    target: str, merged_env: dict[str, str], real_ci: bool
) -> str | None:
    if target in FORBIDDEN_TARGETS:
        return f"target {target!r} is not allowed in make ci"
    if target == "seed-reset":
        db = merged_env.get("DB", os.environ.get("DB", "dev")).strip()
        if db != "test":
            return "seed-reset must use DB=test (never cenomi_dev)"
        if not real_ci:
            if merged_env.get("CONFIRM", "").strip() != "yes":
                return "seed-reset outside real CI requires CONFIRM=yes"
            if not sys.stdin.isatty():
                return "seed-reset outside real CI requires an interactive terminal"
    return None


def job_by_slug(slug: str, ci: dict[str, Any]) -> dict[str, Any] | None:
    needle = f"ci/{slug}" if not slug.startswith("ci/") else slug
    for job in ci["jobs"]:
        if job["name"] == needle or job["name"] == f"ci/{slug}":
            return cast(dict[str, Any], job)
    return None


def topo_make_ci_jobs(ci: dict[str, Any]) -> list[dict[str, Any]]:
    jobs = [j for j in ci["jobs"] if j.get("make_ci")]
    name_to_job = {j["name"]: j for j in jobs}
    visited: set[str] = set()
    order: list[dict[str, Any]] = []

    def visit(name: str) -> None:
        if name in visited or name not in name_to_job:
            return
        visited.add(name)
        for need in name_to_job[name].get("needs", []):
            visit(need)
        order.append(name_to_job[name])

    for job in jobs:
        visit(job["name"])
    return order


def run_make(target: str, extra_env: dict[str, str]) -> int:
    env = os.environ.copy()
    env.update(extra_env)
    cmd = ["make", target]
    print(f"+ {' '.join(cmd)}", flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=False).returncode


def run_job(slug: str) -> int:
    caller_env = dict(os.environ)
    real_ci = caller_is_real_ci(caller_env)

    ci = load_ci_checks()
    job = job_by_slug(slug, ci)
    if job is None:
        print(f"Unknown CI job: {slug!r}", file=sys.stderr)
        return 2
    if not job.get("make_ci"):
        print(f"Job {job['name']} does not use make ci targets", file=sys.stderr)
        return 2

    job_env = sanitized_job_env(job.get("env") or {}, real_ci)
    merged_preview = {**caller_env, **job_env}

    for target in job.get("targets", []):
        err = validate_target(target, merged_preview, real_ci)
        if err:
            print(f"make ci JOB={slug}: refused — {err}", file=sys.stderr)
            return 2
        lines_before = 0
        if slug == "specs" and target == "backend-test":
            lines_before = _status_line_count(STATUS_PATH)
        code = run_make(target, job_env)
        if code != 0:
            print(f"make ci JOB={slug}: failed at target {target}", file=sys.stderr)
            return code
        if slug == "specs" and target == "backend-test":
            trim_specs_status_after_tooling_backend_test(STATUS_PATH, lines_before)
    return 0


def run_all() -> int:
    ci = load_ci_checks()
    for job in topo_make_ci_jobs(ci):
        slug = job["name"].removeprefix("ci/")
        code = run_job(slug)
        if code != 0:
            return code
    return 0


def main() -> int:
    job = os.environ.get("JOB", "").strip()
    if not job:
        return run_all()
    return run_job(job)


if __name__ == "__main__":
    raise SystemExit(main())
