// GENERATED — do not edit. Run `make codegen`.
import { z } from "zod";

export const regionKeySchema = z.string().regex(new RegExp("^[a-z][a-z0-9-]{1,40}$", "u"));
export const mallKeySchema = z.string().regex(new RegExp("^[a-z0-9][a-z0-9-]{1,60}$", "u"));
export const tenantKeySchema = z.string().regex(new RegExp("^[a-z0-9][a-z0-9-]{1,60}$", "u"));
export const leaseKeySchema = z.string().regex(new RegExp("^[A-Z]{1,3}-[0-9]{3,8}$", "u"));
export const scopeSchema = z.discriminatedUnion("kind", [z.strictObject({ kind: z.literal("ALL"),  }), z.strictObject({ kind: z.literal("REGIONS"), regionKeys: z.array(regionKeySchema).min(1).max(3) }), z.strictObject({ kind: z.literal("MALLS"), mallKeys: z.array(mallKeySchema).min(1).max(50) }), z.strictObject({ kind: z.literal("TENANT"), tenantKeys: z.array(tenantKeySchema).min(1).max(10) }), z.strictObject({ kind: z.literal("TENANT_LEASES"), leaseKeys: z.array(leaseKeySchema).min(1).max(100) })]);
export const ScopeDecisionSchema = z.strictObject({ effective: scopeSchema.optional(), fingerprint: z.string().regex(new RegExp("^sfp_[0-9a-f]{32}$", "u")), outcome: z.enum(["allow", "narrowed", "empty", "deny"]), principalId: z.string().regex(new RegExp("^p_[a-z0-9_]{2,60}$", "u")), reasons: z.array(z.enum(["requested_within_grant", "requested_outside_grant", "no_request_full_grant", "no_grants", "hierarchy_unresolved", "permission_missing"])).min(1).max(6), requested: scopeSchema.optional() });
export type ScopeDecision = z.infer<typeof ScopeDecisionSchema>;
