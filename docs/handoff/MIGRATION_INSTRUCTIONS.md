# MIGRATION_INSTRUCTIONS — repository and Claude Project knowledge

Prepared 22 October 2026. Follow the steps in order. Nothing here involves application code.

## 0. What you have

The handoff package `cenomi-handoff-2026-10-22` is delivered as two zips:

| Zip | Contents | Size |
|---|---|---|
| `cenomi-handoff-2026-10-22-docs.zip` | `repo/docs/handoff/`, `repo/docs/reference/`, `repo/plans/`, `repo/docs/design/baseline/README.md`, `repo/docs/design/baseline/DESIGN_BOARDS_TEXT.md`, `SHA256SUMS`, `PACKAGE_README.md` | about 1 MB |
| `cenomi-handoff-2026-10-22-design-baseline.zip` | `repo/docs/design/baseline/` in full: boards, renders, reference models and scripts | about 46 MB |

Unzip both into the **same** folder; the `repo/` trees merge. The layout under `repo/` mirrors the intended repository paths exactly. The largest single file is 5 MB, so Git LFS is not needed.

## 1. Verify the package

```bash
cd cenomi-handoff-2026-10-22/repo
sha256sum -c ../SHA256SUMS        # every line must say OK
grep -rIl -E "sk-|sk-ant-|AKIA|ghp_|github_pat_|BEGIN .*PRIVATE KEY" . || echo "no secrets found"
```

The package was scanned on 22 Oct 2026 and contains no keys, tokens or credentials. Re-scan anyway before you commit.

## 2. Repository: documentation-only change

**Status.** Repository writing was not authorized in the original session, and that session had read-only access. **Nothing has been committed.** These are the pending repository actions, which you perform yourself (or authorize the new account to perform once it has push access, per ED-01):

| # | Pending action | Path |
|---|---|---|
| R1 | Add the handoff files | `docs/handoff/PROJECT_HANDOFF.md`, `MIGRATION_MANIFEST.md`, `ONBOARDING_PROMPT.md`, `HANDOFF_CONSISTENCY_REPORT.md`, `MIGRATION_INSTRUCTIONS.md` |
| R2 | Add the live status file | `plans/STATUS.md` |
| R3 | Add the frozen reference documents and GD exports | `docs/reference/**` (PRD, TA, API Reference, README, `final-design-gate/`, `planning-history/`) |
| R4 | Add the proposed ESP, clearly staged as proposed | `plans/proposed/engineering-specification-plan/**` |
| R5 | Add the DX1–DX6 design baseline | `docs/design/baseline/**` |
| R6 | Leave `README.md` unchanged. PR-M0 replaces it later | — |

Not included, and must not be added now:
- Specifications
- `specs/`
- `tests/`
- Code, CI or `.env` files
- API keys

The folders `docs/product`, `docs/architecture`, `docs/contracts`, `docs/adr`, `specs` and `tests/fixtures` are created by PR-M0 and later PRs, not by this change. Git does not track empty folders.

R3 puts reference copies in the repository under **ED-03 Option A**. The user approved this on 22 Oct 2026, scoped to preserving the reference documents and design baseline. *(Migration update: actions R1–R5 were performed on branch `docs/cenomi-project-handoff`, and the pull request is pending merge.)*

**Commands** (any machine with git and push rights):

```bash
git clone https://github.com/swa01wk/cenomi-dashboard-agent.git
cd cenomi-dashboard-agent
git log --oneline -1                        # expect 5bbd62a (README only)
git checkout -b docs/handoff-2026-10-22

cp -R /path/to/cenomi-handoff-2026-10-22/repo/. .

git status                                   # only docs/ and plans/ should appear
git add docs plans
git commit -m "docs: project handoff, frozen references, DX1–DX6 design baseline, proposed ESP

Documentation-only change. No application code, specs, migrations or CI.
- docs/handoff: PROJECT_HANDOFF, MIGRATION_MANIFEST, ONBOARDING_PROMPT,
  HANDOFF_CONSISTENCY_REPORT, MIGRATION_INSTRUCTIONS
- plans/STATUS.md (status as of 2026-10-22)
- docs/reference: PRD v1.0, TA v1.0, API Reference (2026-10-13), Final Design Gate exports
- docs/design/baseline: DX1–DX6 boards (canvas v27), renders, text, reference models
- plans/proposed: Engineering Specification Plan (Proposed, not approved)"
git push -u origin docs/handoff-2026-10-22
# open a pull request into main, review the file list, then merge
```

After merging, record the merge commit SHA in `plans/STATUS.md` (header line) in the next documentation PR, or tell the new Claude account so that it records the SHA.

## 3. New Claude Project knowledge

1. Create a new Project in the new account. Suggested name: "Dashboard Agent". Copy the original project description.
2. **Project instructions:**
   1. Paste the original project instructions: role, architecture principles and sections 1–14 including the source-of-truth hierarchy.
   2. Append the "Continuity rules" block from `docs/handoff/ONBOARDING_PROMPT.md`.
   3. Update section 10 "Repository Planning Structure" to point at `plans/proposed/engineering-specification-plan/05_REPOSITORY_STRUCTURE.md` as the proposed structure. It supersedes the older list of file names in section 10.
3. **Upload these knowledge files** (text only; see the manifest's recommended set):
   - `docs/handoff/PROJECT_HANDOFF.md`
   - `plans/STATUS.md`
   - `docs/handoff/MIGRATION_MANIFEST.md`
   - `docs/handoff/HANDOFF_CONSISTENCY_REPORT.md`
   - `docs/reference/Cenomi_Dashboard_Intelligence_Agent_PRD.md`
   - `docs/reference/Cenomi_Dashboard_Intelligence_Agent_Technical_Architecture_and_Implementation_Plan.md`
   - `docs/reference/ADMIN_TENANT_DASHBOARD_API_REFERENCE.md`
   - `docs/reference/README.md`
   - `docs/reference/final-design-gate/01…08_*.md` (8 files)
   - `plans/proposed/engineering-specification-plan/00…12_*.md` (13 files)
   - `docs/design/baseline/README.md`
   - `docs/design/baseline/DESIGN_BOARDS_TEXT.md`
   - Optional: `docs/reference/planning-history/PLANNING_ASSESSMENT_v0.3.md`

   Do **not** upload the HTML boards, PNGs or reference models; they stay in the repository. If the Project reports a size limit, drop the optional file first, then rely on the attached repository for the API Reference.
4. **Attach the GitHub repository** `swa01wk/cenomi-dashboard-agent` (branch `main`) as a synced source, after step 2 is merged. If you choose ED-01 Option A, grant the new account's GitHub connector push access to this repository only.
5. **Model configuration (GDQ-12)** is set later in the application's `.env` and CI secrets. It is never stored in Project knowledge or the repository.
6. Start a new conversation and paste the "First message" block from `ONBOARDING_PROMPT.md`.

## 4. Design canvas and Docs artifacts

- The original canvas (v27) and the GD and ESP Docs artifacts are **not transferable**. The exports replace them, as `MIGRATION_MANIFEST.md` § "Interactive artifacts" lists.
- To view the interactive prototypes, run `python3 -m http.server 8766` inside `docs/design/baseline/boards/` and open `http://localhost:8766/<Board>.dc.html`.
- **ECharts verification (GDQ-06), optional now and mandatory before the M2 exit:**
  1. On a machine with internet access, open `DX3-Gallery.dc.html` the same way. It loads ECharts 5.6.0 from cdnjs.
  2. Run its self-test and paste the result to the new account.
  3. The result is recorded in `plans/STATUS.md` → Verification gates.
- If the new account should continue the ESP as an editable document, it can re-create one from `plans/proposed/engineering-specification-plan/*.md`. The repository copy remains the record.

## 5. Post-migration checks (tick all before closing the old account)

- [ ] `sha256sum -c SHA256SUMS` passes.
- [ ] The documentation PR is merged; the repository contains `docs/handoff/`, `docs/reference/`, `docs/design/baseline/`, `plans/STATUS.md` and `plans/proposed/`.
- [ ] The new Project has the instructions, continuity rules, knowledge files and attached repository.
- [ ] The new account's first reply passes the checks at the end of `ONBOARDING_PROMPT.md`.
- [ ] The new account has listed ESP approval and ED-01, ED-02, ED-04, ED-05 and ED-06 as the next required approvals, with ED-03 recorded as approved (scoped).
- [ ] You have downloaded anything else you want from the old account (the zips are the complete record).

## 6. After migration: the next approvals

1. Approve or amend the ESP (tabs 1–6). The checklist is in `07_ENGINEERING_DECISIONS_FOR_APPROVAL.md`.
2. Decide ED-01, ED-02, ED-04, ED-05 and ED-06 (ED-03 is approved, scoped).
3. Authorize the new account to write PR-M0 (writing items 1–12) to the repository.
