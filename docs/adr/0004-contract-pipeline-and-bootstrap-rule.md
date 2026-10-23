# ADR-0004 — Contract pipeline, bootstrap rule and wire conventions

| | |
|---|---|
| Status | **Accepted** — PR-M0 merged 2026-10-22 at `4515031` (recorded 2026-10-23). |
| Date | 2026-10-22 |
| Decision IDs | DR-028 (approved, GDQ-10), DR-016, DXD-40, DXD-41 |

## Context

DR-028 makes Pydantic the source of every contract. JSON Schema 2020-12 is exported from it, TypeScript types and zod schemas are generated from that, and CI fails on drift. While specifications are being written no code exists, so contracts must start somewhere else. The approved design contracts (DX4-AGUI, DX5-Contract) use camelCase field names on the wire (`threadId`, `runId`, `resultRef`), as does AG-UI itself.

## Decision

### 1. Bootstrap rule (ESP "Sources of truth", approved)

1. Each contract is first written by hand as `specs/contracts/<name>.v<major>.schema.json` in the specification PR that freezes it.
2. When its milestone is built, the Pydantic model in `backend/src/cenomi/contracts/` must export exactly that schema. A normalized comparison runs in CI: keys sorted, `description` and `title` ignored, and `$id` compared.
3. From then on the Pydantic model is the only place to edit. The schema file becomes GENERATED (header key `x-generated-from`), and `make contracts-check` regenerates it and fails on any diff.

### 2. Allowed JSON Schema subset

The subset exists so that TypeScript and zod generation is deterministic and lossless.

| Category | Allowed |
|---|---|
| Types | `type` (object, array, string, integer, number, boolean, null) |
| Object keywords | `properties`, `required`, `additionalProperties: false` (mandatory on every object) |
| Value keywords | `enum`, `const`, `pattern`, `format` (date, date-time, uuid only), `minLength`, `maxLength`, `minimum`, `maximum`, `minItems`, `maxItems`, `items` |
| Composition | `oneOf` with a `const` discriminator property, `$ref` to `#/$defs/...` or to another file in `specs/contracts/` by relative path, `$defs` |
| Annotation | `description`, `title`, `examples` |

Further rules:
- Anything outside the subset is rejected by `make specs-check`.
- `anyOf`, `allOf`, `if/then/else`, `patternProperties`, `dependentSchemas` and open objects are not allowed.
- Every schema file declares `$schema: https://json-schema.org/draft/2020-12/schema` and a stable `$id` of the form `https://cenomi.local/contracts/<name>.v<major>.schema.json`.
- Every schema carries at least one `examples` entry. `make specs-check` validates each example against its schema.

### 3. Generators

| Output | Tool | Location |
|---|---|---|
| JSON Schema | Pydantic `model_json_schema(by_alias=True, mode="serialization")`, normalized by `scripts/codegen/export_schemas.py` | `specs/contracts/` |
| TypeScript types | `json-schema-to-typescript` (pinned) | `packages/contracts-ts/src/types/` (GENERATED) |
| zod 4 schemas | In-repo generator `scripts/codegen/zod_from_schema.ts` covering exactly the subset above | `packages/contracts-ts/src/zod/` (GENERATED) |

The zod generator is written in-repo for three reasons:
- Third-party JSON-Schema-to-zod tools do not guarantee zod 4 output.
- A zod-first source would violate DR-028.
- The restricted subset makes a small generator feasible and fully testable (compatibility assumption CA-05).

### 4. Wire conventions

| # | Rule |
|---|---|
| a | **camelCase on the wire** for every public JSON contract: REST bodies, CUSTOM AG-UI payloads, and generated TS and zod. This matches the approved DX4/DX5 contracts and AG-UI |
| b | Python attributes are snake_case; models use `alias_generator=to_camel`, `populate_by_name=True`, and serialize by alias |
| c | Database identifiers stay snake_case |
| d | Enumerated *values* are lower_snake_case unless an approved contract fixes another form. Example: AG-UI event type names stay as AG-UI defines them; lifecycle state names stay UPPER_SNAKE as in DR-032 |
| e | Timestamps are RFC 3339 strings in UTC with a `Z` suffix. Calendar dates are ISO `YYYY-MM-DD` and denote Asia/Riyadh calendar days (DR-006) |
| f | Money is `{amount: string (decimal), currency: "SAR"}` and is never a binary float. Percentages are numbers in percent units with the precision fixed by the formatting module (DR-044, DXD-44) |
| g | Absent ≠ null ≠ zero. A field that is unknown or unavailable is expressed by the contract's explicit state or coverage field, never by a magic number (DXD-16, DXD-45) |

### 5. Versioning

- The file name carries the major version.
- Adding an optional field, or a new error code to `error_codes.v1.yaml`, is additive and goes in the owning specification PR.
- Removing or renaming a field, changing a type, or narrowing an enum is breaking. It creates a v2 file alongside v1 under a CR; v1 keeps its consumers until they migrate.
- Every contract change triggers the consumer test suites in CI, because `specs/contracts/**` is a shared-contract path (DEVELOPMENT_ENVIRONMENT.md §7.3).

### 6. Error code registry

- `specs/contracts/error_codes.v1.yaml` is the single list of error codes, with the HTTP status, a retryable flag and the owning milestone for each.
- `error_envelope.v1` constrains `code` by pattern only. The registry, not the schema enum, is the authority, so later milestones add codes without a breaking change.
- A test (M0-T05) asserts that every code raised by the backend is in the registry.

## Consequences

- One edit point per contract once code exists. Composer never hand-writes a TS type for a contract.
- The restricted subset occasionally forces a flatter model. That is accepted for determinism.

## Verification

AT-M0-T05-01 to AT-M0-T05-06 in `plans/M0_FOUNDATION.md`, and GATE-M0-04.
