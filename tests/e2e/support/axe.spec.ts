import { test, expect } from "@playwright/test";
import { attachNetworkLog, extractRequestRefs } from "./network";
import { recordRequestRefs } from "./trace";
import { scanPage, seriousViolations } from "./axe";

test("[AT-M0-T11-05] axe helper fails on a serious violation fixture", async ({ page }) => {
  await page.setContent(`
    <html lang="en">
      <body>
        <button id="btn" aria-label=""></button>
        <img src="x.png" />
      </body>
    </html>
  `);
  const result = await scanPage(page);
  expect(seriousViolations(result).length).toBeGreaterThan(0);
});

test("[AT-M0-T11-04] failure artefacts and requestRef extraction", async ({ page }, testInfo) => {
  test.fail(true, "Deliberate failure to retain Playwright artefacts");
  const slug = testInfo.titlePath.join("_").replace(/[^\w-]+/g, "_");
  const entries = attachNetworkLog(page, slug);

  await page.goto("about:blank");
  await page.route("http://127.0.0.1:8799/api/v1/demo", async (route) => {
    await route.fulfill({
      status: 500,
      headers: { "X-Request-Ref": "req-fixture-m0-t11-04" },
      body: JSON.stringify({ error: { code: "INTERNAL" } }),
    });
  });
  await Promise.all([
    page.waitForResponse("http://127.0.0.1:8799/api/v1/demo"),
    page.evaluate(async () => {
      await fetch("http://127.0.0.1:8799/api/v1/demo");
    }),
  ]);

  const refs = extractRequestRefs(entries);
  recordRequestRefs(refs);
  expect(refs).toContain("req-fixture-m0-t11-04");
  expect(true).toBe(false);
});
