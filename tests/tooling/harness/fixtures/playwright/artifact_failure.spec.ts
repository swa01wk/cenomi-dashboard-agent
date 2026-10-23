import fs from "node:fs";
import path from "node:path";
import { test, expect } from "@playwright/test";

export const EXPECTED_REQUEST_REF = "req-fixture-m0-t11-04";

const networkLogPath = path.resolve(
  __dirname,
  "../../../../reports/harness/playwright-artifacts/network-log.json",
);

test("[AT-M0-T11-04] deliberate failure retains artefacts", async ({ page }, testInfo) => {
  const entries: Array<{ requestRef?: string }> = [];
  page.on("response", (response) => {
    entries.push({ requestRef: response.headers()["x-request-ref"] });
  });

  await page.goto("about:blank");
  await page.route("http://127.0.0.1:8799/api/v1/demo", async (route) => {
    await route.fulfill({
      status: 500,
      headers: { "X-Request-Ref": EXPECTED_REQUEST_REF },
      body: JSON.stringify({ error: { code: "INTERNAL" } }),
    });
  });

  await Promise.all([
    page.waitForResponse("http://127.0.0.1:8799/api/v1/demo"),
    page.evaluate(async () => {
      await fetch("http://127.0.0.1:8799/api/v1/demo");
    }),
  ]);

  fs.mkdirSync(path.dirname(networkLogPath), { recursive: true });
  fs.writeFileSync(networkLogPath, JSON.stringify(entries, null, 2), "utf-8");

  expect(entries.map((e) => e.requestRef)).toContain(EXPECTED_REQUEST_REF);
  expect(testInfo.title).toContain("AT-M0-T11-04");
  expect(true).toBe(false);
});
