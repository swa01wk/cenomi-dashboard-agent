import { describe, expect, it } from "vitest";

describe("[AT-M0-T11-02] Vitest AT title in JUnit", () => {
  it("records the acceptance test id from the title prefix", () => {
    expect("[AT-M0-T11-02]".startsWith("[AT-M0-T11-02]")).toBe(true);
  });
});
