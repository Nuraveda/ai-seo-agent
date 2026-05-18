#!/usr/bin/env python3
"""
Generates docs/ai-marketing-stack-google-ads-api-design.pdf — the design
document required for Google Ads API Basic Access application.

Content is purely descriptive of how AI Marketing Stack uses the Google Ads
API. No code, credentials, or client PII. Approval-friendly phrasing
that maps to Google's Required Minimum Functionality (RMF) checklist.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUT = Path(__file__).parent / "ai-marketing-stack-google-ads-api-design.pdf"


def build() -> None:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "body",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=15,
        spaceAfter=6,
    )
    h1 = ParagraphStyle(
        "h1",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        spaceAfter=12,
        textColor=colors.HexColor("#1a1a1a"),
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=18,
        spaceAfter=8,
        textColor=colors.HexColor("#0a3d62"),
    )
    h3 = ParagraphStyle(
        "h3",
        parent=styles["Heading3"],
        fontSize=11.5,
        leading=15,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor("#444"),
    )
    meta = ParagraphStyle(
        "meta",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.HexColor("#777"),
    )
    bullet = ParagraphStyle(
        "bullet",
        parent=body,
        leftIndent=18,
        bulletIndent=6,
    )

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="AI Marketing Stack — Google Ads API Design Document",
        author="an open-source project",
    )

    flow: list = []
    add = flow.append

    add(Paragraph("AI Marketing Stack — Google Ads API Design Document", h1))
    add(Paragraph(
        "an open-source project &middot; grow.example.com &middot; Version 1.0",
        meta,
    ))
    add(Spacer(1, 0.2 * cm))

    # ── 1. Overview ─────────────────────────────────────────────────
    add(Paragraph("1. Product overview", h2))
    add(Paragraph(
        "AI Marketing Stack is an AI-powered marketing-operations platform for "
        "direct-to-consumer e-commerce brands. It is operated by "
        "an open-source project as an internal tool for managing our book "
        "of client accounts &mdash; not a multi-tenant SaaS. Each client "
        "explicitly links their Google Ads account to our Manager (MCC) "
        "account before we provision any automation for them.",
        body,
    ))
    add(Paragraph(
        "The platform unifies four signal domains into a single operator "
        "workflow: search (Google Search Console + PageSpeed Insights + "
        "Natural Language), ads (Google Ads + Meta Ads + Amazon "
        "Attribution), shop data (Shopify Admin API), and on-site "
        "behaviour (GA4 + Meta Pixel reconciliation). The Google Ads API "
        "is the authoritative source for everything we do on the ads side.",
        body,
    ))

    # ── 2. How we use the Google Ads API ─────────────────────────────
    add(Paragraph("2. How we use the Google Ads API", h2))

    add(Paragraph("2.1 Read paths", h3))
    for line in [
        "Campaign, ad-group, ad, asset, and keyword performance reports "
        "ingested daily into our internal analytics store. Used to build "
        "operator dashboards and feed AI models that generate "
        "recommendations (bid, budget, creative rotation).",
        "Conversion-action metadata &mdash; names, categories, goal status, "
        "counting rules &mdash; pulled to audit configuration drift across "
        "client accounts and flag discrepancies.",
        "Audience and customer-match list metadata for lifecycle "
        "reporting. We do not re-upload end-user PII to the API; we "
        "rely on the client-side Pixel + Shopify's native Customer Match "
        "integration for audience construction.",
    ]:
        add(Paragraph(f"&bull; {line}", bullet))

    add(Paragraph("2.2 Write paths", h3))
    for line in [
        "Create and maintain conversion actions on client accounts at "
        "scale &mdash; wiring purchase events from Shopify, Shiprocket "
        "Fastrr, and FlexyPe checkouts to the right Google Ads goals "
        "with consistent naming and value/currency fields.",
        "Upload offline conversions (Amazon Attribution click matches "
        "and COD-confirmed Shopify orders) to close the cross-channel "
        "attribution loop that the standard pixel misses.",
        "Apply a small, bounded set of campaign-level optimisations "
        "(budget nudges, negative keyword additions, asset group "
        "enablement) that our operators review and approve before any "
        "API mutation is sent.",
    ]:
        add(Paragraph(f"&bull; {line}", bullet))

    add(Paragraph("2.3 What we do NOT do", h3))
    for line in [
        "No unattended autonomous bidding or account-structure changes. "
        "Every mutating API call either originates from an operator "
        "action in our admin UI or runs on a scheduled job whose "
        "change-set is audit-logged and reviewable.",
        "No exposure of the Google Ads API to end-users, clients, or "
        "third parties. Clients receive read-only dashboards built from "
        "our cached data; they never call the API directly through our "
        "tool.",
        "No reselling, white-labelling, or syndication of API access.",
        "No retention of raw API responses beyond what is needed for "
        "reporting and change-set auditing.",
    ]:
        add(Paragraph(f"&bull; {line}", bullet))

    # ── 3. Architecture ─────────────────────────────────────────────
    add(Paragraph("3. System architecture", h2))
    add(Paragraph(
        "Backend runs on Node.js (React Router, Shopify app) plus a "
        "sibling Python pipeline for long-running signal pulls. Both "
        "services run on a dedicated VM under an open-source project' "
        "control. Data is stored in PostgreSQL with pgvector for "
        "embeddings used by the AI recommendation models.",
        body,
    ))
    add(Paragraph(
        "Credentials are scoped to a single Google Cloud service "
        "account with narrowly-scoped API access. The Google Ads "
        "developer token and Manager customer id are loaded from an "
        "environment file that never leaves the VM and is not "
        "committed to version control. We rotate credentials on a "
        "quarterly cadence.",
        body,
    ))

    tbl_data = [
        ["Layer", "Role", "Google Ads touch-points"],
        ["Node admin app", "Operator UI, approvals, audit log",
         "Orchestrates approved mutations only"],
        ["Python agent",  "Scheduled signal pulls, AI analysis",
         "Read-only reports (searchStream)"],
        ["PostgreSQL",    "Cached metrics, audit trail, AI memory",
         "Stores materialised views + lineage"],
        ["Service account", "Single identity for all API calls",
         "Linked to MCC with user access"],
    ]
    tbl = Table(tbl_data, colWidths=[3.5 * cm, 5.0 * cm, 8.0 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a3d62")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT",       (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ("FONT",       (0, 1), (-1, -1), "Helvetica", 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#fafbfc"), colors.white]),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#d0d7de")),
        ("LEFTPADDING",(0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    add(Spacer(1, 0.3 * cm))
    add(tbl)

    # ── 4. API usage volume ─────────────────────────────────────────
    add(Paragraph("4. Estimated API usage", h2))
    vol = [
        ["Endpoint / Resource", "Frequency", "Requests / day"],
        ["campaign, ad_group, ad, asset reports", "Daily batched pulls", "~1,000"],
        ["conversion_action metadata",           "Twice daily audit", "~40"],
        ["conversion upload (offline)",          "Event-driven, batched", "~200"],
        ["conversion_action mutate (create/update)", "Operator-approved",   "<50"],
        ["customer + linked customer_client",    "Weekly",              "~20"],
        ["Total (current 4-brand scale)",         "&mdash;",              "~1,300"],
        ["Projected (20-brand scale, 12 months)", "&mdash;",              "~7,000"],
    ]
    vt = Table(vol, colWidths=[7.5 * cm, 4.5 * cm, 4.5 * cm])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a3d62")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT",       (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ("FONT",       (0, 1), (-1, -1), "Helvetica", 9.5),
        ("FONT",       (0, -2), (-1, -1), "Helvetica-Bold", 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -3),
         [colors.HexColor("#fafbfc"), colors.white]),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#d0d7de")),
        ("LEFTPADDING",(0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    add(Spacer(1, 0.2 * cm))
    add(vt)
    add(Paragraph(
        "Report pulls are chunked, paginated, and cached aggressively "
        "on our side (see &sect; 5). We do not re-query data we already "
        "have; incremental pulls only fetch rows changed since the last "
        "successful fetch.",
        body,
    ))

    # ── 5. RMF compliance ──────────────────────────────────────────
    add(PageBreak())
    add(Paragraph("5. Required Minimum Functionality (RMF) compliance", h2))

    rmf = [
        ["RMF requirement",
         "How AI Marketing Stack meets it"],
        ["Accurate reporting",
         "All report data is surfaced with source citation (report name, "
         "date range, last-refreshed timestamp). No metric modifications "
         "beyond documented aggregations (sum, avg, ratios)."],
        ["Campaign management (create/edit/remove)",
         "Our admin UI supports the full lifecycle for the campaign "
         "types listed in &sect;2. Operators can pause / resume / edit "
         "budgets / add-remove assets. Complex structural changes use "
         "a preview-first pattern so the proposed diff is visible before "
         "the API mutation is executed."],
        ["Ad group / ad / keyword management",
         "Supported via the same preview-first pattern. Keyword uploads "
         "are diff-checked against the live account to avoid duplicate "
         "adds and preserve historical stats."],
        ["Negative keywords and exclusions",
         "Supported at campaign and account level with operator approval."],
        ["Conversion tracking",
         "Primary use-case (see &sect;2.2). Conversion actions are "
         "created consistently across client accounts and audited "
         "daily. Offline uploads carry order_id for deterministic "
         "deduplication against pixel-fired purchases."],
        ["Budget management",
         "Budget changes originate from operator action or "
         "AI-flagged recommendations that an operator accepts. "
         "No fully-autonomous budget mutation."],
        ["Reporting &mdash; format + customisation",
         "Operators choose date range, segmentation, and metrics in the "
         "admin UI. Reports can be exported to CSV with attribution to "
         "the source Google Ads columns."],
        ["Destination of advertiser data",
         "Stored in our own PostgreSQL only. Not sold, shared, or "
         "syndicated to any third party."],
    ]
    rt = Table(rmf, colWidths=[5.5 * cm, 11.0 * cm])
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a3d62")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONT",       (0, 0), (-1, 0), "Helvetica-Bold", 10),
        ("FONT",       (0, 1), (-1, -1), "Helvetica", 9.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#fafbfc"), colors.white]),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.HexColor("#d0d7de")),
        ("LEFTPADDING",(0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    add(rt)

    # ── 6. Security + data handling ─────────────────────────────────
    add(Paragraph("6. Security and data handling", h2))
    for line in [
        "Service account credentials and developer token are stored in "
        "restricted .env files on the production VM only (0600 mode, "
        "support user only). Never committed to version control; "
        "never exposed to client browsers or third parties.",
        "Transport: all API calls are made over TLS to "
        "googleads.googleapis.com. No intermediate proxies or request "
        "logging services see raw credentials.",
        "Access model: one service account per environment (staging / "
        "prod). Rotated quarterly and immediately on any team-member "
        "departure.",
        "Data retention: report data is cached for 90 days at raw "
        "granularity, then rolled into daily aggregates. Conversion "
        "audit logs are retained for 13 months to satisfy Google Ads "
        "policy-review requests.",
        "PII handling: we do not transmit advertiser's end-user PII "
        "through the API. Customer-match and audience features use "
        "Shopify's native Google Ads integration, which performs "
        "hashing on its side.",
    ]:
        add(Paragraph(f"&bull; {line}", bullet))

    # ── 7. Why we need Basic access ─────────────────────────────────
    add(Paragraph("7. Why Basic access is needed", h2))
    add(Paragraph(
        "All client accounts linked to our MCC are production accounts "
        "with live ad spend. Test-account access does not allow us to "
        "read or write against these accounts, which blocks our primary "
        "use-cases &mdash; conversion management, reporting, and "
        "offline-conversion upload for attribution reconciliation.",
        body,
    ))
    add(Paragraph(
        "Volume and throughput under Basic access (15,000 operations "
        "per day per developer token) are more than sufficient for our "
        "current 4-brand scale and projected 20-brand scale over the "
        "next twelve months. We do not currently need Standard access.",
        body,
    ))

    # ── 8. Contact ──────────────────────────────────────────────────
    add(Paragraph("8. Contact", h2))
    add(Paragraph(
        "Tooling URL: "
        "<font color='#0a3d62'>https://grow.example.com</font>",
        body,
    ))
    add(Paragraph(
        "Technical contact: "
        "<font color='#0a3d62'>dev@example.com</font>",
        body,
    ))
    add(Paragraph(
        "Organisation: an open-source project (operator of the AI Marketing Stack "
        "marketing-operations platform).",
        body,
    ))

    doc.build(flow)
    print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
