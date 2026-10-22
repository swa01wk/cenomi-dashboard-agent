# ADR-0018 — Styling: CSS Modules with generated design-token variables

| | |
|---|---|
| Status | Proposed. **ED-09 Option A** was approved by the project owner on 2026-10-22. This ADR becomes Accepted when PR-M0 merges |
| Date | 2026-10-22 |
| Decision IDs | ED-09 (approved), DXD-01 (Ink & Violet), DR-007, DXD-61 |
| Decision text | `docs/design/DECISION_REGISTER.md` §5.1 "ED-09" (single source) |
| Related | DESIGN_SYSTEM and `specs/design/tokens.json` (PR-M2) define the token set; ADR-0003 styling row |

## Context

- The approved visual design is Ink & Violet (DXD-01). Dashboards, generated components and ECharts visualisations must share one set of colours, spacing and type values.
- The repository already generates code from single sources (ADR-0004); tokens should follow the same pattern.

## Options considered

| Option | Summary | Outcome |
|---|---|---|
| A | CSS Modules co-located with components; CSS custom properties and TypeScript constants generated from `tokens.json` | **Chosen** |
| B | Tailwind with a theme generated from `tokens.json` | Rejected: adds Tailwind and PostCSS dependencies and a second styling vocabulary |

## Decision

ED-09 Option A, exactly as worded in DECISION_REGISTER §5.1 items 1–6, including the requirement the owner added on approval:

- **The approved Ink & Violet visual design is preserved.** Colour and spacing variables are generated from `tokens.json`; no new visual language is introduced, including by the provisional M0 shell stylesheet.

## Consequences

- No UI kit, no Tailwind, no runtime CSS-in-JS.
- M0-T04 ships only `apps/web/src/styles/shell.css` with neutral provisional variables. M2 replaces it with the generated `apps/web/src/styles/tokens.css` and `packages/viz/src/tokens.ts`; both are GENERATED and drift-checked by `make contracts-check`.
- ADR-0003's styling row is settled by this ADR.

## Verification

| Requirement | Check |
|---|---|
| Shell renders with the provisional stylesheet; accessibility baseline | AT-M0-T04-03, AT-M0-T04-09 |
| Generated tokens equal `tokens.json`; no hard-coded colour in CSS Modules | Defined in PR-M2 (DESIGN_SYSTEM, M2 plan) |
