"""Target metadata mirrored from specs/engineering/make_targets.yaml (CF-0)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Group = Literal[
    "environment",
    "database",
    "synthetic_data",
    "backend",
    "frontend",
    "agent",
    "contracts_and_integration",
    "verification",
    "full_validation",
]

GROUP_LABELS: dict[Group, str] = {
    "environment": "Environment and development",
    "database": "Database",
    "synthetic_data": "Synthetic data",
    "backend": "Backend",
    "frontend": "Frontend",
    "agent": "Agent",
    "contracts_and_integration": "Contracts and integration",
    "verification": "Verification",
    "full_validation": "Full validation",
}


@dataclass(frozen=True)
class TargetMeta:
    name: str
    group: Group
    active_from: str
    summary: str
    reason_until_active: str | None = None
    implemented: bool = False
    guard_only: bool = False


# Order matches make_targets.yaml exactly.
TARGETS: tuple[TargetMeta, ...] = (
    TargetMeta(
        "help",
        "environment",
        "M0",
        "List every target with its one-line summary, grouped as in this file.",
        implemented=True,
    ),
    TargetMeta(
        "doctor",
        "environment",
        "M0",
        "Verify the local toolchain and configuration against the pinned versions.",
        implemented=True,
    ),
    TargetMeta(
        "setup",
        "environment",
        "M0",
        "First-time setup — doctor, create .env from .env.example if absent, install dependencies.",
        implemented=True,
    ),
    TargetMeta(
        "install",
        "environment",
        "M0",
        "Install locked dependencies for backend and web (no lockfile changes).",
        implemented=True,
    ),
    TargetMeta(
        "up",
        "environment",
        "M0",
        "Build and start db, api and web; bootstrap roles and migrate the dev database; wait until healthy.",
    ),
    TargetMeta(
        "down",
        "environment",
        "M0",
        "Stop the stack. Data volumes are kept unless VOLUMES=1 CONFIRM=yes.",
        guard_only=True,
    ),
    TargetMeta(
        "logs", "environment", "M0", "Follow container logs (JSON lines for api)."
    ),
    TargetMeta(
        "clean",
        "environment",
        "M0",
        "Remove local build outputs and caches. Never removes dependencies, data volumes, .env or committed files.",
        implemented=True,
    ),
    TargetMeta(
        "db-init",
        "database",
        "M0",
        "Create the four roles and the cenomi_dev / cenomi_test databases if missing (idempotent).",
    ),
    TargetMeta(
        "db-upgrade",
        "database",
        "M0",
        "Apply Alembic migrations to head as cenomi_owner.",
    ),
    TargetMeta(
        "db-current",
        "database",
        "M0",
        "Print the current Alembic revision and whether it is head.",
    ),
    TargetMeta(
        "db-check",
        "database",
        "M0",
        "Detect drift between tables.py metadata and the migrated database (alembic check) and verify roles and grants.",
    ),
    TargetMeta("db-history", "database", "M0", "Print the migration history."),
    TargetMeta(
        "db-downgrade",
        "database",
        "M0",
        "Downgrade to a named revision. Never run by `make check` or `make ci`.",
        guard_only=True,
    ),
    TargetMeta(
        "seed",
        "synthetic_data",
        "M1",
        "Generate the deterministic dataset, snapshots and seed hash into an empty, migrated database; then verify.",
        reason_until_active="The schema and generator are specified in PR-M1.",
    ),
    TargetMeta(
        "seed-reset",
        "synthetic_data",
        "M1",
        "Drop and recreate the target database, migrate, seed and verify.",
        reason_until_active="The schema and generator are specified in PR-M1.",
    ),
    TargetMeta(
        "seed-verify",
        "synthetic_data",
        "M1",
        "Run golden invariants, canonical figures and snapshot reconciliation against a seeded database (read-only).",
        reason_until_active="The schema and generator are specified in PR-M1.",
    ),
    TargetMeta(
        "backend-format",
        "backend",
        "M0",
        "Rewrite backend code formatting and import order (writes files).",
        implemented=True,
    ),
    TargetMeta(
        "backend-lint",
        "backend",
        "M0",
        "Static checks — ruff lint, ruff format check, import-linter module boundaries, SQL safety lint.",
        implemented=True,
    ),
    TargetMeta(
        "backend-typecheck",
        "backend",
        "M0",
        "mypy in strict mode over backend/src and scripts.",
        implemented=True,
    ),
    TargetMeta(
        "backend-test",
        "backend",
        "M0",
        "Backend pytest suites — unit, and integration against cenomi_test.",
        implemented=True,
    ),
    TargetMeta(
        "frontend-format",
        "frontend",
        "M0",
        "Rewrite web and package formatting with Prettier (writes files).",
    ),
    TargetMeta(
        "frontend-lint",
        "frontend",
        "M0",
        "ESLint (flat config, boundaries, no-danger) and Prettier check across apps and packages.",
    ),
    TargetMeta(
        "frontend-typecheck",
        "frontend",
        "M0",
        "TypeScript strict type check of every TS package (tsc --noEmit).",
    ),
    TargetMeta(
        "frontend-test",
        "frontend",
        "M0",
        "Vitest unit and component tests for apps/web and packages.",
    ),
    TargetMeta(
        "frontend-build",
        "frontend",
        "M0",
        "Production build of apps/web (next build) and packages.",
    ),
    TargetMeta(
        "agent-test-mock",
        "agent",
        "M3",
        "Agent runtime tests with the scripted mock model provider (no network, no recordings).",
        reason_until_active="The agent runtime is specified in PR-M3.",
    ),
    TargetMeta(
        "agent-test-replay",
        "agent",
        "M3",
        "Golden analytical cases on the replay provider against a seeded cenomi_test.",
        reason_until_active="The agent runtime and evaluation case schema are specified in PR-M3.",
    ),
    TargetMeta(
        "agent-test-live",
        "agent",
        "M3",
        "Live-model evaluation with budgets. Never part of check or ci.",
        reason_until_active="The agent runtime is specified in PR-M3; model configuration (GDQ-12) is required.",
    ),
    TargetMeta(
        "codegen",
        "contracts_and_integration",
        "M0",
        "Regenerate every GENERATED artefact (writes files).",
    ),
    TargetMeta(
        "contracts-check",
        "contracts_and_integration",
        "M0",
        "Verify generated artefacts are current, schemas use the allowed subset, examples validate, and Pydantic exports equal the bootstrap schemas.",
    ),
    TargetMeta(
        "specs-check",
        "contracts_and_integration",
        "M0",
        "Validate specifications and engineering metadata (structure, IDs, links, frozen references, make/CI parity).",
    ),
    TargetMeta(
        "integration-test",
        "contracts_and_integration",
        "M0",
        "Cross-component tests — API contracts against the app and database, authorization boundaries, and (from M4) AG-UI event fixtures and tool execution.",
    ),
    TargetMeta(
        "e2e",
        "contracts_and_integration",
        "M0",
        "Playwright journeys with axe-core against the Compose stack (real PostgreSQL; replay model provider from M3).",
    ),
    TargetMeta(
        "trace-report",
        "verification",
        "M0",
        "Build the requirement → test trace report from milestone plans and test reports.",
    ),
    TargetMeta(
        "security-check",
        "verification",
        "M0",
        "Secret scan, dependency audit and licence report.",
    ),
    TargetMeta(
        "echarts-gate",
        "verification",
        "M0",
        "Run the DX3 gallery self-test on a local, version-pinned ECharts 5.6.0 (GDQ-06) and record the result.",
    ),
    TargetMeta(
        "replay",
        "verification",
        "M6",
        "Insight checkpoint replay to as_of and golden comparison.",
        reason_until_active="Proactive intelligence is specified in PR-M6 (slice part built before M5 under DR-010).",
    ),
    TargetMeta(
        "check",
        "full_validation",
        "M0",
        "Fast, non-destructive pre-PR validation. Needs no running database.",
        implemented=True,
    ),
    TargetMeta(
        "ci",
        "full_validation",
        "M0",
        "Stable CI entry point. Runs the targets of one CI job (JOB=…) or of every job, as declared in specs/engineering/ci_checks.yaml.",
        implemented=True,
    ),
)

TARGET_BY_NAME: dict[str, TargetMeta] = {t.name: t for t in TARGETS}
