"""Build CI Docker images and record step status (HC-11, ARCH-R103)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.make.report import (
    STATUS_PATH,
    ensure_reports_dir,
    milestone_index,
    read_active_milestone,
)

SPEC_SET = REPO_ROOT / "specs/engineering/spec_set.yaml"
WEB_DOCKERFILE = REPO_ROOT / "apps/web/Dockerfile"
WEB_STEP_MILESTONE = "M0"
NOT_IMPLEMENTED_REASON = "apps/web/Dockerfile arrives with M0-T04"


def append_step_record(*, item: str, result: str, milestone: str, reason: str) -> None:
    ensure_reports_dir()
    record = {
        "item": item,
        "kind": "step",
        "result": result,
        "milestone": milestone,
        "reason": reason,
    }
    with STATUS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def run_docker_build(extra_args: list[str]) -> bool:
    cmd = ["docker", "buildx", "build", "--load", *extra_args]
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, check=False).returncode == 0


def main() -> int:
    active = read_active_milestone(SPEC_SET)

    api_ok = run_docker_build(["-f", "backend/Dockerfile", "-t", "cenomi-api:ci", "."])
    append_step_record(
        item="images-api",
        result="PASSED" if api_ok else "FAILED",
        milestone=active,
        reason="docker buildx build api image" if api_ok else "api image build failed",
    )
    if not api_ok:
        return 1

    if not WEB_DOCKERFILE.is_file():
        in_window = milestone_index(WEB_STEP_MILESTONE) == milestone_index(active)
        if in_window:
            append_step_record(
                item="images-web",
                result="NOT_IMPLEMENTED",
                milestone=WEB_STEP_MILESTONE,
                reason=NOT_IMPLEMENTED_REASON,
            )
            return 0
        append_step_record(
            item="images-web",
            result="FAILED",
            milestone=WEB_STEP_MILESTONE,
            reason=f"missing {WEB_DOCKERFILE.relative_to(REPO_ROOT)} outside build window",
        )
        return 1

    web_ok = run_docker_build(["-f", "apps/web/Dockerfile", "-t", "cenomi-web:ci", "."])
    append_step_record(
        item="images-web",
        result="PASSED" if web_ok else "FAILED",
        milestone=WEB_STEP_MILESTONE,
        reason="docker buildx build web image" if web_ok else "web image build failed",
    )
    return 0 if web_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
