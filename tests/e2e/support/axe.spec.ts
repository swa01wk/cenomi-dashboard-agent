import { test, expect } from "@playwright/test";
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
