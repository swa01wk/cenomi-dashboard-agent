"""specs-check sub-check implementations (M0-T10)."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, RefResolver  # type: ignore[import-untyped]
from scripts.docs.render_engineering_tables import (
    check_drift as engineering_table_drift,
)
from scripts.docs.render_register import check_drift as register_drift
from scripts.specs.findings import Finding

ADR_REQUIRED_HEADINGS = (
    "## Context",
    "## Decision",
    "## Consequences",
    "## Verification",
)

SPEC_REQ = re.compile(r"\*\*([A-Z][A-Z0-9]*-R[0-9]{3})\*\*")
TASK_CARD_HEADING = re.compile(r"^### (M[0-6]-T[0-9]{2}) —", re.MULTILINE)
TASK_ROW = re.compile(r"^\| (\d+) \|", re.MULTILINE)
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
CARD_ID = re.compile(r"^M[0-6]-T[0-9]{2}$")
GATE_ID = re.compile(r"^M[0-6]$")
GATE_CHECK = re.compile(r"^\| (GATE-M[0-6]-[0-9]{2}) \|")

BANNED_TERM = re.compile(r"\boverdue\b", re.IGNORECASE)


def _banned_scan_roots(repo: Path) -> tuple[Path, ...]:
    roots: list[Path] = [
        repo / "backend/src",
        repo / "apps/web/src",
        repo / "tests/fixtures",
    ]
    packages = repo / "packages"
    if packages.is_dir():
        for pkg in sorted(packages.iterdir()):
            src = pkg / "src"
            if src.is_dir():
                roots.append(src)
    return tuple(roots)


CheckFn = Callable[[Path], list[Finding]]


def _load_schema(repo: Path) -> dict[str, Any]:
    path = repo / "specs/engineering/engineering.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _milestone_index(name: str) -> int:
    if not name.startswith("M") or len(name) != 2 or not name[1].isdigit():
        raise ValueError(name)
    return int(name[1])


_SCHEMA_BY_KEY = {
    "cenomi.make_targets.v1": "makeTargets",
    "cenomi.ci_checks.v1": "ciChecks",
    "cenomi.spec_set.v1": "specSet",
    "cenomi.id_conventions.v1": "idConventions",
    "cenomi.error_codes.v1": "errorCodes",
}


def check_engineering_schema(repo: Path) -> list[Finding]:
    schema = _load_schema(repo)
    findings: list[Finding] = []
    files = [
        repo / "specs/engineering/make_targets.yaml",
        repo / "specs/engineering/ci_checks.yaml",
        repo / "specs/engineering/spec_set.yaml",
        repo / "specs/traceability/id_conventions.yaml",
        repo / "specs/contracts/error_codes.v1.yaml",
    ]
    for path in files:
        if not path.is_file():
            findings.append(
                Finding(
                    str(path.relative_to(repo)), 0, "SCHEMA_MISSING", "file not found"
                )
            )
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        schema_key = str(data.get("schema", ""))
        def_name = _SCHEMA_BY_KEY.get(schema_key)
        if not def_name:
            findings.append(
                Finding(
                    str(path.relative_to(repo)),
                    0,
                    "SCHEMA_UNKNOWN",
                    f"unknown schema key {schema_key!r}",
                )
            )
            continue
        resolver = RefResolver.from_schema(schema)
        validator = Draft202012Validator(schema["$defs"][def_name], resolver=resolver)
        for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
            findings.append(
                Finding(
                    str(path.relative_to(repo)),
                    1,
                    "SCHEMA_INVALID",
                    err.message,
                )
            )
    return findings


def check_sha256sums(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    sums_path = repo / "docs/handoff/SHA256SUMS"
    if not sums_path.is_file():
        return [Finding(str(sums_path), 0, "SHA256SUMS_MISSING", "missing SHA256SUMS")]
    listed: set[str] = set()
    for line_no, line in enumerate(
        sums_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            findings.append(
                Finding(str(sums_path), line_no, "SHA256SUMS_FORMAT", "bad line")
            )
            continue
        digest, rel = parts
        if rel.startswith(("docs/reference/", "docs/design/baseline/")):
            listed.add(rel)
        if not (rel.startswith(("docs/reference/", "docs/design/baseline/"))):
            continue
        path = repo / rel
        if not path.is_file():
            findings.append(
                Finding(rel, 0, "SHA256SUMS_MISSING_FILE", "listed file absent")
            )
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            findings.append(
                Finding(rel, 0, "SHA256_MISMATCH", f"expected {digest}, got {actual}")
            )
    for prefix in ("docs/reference", "docs/design/baseline"):
        root = repo / prefix
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = str(path.relative_to(repo))
            if rel not in listed:
                findings.append(
                    Finding(rel, 0, "SHA256SUMS_UNLISTED", "file not in SHA256SUMS")
                )
    return findings


def check_adr_headings(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted((repo / "docs/adr").glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        for heading in ADR_REQUIRED_HEADINGS:
            if heading in text:
                continue
            findings.append(
                Finding(
                    str(path.relative_to(repo)),
                    0,
                    "ADR_HEADING",
                    f"missing heading {heading}",
                )
            )
    return findings


def check_adr_index(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    index = (repo / "docs/adr/README.md").read_text(encoding="utf-8")
    for path in sorted((repo / "docs/adr").glob("[0-9]*.md")):
        num = path.stem.split("-")[0]
        link = f"[{num}]({path.name})"
        if link not in index and f"]({path.name})" not in index:
            findings.append(
                Finding(
                    "docs/adr/README.md",
                    0,
                    "ADR_INDEX",
                    f"{path.name} not indexed",
                )
            )
    return findings


def check_spec_requirement_uniqueness(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(repo.glob("docs/**/*.md")):
        if "reference/" in str(path):
            continue
        seen: dict[str, int] = {}
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for match in SPEC_REQ.finditer(line):
                req_id = match.group(1)
                if req_id in seen:
                    findings.append(
                        Finding(
                            str(path.relative_to(repo)),
                            line_no,
                            "SPEC_REQ_DUP",
                            f"duplicate {req_id} (first at line {seen[req_id]})",
                        )
                    )
                else:
                    seen[req_id] = line_no
    return findings


def _family_patterns(repo: Path) -> list[tuple[str, re.Pattern[str]]]:
    data = yaml.safe_load((repo / "specs/traceability/id_conventions.yaml").read_text())
    patterns: list[tuple[str, re.Pattern[str]]] = []
    for entry in data["families"]:
        patterns.append((entry["id"], re.compile(entry["pattern"])))
    return patterns


def _known_id(token: str, patterns: list[tuple[str, re.Pattern[str]]]) -> bool:
    return any(p.fullmatch(token) for _, p in patterns)


def _malformed_probes(
    patterns: list[tuple[str, re.Pattern[str]]],
) -> list[re.Pattern[str]]:
    probes: list[re.Pattern[str]] = []
    for _, pattern in patterns:
        inner = pattern.pattern.lstrip("^").rstrip("$")
        relaxed = re.sub(r"\[0-9\]\{(\d+)\}", r"[0-9]{1,\1}", inner)
        probes.append(re.compile(rf"\b{relaxed}\b"))
    return probes


def check_id_families(repo: Path) -> list[Finding]:
    patterns = _family_patterns(repo)
    malformed = _malformed_probes(patterns)
    id_token = re.compile(
        r"\b("
        r"AT-M[0-6]-T[0-9]{2}-[0-9]{2}|"
        r"M[0-6]-T[0-9]{2}|"
        r"GATE-M[0-6]-[0-9]{2}|"
        r"DEF-[0-9]{4}|"
        r"CR-[0-9]{3}|"
        r"EXC-[0-9]{3}|"
        r"ADR-[0-9]{4}|"
        r"[A-Z][A-Z0-9]*-R[0-9]{3}|"
        r"DR-[0-9]{3}b?|"
        r"DXD-[0-9]{2}|"
        r"GDQ-[0-9]{2}|"
        r"ED-[0-9]{2}|"
        r"D-0[0-9]|"
        r"UG-[0-9]{2}|"
        r"A-[0-9]{2}|"
        r"OQ-[A-Z]+-[0-9]{2}|"
        r"CA-[0-9]{2}|"
        r"DG-[1-9]|"
        r"DEVENV-R[0-9]{3}|"
        r"ARCH-R[0-9]{3}"
        r")\b"
    )
    scan_roots = [
        repo / "docs",
        repo / "plans",
        repo / "specs",
        repo / "AGENTS.md",
        repo / ".cursor/rules",
    ]
    findings: list[Finding] = []
    for root in scan_roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {
                ".md",
                ".mdc",
                ".yaml",
                ".yml",
            }:
                continue
            if "docs/reference/" in str(path):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for line_no, line in enumerate(text.splitlines(), start=1):
                seen_on_line: set[str] = set()
                for token in id_token.findall(line):
                    seen_on_line.add(token)
                    if _known_id(token, patterns):
                        continue
                    if any(p.fullmatch(token) for p in malformed):
                        findings.append(
                            Finding(
                                str(path.relative_to(repo)),
                                line_no,
                                "ID_MALFORMED",
                                f"malformed id {token}",
                            )
                        )
                    else:
                        findings.append(
                            Finding(
                                str(path.relative_to(repo)),
                                line_no,
                                "ID_UNKNOWN",
                                f"unknown id {token}",
                            )
                        )
                for probe in malformed:
                    for match in probe.finditer(line):
                        token = match.group(0)
                        if token in seen_on_line or _known_id(token, patterns):
                            continue
                        findings.append(
                            Finding(
                                str(path.relative_to(repo)),
                                line_no,
                                "ID_MALFORMED",
                                f"malformed id {token}",
                            )
                        )
    return findings


def check_task_cards(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for plan in sorted(repo.glob("plans/M*_*.md")):
        text = plan.read_text(encoding="utf-8")
        for match in TASK_CARD_HEADING.finditer(text):
            card_id = match.group(1)
            start = match.end()
            next_heading = text.find("\n### ", start)
            block = text[start:] if next_heading == -1 else text[start:next_heading]
            rows = [int(m.group(1)) for m in TASK_ROW.finditer(block)]
            expected = set(range(1, 21))
            if set(rows) != expected:
                missing = sorted(expected - set(rows))
                findings.append(
                    Finding(
                        str(plan.relative_to(repo)),
                        text[: match.start()].count("\n") + 1,
                        "TASK_CARD_ROWS",
                        f"{card_id} missing rows {missing}",
                    )
                )
            if (
                "| 19 |" in block
                and "delivery class" in block.lower()
                and not re.search(
                    r"\| 19 \|[^\n]*\|\s*(slice|full)\b",
                    block,
                    re.IGNORECASE,
                )
            ):
                findings.append(
                    Finding(
                        str(plan.relative_to(repo)),
                        0,
                        "TASK_CARD_CLASS",
                        f"{card_id} row 19 must name slice or full",
                    )
                )
    return findings


def check_markdown_links(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(repo.glob("docs/**/*.md")) + sorted(repo.glob("plans/**/*.md")):
        if "docs/reference/" in str(path):
            continue
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for target in MD_LINK.findall(line):
                target = target.strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                dest = (path.parent / target.split("#", 1)[0]).resolve()
                if not dest.is_file():
                    findings.append(
                        Finding(
                            str(path.relative_to(repo)),
                            line_no,
                            "LINK_BROKEN",
                            f"broken link {target}",
                        )
                    )
    return findings


def _help_target_names(repo: Path, help_output: str | None = None) -> list[str]:
    if help_output is None:
        proc = subprocess.run(
            ["make", "help"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        help_output = proc.stdout
    names: list[str] = []
    for ln in help_output.splitlines():
        match = re.match(r"^  ([a-z0-9-]+)\s+", ln)
        if match:
            names.append(match.group(1))
    return names


def check_make_help(repo: Path, *, help_output: str | None = None) -> list[Finding]:
    findings: list[Finding] = []
    data = yaml.safe_load((repo / "specs/engineering/make_targets.yaml").read_text())
    yaml_names = [t["name"] for t in data["targets"]]
    help_names = _help_target_names(repo, help_output)
    if help_names != yaml_names:
        findings.append(
            Finding(
                "specs/engineering/make_targets.yaml",
                0,
                "MAKE_HELP",
                f"make help target order/names differ from YAML "
                f"(yaml={len(yaml_names)} help={len(help_names)})",
            )
        )
    summaries = {}
    for line in (repo / "Makefile").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([a-z0-9-]+):\s*##\s*(.+)$", line.strip())
        if m:
            summaries[m.group(1)] = m.group(2).strip()
    for entry in data["targets"]:
        name = entry["name"]
        if summaries.get(name) != entry["summary"]:
            findings.append(
                Finding(
                    "Makefile",
                    0,
                    "MAKE_HELP_SUMMARY",
                    f"{name} ## summary differs from make_targets.yaml",
                )
            )
    return findings


def check_ci_jobs(repo: Path) -> list[Finding]:
    workflow = repo / ".github/workflows/ci.yml"
    if not workflow.is_file():
        return []
    findings: list[Finding] = []
    expected = [
        j["name"]
        for j in yaml.safe_load(
            (repo / "specs/engineering/ci_checks.yaml").read_text()
        )["jobs"]
    ]
    text = workflow.read_text(encoding="utf-8")
    found = re.findall(r"^\s+name:\s+(ci/[^\s#]+)", text, re.MULTILINE)
    if found != expected:
        findings.append(
            Finding(
                str(workflow.relative_to(repo)),
                0,
                "CI_JOBS",
                f"job names {found} != ci_checks.yaml {expected}",
            )
        )
    return findings


def check_banned_terms(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    banned_spec_exclude = repo / "specs/engineering"
    for root in _banned_scan_roots(repo):
        if not root.exists():
            continue
        paths = [root] if root.is_file() else root.rglob("*")
        for path in paths:
            if not path.is_file():
                continue
            if path.suffix not in {
                ".py",
                ".ts",
                ".tsx",
                ".js",
                ".jsx",
                ".yaml",
                ".yml",
                ".json",
                ".md",
            }:
                continue
            for line_no, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(),
                start=1,
            ):
                if BANNED_TERM.search(line):
                    findings.append(
                        Finding(
                            str(path.relative_to(repo)),
                            line_no,
                            "BANNED_TERM",
                            'forbidden term "overdue"',
                        )
                    )
    spec_root = repo / "specs"
    if spec_root.is_dir():
        for path in spec_root.rglob("*"):
            if not path.is_file():
                continue
            if (
                banned_spec_exclude in path.parents
                or path.parent == banned_spec_exclude
            ):
                continue
            if path.suffix not in {".yaml", ".yml", ".md"}:
                continue
            for line_no, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(),
                start=1,
            ):
                if BANNED_TERM.search(line):
                    findings.append(
                        Finding(
                            str(path.relative_to(repo)),
                            line_no,
                            "BANNED_TERM",
                            'forbidden term "overdue"',
                        )
                    )
    return findings


def check_manual_results(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    schema = _load_schema(repo)
    resolver = RefResolver.from_schema(schema)
    validator = Draft202012Validator(
        schema["$defs"]["manualResults"], resolver=resolver
    )
    gates = repo / "plans/gates"
    if not gates.is_dir():
        return findings
    for path in sorted(gates.glob("M*-manual-results.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for err in validator.iter_errors(data):
            findings.append(
                Finding(
                    str(path.relative_to(repo)),
                    0,
                    "MANUAL_RESULTS",
                    err.message,
                )
            )
    return findings


def check_renderer_drift(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    for msg in engineering_table_drift(repo):
        findings.append(
            Finding(
                "docs/architecture/DEVELOPMENT_ENVIRONMENT.md", 0, "RENDER_DRIFT", msg
            )
        )
    for msg in register_drift(repo):
        findings.append(
            Finding("docs/design/DECISION_REGISTER.md", 0, "RENDER_DRIFT", msg)
        )
    return findings


def check_cursor_rules(repo: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents = repo / "AGENTS.md"
    if not agents.is_file():
        findings.append(
            Finding("AGENTS.md", 0, "AGENTS_MISSING", "AGENTS.md not found")
        )
    rules_dir = repo / ".cursor/rules"
    if not rules_dir.is_dir() or not any(rules_dir.glob("*.mdc")):
        findings.append(Finding(".cursor/rules", 0, "RULES_MISSING", "no .mdc rules"))
    return findings


def check_gate_mode(repo: Path, gate: str) -> list[Finding]:
    findings: list[Finding] = []
    if not GATE_ID.fullmatch(gate):
        findings.append(Finding("GATE", 0, "GATE_INVALID", f"invalid GATE={gate!r}"))
        return findings
    gate_idx = _milestone_index(gate)
    data = yaml.safe_load((repo / "specs/engineering/make_targets.yaml").read_text())
    records: list[dict[str, Any]] = []
    status_path = repo / "tests/reports/status.jsonl"
    if status_path.is_file():
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    last: dict[str, dict[str, Any]] = {}
    for rec in records:
        if rec.get("kind") == "target":
            last[rec.get("item", "")] = rec
    for target in data["targets"]:
        active = _milestone_index(target["active_from"])
        if active > gate_idx:
            continue
        item = target["name"]
        target_rec: dict[str, Any] | None = last.get(item)
        if target_rec is None or target_rec.get("result") != "PASSED":
            result = str(target_rec.get("result")) if target_rec else "missing"
            findings.append(
                Finding(
                    "tests/reports/status.jsonl",
                    0,
                    "GATE_TARGET",
                    f"{item} is {result}, expected PASSED for GATE={gate}",
                )
            )
    report_path = repo / "tests/reports/gate" / gate / "report.json"
    if not report_path.is_file():
        findings.append(
            Finding(
                str(report_path.relative_to(repo)),
                0,
                "GATE_REPORT_MISSING",
                f"missing gate report for GATE={gate}",
            )
        )
    if report_path.is_file():
        schema = _load_schema(repo)
        resolver = RefResolver.from_schema(schema)
        validator = Draft202012Validator(
            schema["$defs"]["gateReport"], resolver=resolver
        )
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        for err in validator.iter_errors(payload):
            findings.append(
                Finding(
                    str(report_path.relative_to(repo)), 0, "GATE_REPORT", err.message
                )
            )
    plan = repo / f"plans/{gate}_FOUNDATION.md"
    if not plan.is_file():
        for p in sorted(repo.glob("plans/M*_*.md")):
            if f"{gate}_" in p.name or p.name.startswith(f"{gate.lower()}"):
                plan = p
                break
    if plan.is_file() and report_path.is_file():
        text = plan.read_text(encoding="utf-8")
        gate_checks = GATE_CHECK.findall(text)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        reported = {c["id"] for c in payload.get("gateChecks", [])}
        for check_id in gate_checks:
            if check_id not in reported:
                findings.append(
                    Finding(
                        str(report_path.relative_to(repo)),
                        0,
                        "GATE_CHECK",
                        f"missing gate check {check_id}",
                    )
                )
    return findings


SUB_CHECKS: dict[str, CheckFn] = {
    "engineering_schema": check_engineering_schema,
    "sha256sums": check_sha256sums,
    "adr_headings": check_adr_headings,
    "adr_index": check_adr_index,
    "spec_requirement_uniqueness": check_spec_requirement_uniqueness,
    "id_families": check_id_families,
    "task_cards": check_task_cards,
    "markdown_links": check_markdown_links,
    "make_help": check_make_help,
    "ci_jobs": check_ci_jobs,
    "banned_terms": check_banned_terms,
    "manual_results": check_manual_results,
    "renderer_drift": check_renderer_drift,
    "cursor_rules": check_cursor_rules,
}
