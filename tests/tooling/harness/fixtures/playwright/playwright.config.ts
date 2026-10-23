import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  fullyParallel: false,
  workers: 1,
  reporter: [
    ["list"],
    [
      "junit",
      {
        outputFile: "../../../../reports/harness/e2e/junit-playwright-at02.xml",
      },
    ],
  ],
  outputDir: "../../../../reports/harness/playwright-artifacts",
  use: {
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    timezoneId: "UTC",
  },
  projects: [
    {
      name: "desktop",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1440, height: 900 },
      },
    },
  ],
});
