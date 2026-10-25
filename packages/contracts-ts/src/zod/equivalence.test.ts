import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

import corpus from "./__fixtures__/equivalence.cases.json" with { type: "json" };
import { DatasetDescriptorSchema } from "./dataset_descriptor.v1.js";
import { ErrorEnvelopeSchema } from "./error_envelope.v1.js";
import { HealthReportSchema } from "./health_report.v1.js";
import { PrincipalSchema } from "./principal.v1.js";
import { ScopeDecisionSchema } from "./scope_decision.v1.js";

const repoRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../../../..");

const SCHEMAS: Record<string, { safeParse: (v: unknown) => { success: boolean } }> = {
  error_envelope: ErrorEnvelopeSchema,
  principal: PrincipalSchema,
  scope_decision: ScopeDecisionSchema,
  health_report: HealthReportSchema,
  dataset_descriptor: DatasetDescriptorSchema,
};

function zodValid(stem: string, payload: unknown): boolean {
  const schema = SCHEMAS[stem];
  return schema.safeParse(payload).success;
}

describe("[AT-M0-T05-06] zod/jsonschema equivalence", () => {
  it("matches recorded jsonschema verdicts for every case", () => {
    for (const [stem, cases] of Object.entries(corpus.schemas)) {
      for (const testCase of cases) {
        const zod = zodValid(stem, testCase.payload);
        expect(zod).toBe(testCase.jsonschemaValid);
      }
    }
  });

  it("uses the committed corpus on disk", () => {
    const fixturePath = path.join(
      repoRoot,
      "packages/contracts-ts/src/zod/__fixtures__/equivalence.cases.json",
    );
    const raw = readFileSync(fixturePath, "utf8");
    expect(raw.length).toBeGreaterThan(10);
  });
});
