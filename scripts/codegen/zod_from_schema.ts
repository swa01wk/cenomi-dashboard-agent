/**
 * In-repo JSON Schema (ADR-0004 subset) → zod 4 generator.
 * Run: node scripts/codegen/zod_from_schema.ts
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const codegenRoot = process.env.CENOMI_CODEGEN_ROOT ?? repoRoot;
const contractsDir = path.join(codegenRoot, "specs/contracts");
const zodOutDir = path.join(codegenRoot, "packages/contracts-ts/src/zod");

const BANNER = `// GENERATED — do not edit. Run \`make codegen\`.\n`;

type Schema = Record<string, unknown>;

const SCHEMA_FILES = [
  "error_envelope.v1.schema.json",
  "principal.v1.schema.json",
  "scope_decision.v1.schema.json",
  "health_report.v1.schema.json",
  "dataset_descriptor.v1.schema.json",
];

function assertSubset(node: Schema, atRoot: boolean): void {
  const allowedRoot = new Set([
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "const",
    "pattern",
    "format",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "oneOf",
    "$ref",
    "$defs",
    "examples",
    "x-generated-from",
  ]);
  const allowed = atRoot ? allowedRoot : new Set([...allowedRoot].filter((k) => k !== "x-generated-from"));
  for (const key of Object.keys(node)) {
    if (!allowed.has(key)) {
      throw new Error(`Unsupported keyword ${key} at ${atRoot ? "root" : "nested"}`);
    }
  }
  if ("anyOf" in node || "allOf" in node) {
    throw new Error("anyOf/allOf not supported");
  }
}

function refName(ref: string): string {
  if (ref.startsWith("#/$defs/")) {
    return `${ref.slice("#/$defs/".length)}Schema`;
  }
  const m = ref.match(/^([a-z0-9_]+)\.v1\.schema\.json#\/\$defs\/(.+)$/);
  if (m) {
    return `${m[2]}Schema`;
  }
  throw new Error(`Unsupported $ref ${ref}`);
}

function emitExpr(schema: Schema, ctx: { defs: Map<string, Schema>; imports: Set<string> }): string {
  assertSubset(schema, false);
  if ("$ref" in schema) {
    const ref = String(schema.$ref);
    if (ref.includes(".schema.json")) {
      const file = ref.split("#")[0]!.replace(".v1.schema.json", "");
      ctx.imports.add(file);
      return "scopeSchema";
    }
    return refName(ref);
  }
  if ("const" in schema) {
    return `z.literal(${JSON.stringify(schema.const)})`;
  }
  if ("enum" in schema) {
    const vals = schema.enum as unknown[];
    return `z.enum([${vals.map((v) => JSON.stringify(v)).join(", ")}])`;
  }
  if ("oneOf" in schema) {
    const branches = schema.oneOf as Schema[];
    const kind = branches[0]?.properties?.kind as Schema | undefined;
    if (!kind || !("const" in kind)) {
      throw new Error("oneOf requires kind const discriminator");
    }
    const arms = branches.map((branch) => {
      const props = branch.properties as Record<string, Schema>;
      const kindConst = (props.kind as Schema).const;
      const fields = Object.entries(props)
        .filter(([k]) => k !== "kind")
        .map(([k, v]) => `${k}: ${emitExpr(v, ctx)}`);
      return `z.strictObject({ kind: z.literal(${JSON.stringify(kindConst)}), ${fields.join(", ")} })`;
    });
    return `z.discriminatedUnion("kind", [${arms.join(", ")}])`;
  }
  const typ = schema.type;
  if (typ === "string") {
    let base = "z.string()";
    if (schema.format === "date-time") base = "z.string().datetime({ offset: true, precision: 0 })";
    else if (schema.format === "date") base = "z.string().date()";
    else if (schema.format === "uuid") base = "z.string().uuid()";
    if (typeof schema.minLength === "number") base += `.min(${schema.minLength})`;
    if (typeof schema.maxLength === "number") base += `.max(${schema.maxLength})`;
    if (typeof schema.pattern === "string") {
      base += `.regex(new RegExp(${JSON.stringify(schema.pattern)}, "u"))`;
    }
    return base;
  }
  if (typ === "integer") {
    let base = "z.number().int()";
    if (typeof schema.minimum === "number") base += `.min(${schema.minimum})`;
    if (typeof schema.maximum === "number") base += `.max(${schema.maximum})`;
    return base;
  }
  if (typ === "boolean") return "z.boolean()";
  if (typ === "array") {
    const items = schema.items as Schema;
    let base = `z.array(${emitExpr(items, ctx)})`;
    if (typeof schema.minItems === "number") base += `.min(${schema.minItems})`;
    if (typeof schema.maxItems === "number") base += `.max(${schema.maxItems})`;
    return base;
  }
  if (typ === "object" || schema.properties) {
    const props = (schema.properties ?? {}) as Record<string, Schema>;
    const required = new Set((schema.required as string[] | undefined) ?? []);
    const fields = Object.entries(props).map(([key, val]) => {
      let expr = emitExpr(val, ctx);
      if (!required.has(key)) expr += ".optional()";
      return `${key}: ${expr}`;
    });
    return `z.strictObject({ ${fields.join(", ")} })`;
  }
  throw new Error(`Unsupported schema node ${JSON.stringify(schema)}`);
}

function emitDef(name: string, schema: Schema, ctx: { defs: Map<string, Schema>; imports: Set<string> }): string {
  return `export const ${name} = ${emitExpr(schema, ctx)};`;
}

function generateFile(filename: string): string {
  const raw = JSON.parse(readFileSync(path.join(contractsDir, filename), "utf8")) as Schema;
  assertSubset(raw, true);
  const stem = filename.replace(".v1.schema.json", "");
  const rootModel = stem
    .split("_")
    .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
    .join("");
  const ctx = { defs: new Map<string, Schema>(), imports: new Set<string>() };
  const defs = (raw.$defs as Record<string, Schema> | undefined) ?? {};
  let body = "";
  const defOrder = ["regionKey", "mallKey", "tenantKey", "leaseKey", "scope"];
  const defEntries = Object.entries(defs).sort(
    ([a], [b]) => defOrder.indexOf(a) - defOrder.indexOf(b),
  );
  for (const [defName, defSchema] of defEntries) {
    body += emitDef(`${defName}Schema`, defSchema, ctx) + "\n";
  }
  const rootRequired = new Set((raw.required as string[] | undefined) ?? []);
  const props = (raw.properties ?? {}) as Record<string, Schema>;
  const fields = Object.entries(props).map(([key, val]) => {
    let expr = emitExpr(val, ctx);
    if (!rootRequired.has(key)) expr += ".optional()";
    return `${key}: ${expr}`;
  });
  body += `export const ${rootModel}Schema = z.strictObject({ ${fields.join(", ")} });\n`;
  body += `export type ${rootModel} = z.infer<typeof ${rootModel}Schema>;\n`;
  const importLines = [...ctx.imports]
    .filter((s) => s !== stem)
    .map((s) => `import { scopeSchema } from "./${s}.v1.js";`)
    .join("\n");
  return BANNER + `import { z } from "zod";\n${importLines ? importLines + "\n" : ""}\n` + body;
}

mkdirSync(zodOutDir, { recursive: true });
const indexExports: string[] = [];
for (const file of SCHEMA_FILES) {
  const stem = file.replace(".v1.schema.json", "");
  const outPath = path.join(zodOutDir, `${stem}.v1.ts`);
  writeFileSync(outPath, generateFile(file), "utf8");
  indexExports.push(`export * from "./${stem}.v1.js";`);
}
writeFileSync(path.join(zodOutDir, "index.ts"), BANNER + indexExports.join("\n") + "\n", "utf8");
