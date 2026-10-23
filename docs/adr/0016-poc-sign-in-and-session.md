# ADR-0016 — POC sign-in: fixture principals and a signed session cookie

| | |
|---|---|
| Status | **Accepted** — PR-M0 merged 2026-10-22 at `4515031` (recorded 2026-10-23). **ED-07 Option A** was approved by the project owner on 2026-10-22. |
| Date | 2026-10-22 |
| Decision IDs | ED-07 (approved), DR-019, DR-020, DXD-38, DXD-85; SEC-02, SEC-03 |
| Decision text | `docs/design/DECISION_REGISTER.md` §5.1 "ED-07" (single source; this ADR does not restate the numbered rules) |

## Context

- The POC runs locally on synthetic data. It needs several personas (Cenomi admin roles and tenant users) to demonstrate role-appropriate dashboards, scope narrowing and uniform refusals.
- It does not need real identity management. A password table or an identity provider would add dependencies, secrets and policy work that the approved scope does not ask for.
- Authorization must stay server-side in every case (DR-019, AGENTSMD-R016).

## Options considered

| Option | Summary | Outcome |
|---|---|---|
| A | Fixture principals chosen on `/sign-in`; HMAC-signed httpOnly cookie; only in `dev`, `test`, `ci` | **Chosen** |
| B | Username and password table with hashing, lockout and a login form | Rejected: adds identity management outside the approved scope |

## Decision

ED-07 Option A, exactly as worded in DECISION_REGISTER §5.1 items 1–8, including the two requirements the owner added on approval:

- **Production fails closed.** Any `CENOMI_ENV` other than `dev`, `test` or `ci` refuses to start (ARCH-R026 cases b and e). The dev sign-in routes are never mounted elsewhere.
- **Authorization and grants are always enforced and validated on the backend.** The cookie carries identity only (`principalId`, `issuedAt`, `expiresAt`). Role, grants and scope are resolved on the server for every request and pass through AccessScope.

## Consequences

- M0-T06 (sessions and AccessScope interface) and M0-T04 (`/sign-in` page) are built to this decision. ARCHITECTURE §5.4 and §6.6 are normative.
- `SESSION_SECRET` (≥ 32 bytes) is a local secret, never committed; `.env.example` holds a placeholder only (DEVENV §4).
- Changing to real authentication later replaces `/sign-in`, the dev routes and `cenomi.auth.session` only; the cookie boundary, `GET /api/v1/me` and AccessScope stay.

## Verification

| Requirement | Acceptance test |
|---|---|
| Fail closed outside `dev`, `test`, `ci` | AT-M0-T03-01 (ARCH-R026 cases b and e) |
| Dev routes absent unless `AUTH_MODE=dev_fixture` | AT-M0-T06-04 |
| Cookie attributes; identity-only payload; grants resolved on the backend | AT-M0-T06-02 |
| Tampered or expired cookie refused | AT-M0-T06-03 |
| Cookie unreadable by page script | AT-M0-T04-10 (moved from AT-M0-T06-03 by HC-2, 2026-10-23) |
| Sign-in lands on the persona's route; sign-out returns to `/sign-in` | AT-M0-T04-11 (moved from M0-T06, formerly its eighth AT, by HC-2) |
| Deny by default; narrow-only authorization | AT-M0-T06-05, AT-M0-T06-06 |
