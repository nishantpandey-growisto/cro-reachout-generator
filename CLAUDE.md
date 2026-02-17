# CLAUDE.md — CRO ReachOut Generator

> **This is the single source of truth for Claude Code** when working in this folder. It contains everything needed to understand, modify, test, and deploy the CRO ReachOut Generator application.

---

## 1. Project Overview

| Item | Value |
|------|-------|
| **App Name** | CRO Reach-Out Generator v2.4 |
| **Purpose** | Upload a CRO audit PDF/PPTX → auto-extract findings → generate personalized outreach emails & WhatsApp messages for Growisto's sales team |
| **Live URL** | `https://nishantpandey-growisto.github.io/cro-reachout-generator/` |
| **GitHub Repo** | `nishantpandey-growisto/cro-reachout-generator` |
| **Password** | `growisto2026` |
| **Architecture** | Single `index.html` file (~3,404 lines) — all HTML, CSS, and JavaScript in one file |
| **External Libraries** | pdf.js (3.11.174), JSZip (3.10.1), Google Fonts (Poppins) |

---

## 2. Folder Structure

```
CRO_ReachOut_Generator/
├── CLAUDE.md                              # THIS FILE
├── index.html                             # The entire application (~3,404 lines)
├── build_v2.py                            # Historical: Python build script for v1→v2 migration (not needed for ongoing dev)
├── .github/
│   └── workflows/
│       └── static.yml                     # GitHub Actions: auto-deploy to Pages on push to main
└── Training Model/                        # 13 CRO audit PDFs used to develop extraction logic
    ├── Arya Vaidya Pharmacy - CRO Audit...pdf
    ├── Chai Point - CRO Audit...pdf
    ├── Citizen - CRO Audit...pdf
    ├── Indian Milk & Honey - CRO Audit...pdf
    ├── Invigorated Water - CRO Audit...pdf
    ├── KLF Nirmal - CRO Audit...pdf
    ├── Knya - CRO Audit...pdf
    ├── Lifestyle - CRO Audit...pdf
    ├── Nu Republic - CRO Audit...pdf
    ├── Pokonut - CRO Audit...pdf
    ├── Re'equil - CRO Audit...pdf
    ├── Reisemoto - CRO Audit...pdf
    └── Yo Treasure - CRO Audit...pdf
```

---

## 3. Three User Flows

### Flow A — "I Have a CRO Audit" (Primary)
1. User uploads a PDF or PPTX audit file
2. File is parsed client-side (pdf.js for PDFs, JSZip for PPTX)
3. `extractFindings()` runs section-aware extraction to detect brand name, URL, PageSpeed scores, industry, and CRO issues
4. Results shown in a verification form: brand info + ranked issue list (sorted by impactScore, top 4 pre-checked)
5. User fills in recipient/sender names and adjusts selections
6. Generates email + WhatsApp message + follow-up sequence
7. Score summary card shown with SVG gauge + component breakdown

### Flow B — "I Need a CRO Audit"
1. Manual entry via tabbed checkbox grids (Homepage, PDP, Cart, Checkout, etc.)
2. User checks missing elements + enters PageSpeed/GA4 data
3. `collectFormData()` gathers all selections
4. Same message generation pipeline as Flow A

### Follow-Up Mode
- 4-message nurture sequence (Day 0, Day 3-5, Day 7-10, Day 14-21)
- Templates: Data Point Lead → Industry Pattern → Social Proof → Trust Story
- Each message has email + WhatsApp variants
- Context-aware (uses brand name, industry, mobile PageSpeed, specific issues)

---

## 4. Key JavaScript Architecture

### Data Structures (lines ~1154-1423)

| Structure | Lines | Purpose |
|-----------|-------|---------|
| `DEFAULT_CASE_STUDIES` | 1154-1253 | 14 case studies with `id`, `category`, `clientName`, `statHeadline`, `emailSnippet`, `whatsappSnippet`, `triggerIssues[]`, `active` |
| `DEFAULT_CLIENT_NAMES` | 1255 | 12 brand names for "We've worked with..." line |
| `FINDING_REGISTRY` | 1349-1423 | ~70+ issue types, each with: `category`, `impactScore` (1-10), `pointsAtStake`, `criticalRule`, `label`, `emailBullet`, `whatsappBullet` |
| `TITLE_ISSUE_MAP` | 2209-2308 | ~100 keyword-to-issue entries for PDF title/observation matching |

### Core Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `getCaseStudies()` | 1257-1263 | Returns case studies (localStorage override or defaults) |
| `getClientNames()` | 1265-1271 | Returns client names (localStorage override or defaults) |
| `collectFormData()` | 1276-1300 | Gathers all form inputs into a data object (Flow B) |
| `matchCaseStudies(issues)` | 1305-1321 | Matches detected issues to case studies by `triggerIssues` overlap |
| `getTopCaseStudiesForIssues(issues)` | 1323-1344 | Returns top 3 case studies (relevance-scored, deduplicated by clientName) |
| `scoreFindingsByImpact(issues, data)` | 1425-1439 | Sorts issues by impactScore, assigns HIGH/MEDIUM/LOW priority |
| `calculateEstimatedCROScore(issues, data)` | 1441-1509 | 100-point CRO score with 5 components + critical rules |
| `generateSmartBullets(data, forWhatsApp)` | 1511-1543 | Converts selected issues to message bullets using registry data |
| `displayScoreSummary(issues, data)` | 1545-1575 | Renders SVG gauge + component breakdown bars + alert cards |
| `renderDetectedIssues(detectedKeys)` | 1580-1700+ | Ranked checkbox UI: sorted by impact, top 4 pre-checked, min 3 / max 5 |
| `generateFindingBullets(...)` | 1753-1836 | Legacy v1 hardcoded priority bullet system (still used as fallback) |
| `generateEmail(data)` | 1841-1879 | Email template with smart opener, bullets, case studies, CTA |
| `generateWhatsApp(data)` | 1884-1906 | WhatsApp template (shorter, emoji-friendly) |
| `generateFollowUpSequence(data)` | 1911-2013 | 4-message nurture sequence with email + WhatsApp variants |
| `parsePDF(file)` | 2156-2173 | pdf.js parser, injects `--- PAGE X ---` markers |
| `parsePPTX(file)` | 2176-2206 | JSZip parser, extracts `<a:t>` text, injects `--- SLIDE X ---` markers |
| `extractFindings(text, fileName)` | 2311-2585 | **Core algorithm**: section-aware extraction engine (see Section 5) |
| `populateVerifyForm(findings)` | 2588-2602 | Fills verification form with extracted data |
| `loadAllData()` | 3038-3053 | Loads from localStorage or initializes defaults |
| `saveAllData(data)` | 3055-3057 | Saves to localStorage |
| `saveToHistory()` | 3076-3099 | Stores current brand to brand history |

---

## 5. Section-Aware Extraction Engine (v2.3)

This is the core algorithm that makes Flow A work. Located at lines 2311-2585.

### How It Works

**Step 1: Split text into pages/slides**
- PDF parser injects `--- PAGE X ---` markers; PPTX parser injects `--- SLIDE X ---` markers
- Text is split at these markers into per-page chunks
- If no markers found (plain text), falls back to full-text scanning

**Step 2: Classify pages into sections**
Section dividers are detected by regex patterns on each page's text:

| Pattern | Section | Treatment |
|---------|---------|-----------|
| `analytics insights` | ANALYTICS | Skip for issue detection (informational data, not findings) |
| `performance insights` | PERFORMANCE | Extract PageSpeed scores; also scan for performance issues |
| `ux insights` | UX_OBS | **Primary issue source** |
| `theme architecture` | THEME_OBS | Issue source |
| `heuristics insight/review` | HEURISTICS_OBS | Issue source |
| `proven results` | CASE_STUDIES | **Skip entirely** (Growisto portfolio, mentions every keyword) |
| `we have worked` / `they trust us` / `our leadership` / etc. | COMPANY_INFO | **Skip entirely** |

Pages inherit the most recent section divider. Pages before any divider = INTRO.

**Step 3: Brand name extraction**
Priority order: (1) filename pattern matching, (2) text pattern matching, (3) capitalized word frequency analysis. Excludes "Growisto".

**Step 4: PageSpeed extraction (PERFORMANCE section only)**
- Looks for `Score: XX/100` format from PDF performance boxes
- Falls back to `mobile page speed: XX` patterns
- Competition table matching (brand name row)
- Values of exactly 100 are discarded (false positives from "100% increase")
- Only searches PERFORMANCE section text (prevents case study false positives)

**Step 5: URL extraction (INTRO + PERFORMANCE only)**
- Prefers URLs containing the brand slug
- Falls back to first non-Growisto URL in intro pages
- Excludes competitor URLs from comparison tables

**Step 6: Industry detection (full text)**
Keyword matching: skincare, fashion, electronics, health, food, jewelry, home, automotive.

**Step 7: Issue detection (observation sections only)**
Two-pass approach using `TITLE_ISSUE_MAP`:

1. **Pass 1 — Title matching**: Extract first significant line (>15 chars) from each observation page. Match against TITLE_ISSUE_MAP keywords.
2. **Pass 2 — Observation text**: If title didn't match, extract text between "Observations" and "Recommendations" headers. Match against same map.
3. **Pass 3 — Full page fallback**: For short pages (<500 chars) with no other matches, scan full page text.

Only pages in `UX_OBS`, `THEME_OBS`, `HEURISTICS_OBS`, or `PERFORMANCE` sections are scanned.

**Step 8: `auditedSections` tracking**
Tracks which sections were found in the document. This determines scoring behavior:
- If analytics/SEO sections are absent → those categories get full marks (absence ≠ problem)
- Prevents false GA4/SEO penalties on PDFs that only audit UX/performance

### TITLE_ISSUE_MAP Format
```javascript
{ keywords: ['sticky', 'add to cart'], issue: 'no_sticky_atc' }
```
All keywords must match (AND logic). ~100 entries covering PDP, Collection, Cart, Checkout, Homepage, and Performance issues.

---

## 6. CRO Scoring Methodology (100-Point Framework)

### Component Weights

| Component | Max Points | Source |
|-----------|-----------|--------|
| Analytics & Tracking | 25 | GA4 base (5) + 5 ecommerce events (4 each) |
| Site Performance | 20 | Mobile PS/10 (max 10) + Desktop PS/20 (max 5) + CWV (5) |
| SEO Fundamentals | 15 | H1 (3) + Meta (2) + Canonical (2) + Schema (3) + Breadcrumb (2) + OG (1) + Mobile (2) |
| UX & Usability | 20 | Based on count of UX-category issues (−2 per issue, min 4) |
| Conversion Elements | 20 | Based on Conversion-category issues (deduct `pointsAtStake` per issue) |

### Critical Rules
1. **GA4 Cap**: If `no_ecom_events` or `no_ga4` detected AND analytics was actually audited → overall score capped at 50
2. **Mobile Speed Penalty**: If mobile PageSpeed < 40 → deduct 15 points from overall
3. **H1 Penalty**: If `multiple_h1` detected → deduct from SEO component
4. **auditedSections**: If analytics/SEO not audited in PDF, those components get full marks automatically

### Score Interpretation
| Range | Rating | Color |
|-------|--------|-------|
| 70-100 | Good | Green |
| 50-69 | Moderate | Yellow/Orange |
| 0-49 | Poor | Red |

---

## 7. Case Study Bank (14 Studies)

| ID | Client | Category | Stat Headline | Trigger Issues |
|----|--------|----------|---------------|----------------|
| cs_1 | Atomberg | Mobile PageSpeed / Performance | 167% conversion growth | `slow_mobile`, `poor_cwv` |
| cs_2 | TyresNmore | Funnel Optimization / Add-to-Cart | 120% add-to-cart increase | `no_sticky_atc`, `no_quick_add`, `no_buy_now` |
| cs_3 | TyresNmore | Conversion Rate (General) | 46% peak CR growth | `checkout_friction`, `no_guest_checkout` |
| cs_4 | Premium Ayurvedic brand | AOV / Cart Upsell / Cross-sell | 12% AOV increase | `no_cross_sell`, `no_shipping_bar`, `no_cross_sell_pdp` |
| cs_5 | Powerlook | Platform Migration / Stability | ₹1 Cr/month saved | `very_slow_mobile` |
| cs_6 | Atomberg | Long-term Growth / Revenue | 167% conversion + 58% YoY | `no_ga4`, `no_ecom_events`, `no_tracking` |
| cs_7 | Brand Portfolio | Trust & Social Proof | Trusted by leading brands | `no_trust_badges`, `no_social_proof`, `no_reviews_pdp` |
| cs_8 | PUMA India | SEO / Catalog Optimization | 1.7x revenue in 5 months | `no_product_schema`, `no_meta_desc`, `multiple_h1`, `no_og_tags` |
| cs_9 | Monsoon Harvest | Revenue Growth / Analytics | 700% revenue in 1 year | `no_ga4`, `no_ecom_events`, `no_tracking` |
| cs_10 | Avaana | SEO / Organic Traffic | 3.2x organic in 6 months | `no_product_schema`, `no_breadcrumb_schema`, `no_canonical`, `no_meta_desc` |
| cs_11 | Safety Signs Brand | Platform Migration / Performance | 25% CR + 90 PS score | `very_slow_mobile`, `slow_mobile`, `poor_cwv` |
| cs_12 | Vegan Skincare Brand | Checkout / UX Optimization | 50% higher CR | `checkout_friction`, `no_guest_checkout`, `slow_mobile` |
| cs_13 | Bewakoof | Fashion D2C / SEO | 20% organic traffic in 3 months | `multiple_h1`, `no_canonical`, `no_meta_desc` |
| cs_14 | Top Indian Marketplace | Marketplace / E-commerce | 2.1x non-brand clicks | `no_product_schema`, `no_breadcrumb_schema` |

### Case Study Matching Algorithm (`getTopCaseStudiesForIssues`)
- For each case study, count overlap between its `triggerIssues` and detected issues
- Score = overlap count (higher = more relevant)
- Sort by score descending
- Return top 3, deduplicated by `clientName` (no two studies from same client)

---

## 8. Message Templates

### Email Template (v2.4 — `generateEmail()`)

**Subject**: `Quick CRO wins I spotted on {brand}'s store`

**Structure**:
1. **Smart opener** — varies by CRO score severity:
   - Score < 40: "...spotted some critical gaps that are likely costing significant revenue"
   - Score 40-60: "...spotted a few high-impact opportunities"
   - Score > 60: "...spotted some quick wins that could push your results further"
2. **3-5 bullet points** — from selected issues, using `emailBullet` from FINDING_REGISTRY (case studies embedded in bullets)
3. **"About us" paragraph** — "At Growisto, our team of conversion specialists has helped brands such as {industry-aware names}..." Uses `getClientNamesForIndustry(data.industry)` for relevant social proof
4. **Score-adaptive revenue claim + 30-minute call CTA**:
   - Score < 40 → "increase revenue by 50-70%"
   - Score 40-60 → "increase revenue by 30-50%"
   - Score > 60 → "increase revenue by 15-25%"
5. **"findings in a deck"** closing

### WhatsApp Template (v2.4 — `generateWhatsApp()`)
- Shorter, emoji-friendly
- 4 bullets max
- Industry-aware brand names (top 3 from pool)
- Score-adaptive revenue claim
- 30-min walkthrough offer

### Industry-Aware Client Names (`getClientNamesForIndustry()`)
New function added in v2.4. Returns different brand pools based on `data.industry`:
- Skincare: Pilgrim, Kaya Clinic, Kama Ayurveda, OZiva, Ubeauty
- Fashion: Bewakoof, Nobero, Freakins, Powerlook, PUMA India
- Electronics: Atomberg, Boat, TyresNmore
- Health: Kaya Clinic, Kama Ayurveda, OZiva, Pathkind Labs
- Default: full DEFAULT_CLIENT_NAMES list
Falls back to localStorage override if user has customized client names.

### Future Enhancements (Not Yet Coded)
- **Follow-up template for "we already have a partner" responses** (Re'equil-style):
  - Hook into their specific comment (e.g., "reviving UX")
  - Offer category expert with specific industry experience
  - Include a live example link (e.g., UBeauty "Try Before You Buy")
  - 30-minute sync ask

---

## 9. FINDING_REGISTRY — Complete Issue Key Reference

### Analytics Category
`no_ga4` (10), `no_ecom_events` (10), `no_gtm` (7), `no_view_item_list` (5), `no_view_item` (5), `no_add_to_cart_event` (6), `no_begin_checkout` (6), `no_purchase_event` (6), `no_fb_pixel` (4), `no_fb_capi` (3), `no_clarity` (3), `no_hotjar` (2), `no_gads` (4), `no_email_platform` (3), `no_tracking` (8)

### Performance Category
`slow_mobile` (9), `very_slow_mobile` (10), `poor_cwv` (7), `poor_mobile` (6)

### SEO Category
`multiple_h1` (8), `no_meta_desc` (5), `no_product_schema` (7), `no_canonical` (5), `no_breadcrumb_schema` (4), `no_og_tags` (3), `no_alt_tags` (3), `no_sitemap` (4), `no_structured_data` (4)

### UX Category
`no_category_nav` (4), `no_search` (4), `no_announcement_bar` (3), `no_sticky_nav` (4), `no_size_chart` (5), `no_image_zoom` (4), `no_product_video` (3), `no_wishlist` (4), `no_recently_viewed` (3), `no_product_badges` (3), `no_notify_me` (3), `no_shipping_info` (4), `no_return_policy` (4), `no_cart_drawer` (5), `no_discount_field` (3), `no_guest_checkout` (6), `no_payment_options` (5), `no_order_summary` (3), `no_estimated_delivery` (4), `poor_plp_design` (6), `no_qty_selector` (4), `poor_cart_summary` (4), `no_filters` (5)

### Conversion Category
`no_value_prop` (7), `no_hero_cta` (5), `no_trust_badges` (7), `no_social_proof` (7), `no_email_capture` (4), `no_urgency_hp` (5), `no_sticky_atc` (9), `no_buy_now` (6), `no_reviews_pdp` (7), `no_urgency_pdp` (5), `no_cross_sell_pdp` (6), `no_quick_add` (7), `no_cross_sell` (7), `no_shipping_bar` (6), `no_trust_cart` (5), `no_stock_indicator` (4), `checkout_friction` (8), `no_emi_bnpl` (5), `no_cart_abandonment` (5), `no_press_mentions` (2), `weak_value_prop` (7), `weak_hero` (5)

*(Numbers in parentheses = impactScore)*

---

## 10. Training Data

### 13 CRO Audit PDFs in `Training Model/`

These are Growisto's actual CRO audit decks used to develop and test the extraction engine. They follow a consistent structure:

```
Pages 1-2:    Cover page + Index / Table of contents
Pages 3-5:    Analytics Insights (device split, traffic data, CRO recommendations)
Pages 5-9:    Performance Insights (PageSpeed scores, CWV metrics, competition table)
              → Includes performance observation slides with "(Issue/observation)" + "Recommendation"
Pages 10+:    "UX Insights" section divider
              → UX observation slides (PRIMARY source of issues)
              → Each has: bold title = issue description, "Observations" box, "Recommendations" box
Later:        "Theme Architecture Insights" section divider → more observation slides
Later:        "Heuristics Insights" / "Heuristics Review" → more observation slides
Final:        "Proven Results" section divider → Growisto case studies (NOT findings!)
              → Company info, leadership, client logos
```

**Key insight**: The slide title IS the issue description (e.g., "Add a progress bar on the cart page to encourage more purchases"). This is why TITLE_ISSUE_MAP uses AND-logic keyword matching against slide titles.

---

## 11. Growisto Brand Guidelines

### Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Primary (Teal) | `#367588` | Main brand color, CTAs, headers |
| Primary Dark | `#2a5d6d` | Hover states |
| Secondary | `#b8dbd9` | Backgrounds, cards |
| Secondary Light | `#e8f4f3` | Light backgrounds |
| Tertiary (Orange) | `#e35d34` | Warnings, emphasis, accents |
| Dark Text | `#1d1d20` | Body text |

### Typography
- **Font**: Poppins (Google Fonts)
- **Weights**: 300 (Light), 400 (Regular), 500 (Medium), 600 (Semi-Bold), 700 (Bold)

### Note on Logos
Logo files (`growisto-logo.png`, `growisto-logo-white.png`) are NOT in this folder. They are referenced from the parent `_cro_audit_system/templates/` folder or embedded inline. The app uses Growisto's teal/orange color scheme throughout the UI.

---

## 12. localStorage

### Single Key: `cro_reachout_data`

All persistent data is stored under one localStorage key as a JSON object:

```javascript
{
  brands: {},           // Brand history (keyed by UUID)
  messages: [],         // Generated message history
  conversations: [],    // Conversation tracking
  caseStudies: [...],   // Overrides DEFAULT_CASE_STUDIES if present
  clientNames: [...]    // Overrides DEFAULT_CLIENT_NAMES if present
}
```

### Settings Panel
- **Case Study Editor**: Users can add/edit/delete case studies (persisted to localStorage)
- **Client Names Editor**: Users can modify the "We've worked with..." brand list
- **Export/Import**: Full data export as JSON, import from file
- **Clear All Data**: Removes `cro_reachout_data` from localStorage

---

## 13. Development & Deployment

### Local Testing
```bash
cd /Users/growisto/Documents/Claude_Code-CRO
python3 -m http.server 8765 --bind 127.0.0.1
# Open: http://127.0.0.1:8765/CRO_ReachOut_Generator/
```

**Important**: Serve from the PARENT directory (`Claude_Code-CRO/`), not from inside `CRO_ReachOut_Generator/`. This matches the folder structure expected by the app.

Alternatively, serve directly:
```bash
cd /Users/growisto/Documents/Claude_Code-CRO/CRO_ReachOut_Generator
python3 -m http.server 8765 --bind 127.0.0.1
# Open: http://127.0.0.1:8765/
```

### Deploy to GitHub Pages
```bash
cd /Users/growisto/Documents/Claude_Code-CRO/CRO_ReachOut_Generator
git add index.html
git commit -m "v2.x: description of changes"
git push origin main
```

Auto-deploys via `.github/workflows/static.yml` (GitHub Actions). Live within 1-2 minutes at:
`https://nishantpandey-growisto.github.io/cro-reachout-generator/`

### GitHub Actions Workflow
```yaml
name: Deploy static content to Pages
on:
  push:
    branches: ["main"]
  workflow_dispatch:
# Deploys entire folder as static site
```

---

## 14. Version History

| Version | Key Changes |
|---------|-------------|
| **v1** | Basic keyword matching, hardcoded bullet generation, single flow |
| **v2.0** | FINDING_REGISTRY (~55 issue types), smart scoring (100-point methodology), 2-path dashboard ("I Have" + "I Need"), case study matching, score summary card with SVG gauge |
| **v2.1** | Incremental improvements to bullet generation and UI |
| **v2.2** | Follow-up sequence (4-message nurture), brand history, settings panel |
| **v2.3** | **Section-aware extraction engine**: title-based issue detection, TITLE_ISSUE_MAP (~100 entries), section classification, false positive elimination (no more GA4/SEO false flags from case study slides), `auditedSections` tracking, new issue types (`poor_plp_design`, `no_qty_selector`, `poor_cart_summary`, `weak_value_prop`, `weak_hero`, `no_search`, `no_filters`) |
| **v2.4** (current) | **Messaging overhaul**: industry-aware client names (`getClientNamesForIndustry()`), score-adaptive revenue claims (50-70% / 30-50% / 15-25%), new "about us" paragraph, removed redundant case studies block and 2-question closing, 30-min call (was 15), "findings in a deck" (was "short deck") |

---

## 15. Patterns & Lessons Learned

### Code Editing
- For this large HTML file (~3,400 lines), use **targeted `Edit` operations** on specific sections rather than rewriting the whole file
- When a build script is needed for multi-step transformations, `build_v2.py` demonstrates the pattern (string replacements on a backup)
- Always **read the section first** before editing — line numbers shift when you add/remove lines

### Common Gotchas
- `onclick` on parent `<div>` elements interferes with child checkboxes — put click handlers on specific header elements, not wrapper divs
- `event.stopPropagation()` on child elements works but is fragile — better to move the handler to the correct element
- The PPTX parser extracts `<a:t>` elements from XML — bold/italic formatting info is lost, only plain text is preserved
- PageSpeed regex must exclude patterns like "100% increase" and "80% revenue growth" (case study text)
- Brand name extraction must exclude "Growisto" — it appears on every page

### Testing Checklist
1. Upload a Training Model PDF (e.g., "Nu Republic") → verify correct issues detected, no false positives
2. Verify PageSpeed scores come from Performance section (not "100% from case studies")
3. Verify brand URL is correct (not a competitor URL)
4. Test Flow B manual entry → verify scoring and message generation
5. Test "Upload Different File" resets cleanly
6. Check localStorage persistence (settings, brand history)
7. Verify follow-up sequence generates correctly

### What NOT to Change Without Careful Testing
- `FINDING_REGISTRY` — keys are referenced throughout the codebase (TITLE_ISSUE_MAP, case study triggerIssues, scoring logic)
- `extractFindings()` section classification — order of sectionDividers matters
- `calculateEstimatedCROScore()` — critical rules have cascading effects on score display and message tone
- `generateEmail()`/`generateWhatsApp()` — template changes affect all generated messages

---

## 16. Quick Reference: Adding a New Issue Type

1. **Add to `FINDING_REGISTRY`** (lines ~1349-1423):
   ```javascript
   new_issue_key: { category: 'UX', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'Description', emailBullet: "...", whatsappBullet: "..." }
   ```

2. **Add to `TITLE_ISSUE_MAP`** (lines ~2209-2308):
   ```javascript
   { keywords: ['keyword1', 'keyword2'], issue: 'new_issue_key' }
   ```

3. **Optionally add to case study `triggerIssues`** if a relevant case study exists

4. **Test**: Upload a PDF that should trigger this issue and verify detection

---

## 17. Quick Reference: Modifying Message Templates

- **Email template**: `generateEmail()` at line 1841
- **WhatsApp template**: `generateWhatsApp()` at line 1884
- **Follow-up sequence**: `generateFollowUpSequence()` at line 1911
- **Smart bullets**: `generateSmartBullets()` at line 1511 (uses selected issues + FINDING_REGISTRY)
- **Legacy bullets**: `generateFindingBullets()` at line 1753 (v1 fallback, hardcoded priorities)
- **Case study integration**: `getTopCaseStudiesForIssues()` at line 1323
- **Score-adaptive opener**: Inside `generateEmail()`, line 1853 (IIFE that checks score ranges)

---

*Document Version: 1.0*
*Last Updated: February 2026*
*App Version: v2.4*
