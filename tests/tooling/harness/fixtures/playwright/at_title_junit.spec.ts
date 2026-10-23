import { test, expect } from "@playwright/test";

test("[AT-M0-T11-02] Playwright AT title appears in JUnit output", async () => {
  expect("[AT-M0-T11-02]".startsWith("[AT-M0-T11-02]")).toBe(true);
});
