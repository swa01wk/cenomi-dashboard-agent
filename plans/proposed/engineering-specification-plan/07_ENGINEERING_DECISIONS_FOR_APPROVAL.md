# 7 · Engineering decisions for approval

Eleven engineering decisions are still needed. None reopens an approved design decision; they fix how the approved design is built and delivered. ED-01 to ED-06 are needed before I write the M0 specifications; ED-07 to ED-09 before M0 is built; ED-10 before PR-M4; ED-11 before PR-M5. Pick a value in the last column, or comment on a row.

| ID | Decision | Options | Recommendation and reason | Needed before | Your decision |
| --- | --- | --- | --- | --- | --- |
| ED-01 | How specifications reach the repository | A: I get push access to swa01wk/cenomi-dashboard-agent and open one PR per milestone spec set; you review and merge (supersedes DR-035). B: I publish files to the Project; you commit them (DR-035 stays) | A. It matches “committed milestone by milestone”, keeps review comments on the files, and lets CI validate the YAML and schemas in each spec PR | M0 specs |  |
| ED-02 | Backend topology | A: one FastAPI deployable with the agent runtime in-process; module boundaries enforced by import-linter. B: separate api and agent services as in TA §11, linked over internal HTTP | A. One fewer network boundary for AG-UI streaming, tracing and authorization; the boundaries still hold in code. The agent can be split out later without contract changes | M0 specs |  |
| ED-03 | Reference documents in the repository | A: frozen copies of the PRD, TA plan and API Reference, plus GD exports, in docs/reference; the repository copy is canonical for Cursor. B: keep them only in the Project; specs quote what they need | A. Composer can only cite what is in the repository, and quoting by hand risks drift | M0 specs |  |
| ED-04 | How the slice is planned | A: slice task cards are tagged inside each milestone plan; plans/SLICE\_FIVE\_DAY.md orders them into days. B: a separate slice milestone with its own cards | A. No card exists twice; the full scope extends the same cards | M0 specs |  |
| ED-05 | CI/CD scope | A: CI on every PR and on main; images built but not pushed; no deployment. B: also push images to GitHub Container Registry on tags | A. DR-037 rules out deployment, and nothing consumes pushed images | M0 specs |  |
| ED-06 | When M0 is built | A: build M0 as soon as the M0 PR is merged, while PR-M1 to PR-M6 are written; the spike report feeds PR-M4 and the ECharts result feeds PR-M2. B: build nothing until all slice specs are merged; M0 runs on slice day 1 | A. The AG-UI spec can then rest on a verified spike, and slice day 1 gains about 9 hours of buffer. It still needs your explicit go-ahead to start building | M0 specs |  |
| ED-07 | POC sign-in | A: dev sign-in that picks a fixture principal; the API issues a signed httpOnly session cookie; no passwords or identity provider. B: a username and password table | A. Roles stay backend-enforced (DR-019) without building account management | M0 build |  |
| ED-08 | Model determinism in tests | A: a replay provider returns recorded model responses keyed by request hash; CI and E2E use it; live runs use a manual workflow with the key as a secret. B: CI calls the live model | A. Deterministic, free CI; the live model is still measured in M5 | M0 build |  |
| ED-09 | Styling approach | A: CSS Modules with CSS variables generated from tokens.json; no UI kit. B: Tailwind CSS with the tokens as its theme | A. One token source, no extra framework, and it matches the hand-built DX1–DX3 components | M0 build |  |
| ED-10 | AG-UI version | A: pin AG-UI 1.0 (ag-ui-protocol 1.0.x, @ag-ui/core and @ag-ui/client 1.x); the spike confirms. B: pin the last 0.x release the DX4 design assumed | A. 1.0 is frozen and adds the cancelled outcome and pending frontend tool calls the design needs | PR-M4 |  |
| ED-11 | Evaluation scoring (DR-036) | A: deterministic checks for values, filters, grounding, isolation and schemas at 100%; an LLM judge with a rubric for explanation quality; at least 20% of judged items spot-checked by a person. B: deterministic checks plus human review only | A. It is the DR-036 proposal; the judge covers the only criteria code cannot check | PR-M5 |  |

## Configuration still to supply (not decisions)

- **Model provider, primary and fallback model names and the API key (GDQ-12):** needed before slice day 3, when the replay recordings for the 20 slice questions are made.
- **Repository push access (if ED-01 is A):** I request it through the repository connector when you approve; nothing is written until then.

## Approval checklist for this plan

- [ ] Milestone dependency plan and contract freezes (tab 1)
- [ ] Five-day slice scope, day plan and demo journeys (tab 2)
- [ ] Full-scope roadmap and milestone gates (tab 3)
- [ ] Specification inventory and PR order (tab 4)
- [ ] Repository structure and ownership rules (tab 5)
- [ ] M0 authoring plan and task cards (tab 6)
- [ ] ED-01 to ED-06 decided
- [ ] Approval to write PR-M0 into the repository
