/**
 * BSK-006 SEO → brain bridge (GROW-BIND-5, 2026-05-18).
 *
 * Mirrors every successful SEO agent run onto the shared
 * `brain-mcp` so sibling agents on the same brand can see
 * what SEO just audited via team_state / recent_activity / briefing.
 *
 * This is **additive**: the existing `AgentMemory` row in the
 * Prisma database stays as the agent's primary vector-searchable
 * memory (FTS + pgvector + recency decay drives planner recall).
 * The brain mirror is the sibling-visible coordination layer.
 *
 * Wiring contract (BIND-1b multi-brand pattern):
 *   - Env BRAIN_MCP_URL overrides the brain URL.
 *   - Per-brand tokens: BRAIN_TOKEN_BSK_006_<BRAND_SLUG_UPPER>.
 *     Brand identifier flows from the audit's `siteId` (which in
 *     SEO's data model is the Shopify shop slug; the matrix uses
 *     the same slugs).
 *   - Legacy bare BRAIN_TOKEN_BSK_006 fallback.
 *   - Unknown / empty siteId → silent no-op.
 *   - All brain calls are fire-and-forget; brain failures NEVER
 *     block or fail the local AgentMemory insert.
 *
 * Per the brands × agents matrix in memory, BSK-006 is enrolled in
 * all 7 brands (glitch-executor, urban-classics, storico, classicoo,
 * trendsetters, example, mokshya) — broadest agent enrolment of any
 * BSK. All 7 BRAIN_TOKEN_BSK_006_* entries are in the consolidated
 * `.env` from GROW-ENV-1.
 *
 * First lane to consume `@ai-marketing-stack/brain-client` (the TS wrapper
 * shipped in BIND-0); previous BIND lanes were Python (1/1b/2/3) or
 * pure JS (4).
 */
import {
  BrainAuthError,
  BrainClient,
  BrainError,
} from "@ai-marketing-stack/brain-client";

const DEFAULT_BRAIN_URL = "http://127.0.0.1:3107/mcp";
const BRAIN_TOKEN_PREFIX = "BRAIN_TOKEN_BSK_006_";
const BRAIN_TOKEN_LEGACY = "BRAIN_TOKEN_BSK_006";
const BRAIN_URL_ENV = "BRAIN_MCP_URL";

const NON_ENV_CHARS = /[^A-Z0-9_]/g;

/**
 * Normalize a brand/site slug into the env-key suffix. Accepts
 * kebab ("urban-classics") and snake ("urban_classics") forms;
 * both produce UPPER_SNAKE ("URBAN_CLASSICS").
 */
export function slugToEnvSuffix(brand: string | null | undefined): string | null {
  if (!brand) return null;
  let s = String(brand).trim().toUpperCase().replace(/-/g, "_");
  s = s.replace(NON_ENV_CHARS, "");
  return s.length > 0 ? s : null;
}

function brainTokenFor(brand: string | null | undefined): string | null {
  const suffix = slugToEnvSuffix(brand);
  if (suffix) {
    const perBrand = process.env[BRAIN_TOKEN_PREFIX + suffix];
    if (perBrand) return perBrand;
  }
  const legacy = process.env[BRAIN_TOKEN_LEGACY];
  return legacy || null;
}

function brainUrl(): string {
  return process.env[BRAIN_URL_ENV] || DEFAULT_BRAIN_URL;
}

export function brainAvailableFor(brand: string | null | undefined): boolean {
  return brainTokenFor(brand) !== null;
}

function summarizeForBrain(text: string | null | undefined, maxChars = 240): string {
  const t = (text || "").trim().replace(/\n/g, " ");
  if (t.length <= maxChars) return t;
  return t.slice(0, maxChars - 1).replace(/\s+$/, "") + "…";
}

export interface AgentRunMirrorInput {
  /** Shopify shop slug — maps to brand identifier in `BRAIN_TOKEN_BSK_006_<SLUG>`. */
  siteId: string;
  /** Storefront platform string (Shopify / WooCommerce / etc.); recorded in payload. */
  platform: string;
  /** Number of failing signals from this audit run. */
  failingSignalCount: number;
  /** Number of findings (recommendations) the agent produced. */
  findingCount: number;
  /** Optional natural-language summary; clipped to 240 chars for the brain. */
  summaryText?: string;
  /** Optional metrics dict surfaced in the brain payload as-is. */
  metrics?: Record<string, number>;
  /** Optional local AgentMemory row id for back-reference. */
  memoryRowId?: string | null;
}

/**
 * Best-effort mirror of one completed audit run to the brain.
 *
 * Called from `memory.ts:logRun` after the Prisma `agentMemory.create`
 * resolves. Errors caught + logged via console.warn; the local
 * AgentMemory row is never rolled back on brain failure.
 */
// GROW-BIND-HARDENING-1: cap payload size at ~32 KB serialized,
// matching src/grow_platform/brain/limits.py on the Python side.
const PAYLOAD_MAX_BYTES_TS = 32 * 1024;
const MAX_STRING_VALUE_TS = 2048;
const MAX_LIST_ITEMS_TS = 50;
function _capValueTs(v: unknown): unknown {
  if (typeof v === 'string' && v.length > MAX_STRING_VALUE_TS) {
    return v.slice(0, MAX_STRING_VALUE_TS - 1).replace(/\s+$/, '') + '…';
  }
  if (Array.isArray(v) && v.length > MAX_LIST_ITEMS_TS) {
    return [...v.slice(0, MAX_LIST_ITEMS_TS), { _truncated: `...${v.length - MAX_LIST_ITEMS_TS} more items` }];
  }
  if (v && typeof v === 'object' && !Array.isArray(v)) {
    const out: Record<string, unknown> = {};
    for (const k of Object.keys(v as Record<string, unknown>)) {
      out[k] = _capValueTs((v as Record<string, unknown>)[k]);
    }
    return out;
  }
  return v;
}
export function capPayload(payload: Record<string, unknown> | null | undefined): Record<string, unknown> | null {
  if (payload == null) return null;
  const ser = (x: unknown) => new TextEncoder().encode(JSON.stringify(x ?? null)).length;
  if (ser(payload) <= PAYLOAD_MAX_BYTES_TS) return payload;
  const clipped: Record<string, unknown> = {};
  for (const k of Object.keys(payload)) clipped[k] = _capValueTs(payload[k]);
  if (ser(clipped) <= PAYLOAD_MAX_BYTES_TS) {
    clipped._truncated = 'value-level clip applied';
    return clipped;
  }
  const entries = Object.entries(clipped).map(([k, v]) => [k, v, ser({ [k]: v })] as const);
  entries.sort((a, b) => (a[2] as number) - (b[2] as number));
  const kept: Record<string, unknown> = {};
  const dropped: string[] = [];
  for (const [k, v] of entries) {
    const candidate = { ...kept, [k]: v };
    if (ser(candidate) <= PAYLOAD_MAX_BYTES_TS - 128) kept[k] = v;
    else dropped.push(k as string);
  }
  kept._truncated = `dropped fields: ${dropped.join(',')}`;
  return kept;
}

export async function mirrorAgentRunToBrain(input: AgentRunMirrorInput): Promise<void> {
  const token = brainTokenFor(input.siteId);
  if (!token) return;

  const summary =
    summarizeForBrain(
      [
        `audited ${input.platform || "site"}`,
        input.failingSignalCount > 0
          ? `${input.failingSignalCount} failing signals`
          : "no failing signals",
        `${input.findingCount} findings`,
        input.summaryText && input.summaryText.length > 0 ? input.summaryText : null,
      ]
        .filter(Boolean)
        .join(" — "),
    ) || "audit run completed";

  let brain: BrainClient | null = null;
  try {
    brain = new BrainClient({ url: brainUrl(), token });
    await brain.connect();
    await brain.append_activity({
      action: "seo.audit_run",
      summary,
      subject: input.siteId,
      payload: capPayload({
        site_id: input.siteId,
        platform: input.platform || null,
        failing_signal_count: input.failingSignalCount,
        finding_count: input.findingCount,
        metrics: input.metrics ?? null,
        memory_row_id: input.memoryRowId ?? null,
      }),
      agent_sku: "BSK-006",
    });
  } catch (err) {
    if (err instanceof BrainAuthError) {
      const suffix = slugToEnvSuffix(input.siteId) ?? "<unknown>";
      console.warn(
        `[seo_agent] brain mirror auth failed for siteId=${JSON.stringify(input.siteId)} ` +
          `(BSK-006); check env var ${BRAIN_TOKEN_PREFIX}${suffix} or legacy ${BRAIN_TOKEN_LEGACY}`,
      );
    } else if (err instanceof BrainError) {
      console.warn(`[seo_agent] brain mirror failed: ${err.message}`);
    } else {
      console.warn(`[seo_agent] brain mirror raised unexpectedly: ${(err as Error)?.message ?? err}`);
    }
  } finally {
    try { await brain?.close(); } catch { /* ignore */ }
  }
}

/**
 * Schedule a brain mirror without awaiting. Use after the local
 * `prisma.agentMemory.create` resolves so the audit-run path
 * doesn't wait on brain I/O.
 */
export function scheduleAgentRunMirror(input: AgentRunMirrorInput): void {
  if (!brainAvailableFor(input.siteId)) return;
  Promise.resolve()
    .then(() => mirrorAgentRunToBrain(input))
    .catch(() => { /* mirror already swallows; double-safety */ });
}
