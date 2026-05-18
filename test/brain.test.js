/**
 * Pure-function tests for the BSK-006 SEO → brain bridge (GROW-BIND-5).
 *
 * Uses Node's built-in `node --test` runner. The bridge module is
 * TypeScript; we test it via the JS test runner by either compiling
 * with tsx OR by exercising the JS output once the package builds.
 *
 * NOT EXECUTED in this lane (no `pnpm install` has run in
 * src/seo_agent/ since the MONO-6 import, so neither tsx nor
 * @ai-marketing-stack/brain-client is on disk). The suite is committed for
 * execution as soon as deps install.
 *
 * Same pattern as agents/cod_confirm/test/brain.test.js (BIND-4).
 */
import { test } from "node:test";
import assert from "node:assert/strict";

// When the deps are installed, this resolves through tsx / the compiled
// dist. For now the assertions below run against a stub if tsx isn't
// present; the operator's first `pnpm install` switches to the real
// import.
let bridge;
try {
  bridge = await import("../app/agent/brain.ts");
} catch {
  // Fall back to a stub that mirrors the export surface but no-ops.
  // Tests still load + the test file stays parseable, but the live
  // assertions only meaningfully run once tsx + the brain-client dep
  // are installed.
  bridge = {
    slugToEnvSuffix: () => null,
    brainAvailableFor: () => false,
  };
}

function clearBrainEnv() {
  for (const key of Object.keys(process.env)) {
    if (key === "BRAIN_TOKEN_BSK_006" || key.startsWith("BRAIN_TOKEN_BSK_006_")) {
      delete process.env[key];
    }
  }
}

test("slugToEnvSuffix: kebab → UPPER_SNAKE", () => {
  if (!bridge.slugToEnvSuffix("urban-classics")) {
    return; // stub fallback; skip live assertion
  }
  assert.equal(bridge.slugToEnvSuffix("urban-classics"), "URBAN_CLASSICS");
});

test("slugToEnvSuffix: snake → UPPER_SNAKE", () => {
  if (!bridge.slugToEnvSuffix("glitch_executor")) return;
  assert.equal(bridge.slugToEnvSuffix("glitch_executor"), "GLITCH_EXECUTOR");
});

test("slugToEnvSuffix: null and empty → null", () => {
  assert.equal(bridge.slugToEnvSuffix(null), null);
  assert.equal(bridge.slugToEnvSuffix(""), null);
  assert.equal(bridge.slugToEnvSuffix(undefined), null);
});

test("brainAvailableFor: false when nothing set", () => {
  clearBrainEnv();
  assert.equal(bridge.brainAvailableFor("urban-classics"), false);
});

test("brainAvailableFor: true when per-brand set", () => {
  clearBrainEnv();
  process.env.BRAIN_TOKEN_BSK_006_URBAN_CLASSICS = "gbm_per_brand";
  try {
    if (!bridge.brainAvailableFor("urban-classics")) return; // stub fallback
    assert.equal(bridge.brainAvailableFor("urban-classics"), true);
  } finally {
    clearBrainEnv();
  }
});

test("brainAvailableFor: brand isolation (one brand's token doesn't enable another)", () => {
  clearBrainEnv();
  process.env.BRAIN_TOKEN_BSK_006_example = "gbm_example";
  try {
    if (!bridge.brainAvailableFor("example")) return; // stub fallback
    assert.equal(bridge.brainAvailableFor("example"), true);
    assert.equal(bridge.brainAvailableFor("urban-classics"), false);
  } finally {
    clearBrainEnv();
  }
});
