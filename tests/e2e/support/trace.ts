import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(__dirname, "../../..");
const refsPath = path.join(repoRoot, "tests/reports/e2e/request-refs.json");

export function recordRequestRefs(refs: string[]): void {
  fs.mkdirSync(path.dirname(refsPath), { recursive: true });
  fs.writeFileSync(refsPath, JSON.stringify(refs, null, 2), "utf-8");
}

export function traceOutputDir(): string {
  return path.join(repoRoot, "tests/reports/e2e/traces");
}
