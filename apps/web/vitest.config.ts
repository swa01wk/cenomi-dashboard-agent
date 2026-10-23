import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const repoRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../..");

export default defineConfig({
  test: {
    environment: "jsdom",
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      path.join(repoRoot, "tests/tooling/harness/**/*.vitest.test.ts"),
    ],
    reporters: [
      "default",
      [
        "junit",
        {
          outputFile: path.join(repoRoot, "tests/reports/frontend/junit-vitest.xml"),
          includeConsoleOutput: false,
        },
      ],
    ],
    outputFile: {
      junit: path.join(repoRoot, "tests/reports/frontend/junit-vitest.xml"),
    },
  },
});
