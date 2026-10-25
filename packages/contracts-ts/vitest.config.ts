import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const repoRoot = path.resolve(fileURLToPath(new URL(".", import.meta.url)), "../..");

export default defineConfig({
  test: {
    include: ["src/**/*.test.ts", "src/**/*.spec.ts"],
    reporters: [
      "default",
      [
        "junit",
        {
          outputFile: path.join(repoRoot, "tests/reports/contracts/junit-contracts-vitest.xml"),
        },
      ],
    ],
  },
});
