// GENERATED — do not edit. Run `make codegen`.
import { z } from "zod";

export const ErrorEnvelopeSchema = z.strictObject({ error: z.strictObject({ code: z.string().regex(new RegExp("^[A-Z][A-Z0-9_]{2,63}$", "u")), details: z.array(z.strictObject({ path: z.string().max(200), rule: z.string().regex(new RegExp("^[a-z][a-z0-9_]{1,63}$", "u")) })).max(50).optional(), message: z.string().min(1).max(500), requestRef: z.string().regex(new RegExp("^req_[0-9a-f]{16}$", "u")), retryable: z.boolean() }) });
export type ErrorEnvelope = z.infer<typeof ErrorEnvelopeSchema>;
