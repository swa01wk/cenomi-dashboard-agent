# Onboarding prompt for the new Claude Project

Use this in two places:

1. **Project instructions.** Keep the original project instructions (role, architecture principles, deliverables, boundaries and source-of-truth hierarchy) and append the block "Continuity rules" below.
2. **First message.** Paste the block "First message" into the first conversation of the new Project, after uploading the knowledge files listed in `MIGRATION_MANIFEST.md` § Recommended Project knowledge set.

---

## Continuity rules (append to the Project instructions)

```text
# Continuity rules (added 22 Oct 2026 at account migration)

This project continues an existing, partly approved plan. It is NOT a new project.

- The DX1–DX6 design baseline and the Final Design Gate decision register are APPROVED and FROZEN (22 Oct 2026). Do not restart product discovery, re-explore design directions, or redesign approved functionality.
- A gap or contradiction found while writing specifications is recorded as an open question in that specification, or as a change request (CR-nnn) in plans/STATUS.md. It is never silently decided.
- Source of truth for project state: docs/handoff/PROJECT_HANDOFF.md and plans/STATUS.md. Source of truth for decisions: docs/reference/final-design-gate/03_DECISION_REGISTER.md, then accepted ADRs in docs/adr/.
- The Engineering Specification Plan in plans/proposed/ is PROPOSED until the user approves it. ED-01 to ED-11 are PROPOSED, except ED-03 Option A, which was approved on 22 Oct 2026 and is limited to storing frozen reference and design-baseline copies in the repository.
- Specification PR order: M0, M1, M2, M3, M4, M6, M5. Implementation order: M0 → M1 → M2 → M3 → M4 → M5 → M6. The complete M6 is built only after the M5 gate (DR-010). The five-day slice (~49 h) is a delivery cut, not the POC (~166.5 h, ~20 working days).
- Planning only unless the user explicitly says otherwise. Do not write application code, install packages, create migrations or CI, or push to the repository without explicit authorization.
- Never mark an unapproved specification, decision or verification as complete. Never commit API keys, credentials or tokens.
- Claude Docs, canvas and artifact links from the previous account are not accessible. Use the exported files in the repository and Project knowledge.
```

---

## First message (paste into the first conversation)

```text
You are continuing the Cenomi Dashboard Intelligence Agent POC from another Claude account. The previous conversations and artifacts are not available to you; the handoff package is. This is still a PLANNING-ONLY exercise.

Do the following, in order, and stop for my approval at the end.

1. Read docs/handoff/PROJECT_HANDOFF.md and plans/STATUS.md in full.

2. Read the authoritative documents listed in docs/handoff/MIGRATION_MANIFEST.md:
   - docs/reference/final-design-gate/01_DESIGN_REVIEW_REPORT.md and 03_DECISION_REGISTER.md in full;
   - 02, 05 and 08 of the same folder;
   - plans/proposed/engineering-specification-plan/00, 01, 04, 06 and 07 in full; the other ESP tabs as needed;
   - the PRD and the Technical Architecture plan;
   - the API Reference and docs/design/baseline/DESIGN_BOARDS_TEXT.md only where needed. They are large: search them rather than reading them end to end.
   If the repository is attached, also confirm which of these files are actually committed (and at which commit), and whether the files match SHA256SUMS.

3. Verify your understanding. Reply with a short structured summary (no more than one screen per item) covering:
   a. product vision, users and the central promise;
   b. the consolidated architecture: layers, the one-metric-service rule, the LLM-never-computes rule, AccessScope, and the AG-UI/GenUI contracts (the 15 DX5 kind names);
   c. the approved dataset sd-2026.10.20-01 and three canonical figures of your choice, with their source file;
   d. the milestone chain M0–M6 with gates and contract freezes; specification-writing order versus implementation order; why the complete M6 follows M5;
   e. the five-day slice scope versus the complete POC scope.

4. Confirm decisions and status as three lists:
   - APPROVED: GDQ-01 to GDQ-12 (Option A), DXD-80 to DXD-93, the 17 batch defaults, the scope freeze;
   - PENDING / PROPOSED: the ESP, ED-01 to ED-11 except the scoped ED-03 approval (which five still block M0 specifications), DR-036, the snap vs meta schema, GDQ-12 configuration;
   - VERIFICATION GATES still open: ECharts 5.6.0 (GDQ-06), the AG-UI spike (GDQ-11), axe-core and screen reader, latency.
   State the current milestone and phase exactly as plans/STATUS.md records them.

5. Identify missing files and contradictions:
   - every file MIGRATION_MANIFEST.md lists that you cannot find;
   - every place where two documents disagree, citing file and section, and which one wins under the source-of-truth hierarchy;
   - anything in HANDOFF_CONSISTENCY_REPORT.md you think is wrong.
   Do not resolve contradictions yourself; propose resolutions.

6. Propose how to continue the existing specification-authoring plan:
   - the exact next action (it should be: obtain approval of the ESP and decisions on ED-01, ED-02, ED-04, ED-05 and ED-06, then author PR-M0 writing items 1–12 in sessions A–E per ESP tab 6);
   - what you need from me before starting;
   - how specifications will reach the repository (ED-01).

Do not redesign anything, do not restart discovery, and do not start writing specifications or code until I approve.
```

---

## What a good first reply looks like (for the user's own check)

- Uses the DX5 kind names (`kpi`, `unavailable`, and so on), not `kpi_card` or `limitation`.
- Cites Rawdah Point Mall: 41 waiting 31+ days = 66.1% of Central's 62. Central: 130 pending.
- Names ED-01, ED-02, ED-04, ED-05 and ED-06 as the blockers for M0 specifications, and ED-03 as approved with a limited scope.
- States that nothing is committed and no specification exists. If the repository is attached, it reports what it actually finds.
- Keeps "slice" and "full POC" separate. Keeps M6 implementation after M5.
- Lists ECharts and AG-UI verification as still pending.
