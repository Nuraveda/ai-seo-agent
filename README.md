# AI SEO Agent

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
[![Part of Mesh Pilot](https://img.shields.io/badge/Mesh%20Pilot-stack-black.svg)](https://meshpilot.app)
[![Open on GitHub](https://img.shields.io/badge/github-Nuraveda--Labs-black.svg)](https://github.com/Nuraveda-Labs/ai-seo-agent)
[![Mirrored on Codeberg](https://img.shields.io/badge/codeberg-mirror-black.svg)](https://codeberg.org/Nuraveda_lab/ai-seo-agent)

> **Part of the [Mesh Pilot](https://meshpilot.app) open-source 6-agent marketing stack.**
> Autonomous Shopify SEO — site audits, on-page optimization proposals, structured-data fixes, content-gap analysis. Ships as a Shopify Embedded App with a built-in human approval gate.

The agent crawls a Shopify storefront, scores it across meta tags / headings / schema.org / image alt / internal linking / Core Web Vitals, surfaces gaps against competitors, and proposes edits. **Nothing applies to the live storefront until the operator approves it inside the embedded app.**

## Quick start

```bash
git clone https://gitlab.com/nuraveda-lab/ai-seo-agent.git
# or: git clone https://codeberg.org/Nuraveda_lab/ai-seo-agent.git
cd ai-seo-agent

pnpm install
cp .env.example .env         # Shopify partner + GSC + LLM keys
pnpm dev                     # Remix app on http://localhost:3000
```

## What it does

- **Audit** — crawls a Shopify storefront and scores on-page SEO across meta tags, headings, schema.org markup, image alt text, internal linking, and Core Web Vitals.
- **Content gaps** — compares the storefront's product/collection pages against competitor sites and surfaces missing topics.
- **Proposals** — generates suggested edits (title rewrites, meta rewrites, schema additions) shown in the embedded app for approval.
- **Apply** — once approved, writes the changes via the Shopify Admin GraphQL API.
- **Fleet** — multi-store: one agent instance can audit/edit many stores configured in `fleet.json`.

## The HITL pattern (shared across the stack)

Every proposed edit lands in the operator-facing app UI as an approvable card. The agent never touches the live storefront without explicit sign-off. The audit log records who approved what, when. In the [Mesh Pilot](https://meshpilot.app) cockpit, the SEO surface lives alongside ads / sales / social / UGC / voice in one inbox.

## Layout

```
app/            # Remix routes — the Shopify Embedded App
agent/          # LangGraph SEO planner + applier
cli/            # standalone CLI for one-off audits
integrations/   # Shopify Admin GraphQL client, Google Search Console
extensions/     # Shopify theme app extensions (schema.org blocks)
docs/           # docs site (Mintlify)
fleet.example.json  # multi-store config template
```

## Companions in the stack

| Agent | Domain | Repo |
|---|---|---|
| AI Ads Agent | Meta / Google / TikTok / Amazon Ads | [mesh-pilot/ai-ads-agent](https://gitlab.com/nuraveda-lab/ai-ads-agent) |
| AI Sales Agent | Outbound B2B sales | [mesh-pilot/ai-sales-agent](https://gitlab.com/nuraveda-lab/ai-sales-agent) |
| AI Social Agent | Multi-platform posting + ORM | [mesh-pilot/ai-social-agent](https://gitlab.com/nuraveda-lab/ai-social-agent) |
| AI UGC Agent | Vertical video ad pipeline | [mesh-pilot/ai-ugc-agent](https://gitlab.com/nuraveda-lab/ai-ugc-agent) |
| AI Voice Agent | LiveKit-based phone agent | [mesh-pilot/ai-voice-agent](https://gitlab.com/nuraveda-lab/ai-voice-agent) |
| **AI SEO Agent** | This repo | — |

In production they're orchestrated by **[Mesh Pilot](https://meshpilot.app)** — the closed-source cockpit that runs all six in concert with shared brand context, a single web approval inbox, and cross-agent handoffs.

## Mirrors

- GitLab: [`mesh-pilot/ai-seo-agent`](https://gitlab.com/nuraveda-lab/ai-seo-agent)
- Codeberg: [`Glitch_Exec_Lab/ai-seo-agent`](https://codeberg.org/Nuraveda_lab/ai-seo-agent)

## Contributing

Bug reports + PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution shape (issue-first for non-trivial changes, preserve the HITL gate, conventional commits).

## Security

Security reports go to `support@meshpilot.app` — see [SECURITY.md](SECURITY.md). Please do not open public issues for vulnerabilities.

## Code of conduct

Be kind, stay on scope — see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) — fork it, ship products with it, no attribution required.

---

Built by [Mesh Pilot](https://meshpilot.app).
