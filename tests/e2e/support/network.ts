import fs from "node:fs";
import path from "node:path";
import type { Page, Request, Response } from "@playwright/test";

const repoRoot = path.resolve(__dirname, "../../..");
const networkLogDir = path.join(repoRoot, "tests/reports/e2e/network");

export type NetworkEntry = {
  method: string;
  url: string;
  status?: number;
  requestRef?: string;
};

export function attachNetworkLog(page: Page, testSlug: string): NetworkEntry[] {
  const entries: NetworkEntry[] = [];

  const recordResponse = (response: Response) => {
    const request = response.request();
    const requestRef = response.headers()["x-request-ref"];
    entries.push({
      method: request.method(),
      url: request.url(),
      status: response.status(),
      requestRef,
    });
  };

  page.on("response", recordResponse);

  page.on("close", () => {
    fs.mkdirSync(networkLogDir, { recursive: true });
    const file = path.join(networkLogDir, `${testSlug}.json`);
    fs.writeFileSync(file, JSON.stringify(entries, null, 2), "utf-8");
  });

  return entries;
}

export function extractRequestRefs(entries: NetworkEntry[]): string[] {
  const refs = new Set<string>();
  for (const entry of entries) {
    if (entry.requestRef) {
      refs.add(entry.requestRef);
    }
  }
  return [...refs];
}

export function logRequestRefFrom(request: Request): string | undefined {
  return request.headers()["x-request-ref"];
}
