# AI SEO Agent

Open-source AI agent for autonomous Shopify SEO — site audits, on-page
optimization proposals, structured-data fixes, and content gap analysis.

Runs as a Shopify Embedded App: the operator approves changes inside
the app UI; the agent never edits the storefront without explicit
human approval.

## What it does

- **Audit** — crawls a Shopify storefront and scores on-page SEO across
  meta tags, headings, schema.org markup, image alt text, internal
  linking, and Core Web Vitals.
- **Content gaps** — compares the storefront's product/collection pages
  against competitor sites and surfaces missing topics.
- **Proposals** — generates suggested edits (title rewrites, meta
  rewrites, schema additions) shown in the embedded app for approval.
- **Apply** — once approved, writes the changes via the Shopify Admin
  GraphQL API.
- **Fleet** — multi-store: one agent instance can audit/edit many stores
  configured in `fleet.json`.

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

## Install

```
pnpm install
cp .env.example .env   # fill in Shopify partner + GSC + LLM keys
pnpm dev               # Remix app on http://localhost:3000
```

## License

MIT — see `LICENSE`.
