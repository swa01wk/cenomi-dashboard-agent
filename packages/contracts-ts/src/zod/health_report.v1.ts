// GENERATED — do not edit. Run `make codegen`.
import { z } from "zod";

export const HealthReportSchema = z.strictObject({ app: z.strictObject({ migrationHead: z.string().max(80).optional(), specSet: z.string().regex(new RegExp("^[0-9]+\\.[0-9]+\\.[0-9]+$", "u")), version: z.string().max(40) }), checkedAt: z.string().datetime({ offset: true, precision: 0 }), checks: z.array(z.strictObject({ detail: z.string().max(200).optional(), durationMs: z.number().int().min(0).max(60000), name: z.enum(["process", "db_reader", "db_app", "schemas_present", "role_isolation", "migrations_at_head", "dataset"]), required: z.boolean(), status: z.enum(["pass", "fail", "skipped"]) })).min(1).max(20), status: z.enum(["ok", "degraded", "fail"]) });
export type HealthReport = z.infer<typeof HealthReportSchema>;
