// GENERATED — do not edit. Run `make codegen`.
import { z } from "zod";

export const DatasetDescriptorSchema = z.strictObject({ asOf: z.string().date(), datasetId: z.string().regex(new RegExp("^sd-[0-9]{4}\\.[0-9]{2}\\.[0-9]{2}-[0-9]{2}$", "u")), seedHash: z.string().regex(new RegExp("^[0-9a-f]{16,64}$", "u")).optional(), source: z.enum(["config", "database"]), state: z.enum(["declared", "seeded"]), synthetic: z.literal(true), timezone: z.literal("Asia/Riyadh"), transactionalStart: z.string().date().optional() });
export type DatasetDescriptor = z.infer<typeof DatasetDescriptorSchema>;
