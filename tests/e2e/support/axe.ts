import AxeBuilder from "@axe-core/playwright";
import type { Page } from "@playwright/test";

export type AxeScanResult = {
  violations: Array<{ id: string; impact?: string; description: string }>;
};

export async function scanPage(page: Page): Promise<AxeScanResult> {
  const results = await new AxeBuilder({ page }).analyze();
  return {
    violations: results.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      description: v.description,
    })),
  };
}

export function seriousViolations(result: AxeScanResult): AxeScanResult["violations"] {
  return result.violations.filter(
    (v) => v.impact === "serious" || v.impact === "critical",
  );
}
