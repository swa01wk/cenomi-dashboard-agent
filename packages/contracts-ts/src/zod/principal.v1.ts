// GENERATED — do not edit. Run `make codegen`.
import { z } from "zod";
import { scopeSchema } from "./scope_decision.v1.js";

export const PrincipalSchema = z.strictObject({ displayName: z.string().min(1).max(120), grants: z.array(scopeSchema).max(20), permissions: z.array(z.string().regex(new RegExp("^[a-z][a-z0-9_]*(:[a-zA-Z0-9_.-]+)+$", "u"))).max(200), persona: z.enum(["admin", "tenant"]), principalId: z.string().regex(new RegExp("^p_[a-z0-9_]{2,60}$", "u")), role: z.enum(["PORTFOLIO_ADMIN", "REGIONAL_ADMIN", "MALL_MANAGER", "LEASING_MANAGER", "FITOUT_MANAGER", "TENANT_COMPANY_ADMIN", "TENANT_LEASE_CONTACT"]), sessionExpiresAt: z.string().datetime({ offset: true, precision: 0 }) });
export type Principal = z.infer<typeof PrincipalSchema>;
