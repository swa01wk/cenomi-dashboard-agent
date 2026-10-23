import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      "../../tests/tooling/harness/**/*.{vitest,test}.ts",
    ],
    reporters: [
      "default",
      [
        "junit",
        {
          outputFile: "../../tests/reports/frontend/junit-vitest.xml",
          includeConsoleOutput: false,
        },
      ],
    ],
    outputFile: {
      junit: "../../tests/reports/frontend/junit-vitest.xml",
    },
  },
});
