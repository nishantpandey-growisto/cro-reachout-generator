#!/usr/bin/env python3
"""
Build script for CRO Reach-Out Generator v2.
Reads v1 index.html and applies targeted transformations:
1. Add new CSS for score cards, path options, worksheet, etc.
2. Restructure dashboard from 3 cards to 2 + follow-up row
3. Add Path 2 section (Claude Code prompt + self-guided worksheet)
4. Add scoring engine JavaScript
5. Update message generators to use smart scoring
6. Add score summary card to output section
"""

import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
V1_PATH = os.path.join(BASE_DIR, "index.html.v1.bak")
OUTPUT_PATH = os.path.join(BASE_DIR, "index.html")

with open(V1_PATH, 'r') as f:
    html = f.read()

# ===========================
# 1. UPDATE TITLE
# ===========================
html = html.replace(
    '<title>CRO Reach-Out Generator | Growisto</title>',
    '<title>CRO Reach-Out Generator v2 | Growisto</title>'
)

# ===========================
# 2. ADD NEW CSS BEFORE </style>
# ===========================
new_css = """
        /* V2: SCORE SUMMARY CARD */
        .score-summary-card { background: var(--color-bg-primary); border-radius: 16px; padding: 28px; box-shadow: var(--shadow-lg); margin-bottom: 24px; border-top: 4px solid var(--color-primary); }
        .score-summary-grid { display: grid; grid-template-columns: 160px 1fr; gap: 28px; align-items: start; }
        .score-gauge-wrap { text-align: center; }
        .score-gauge-label { font-size: 13px; font-weight: 600; color: var(--color-text-muted); margin-top: 8px; }
        .score-components { display: flex; flex-direction: column; gap: 10px; }
        .comp-row { display: flex; align-items: center; gap: 12px; }
        .comp-label { width: 130px; font-size: 12px; font-weight: 500; color: var(--color-text-dark); flex-shrink: 0; }
        .comp-track { flex: 1; height: 8px; background: #e5e7eb; border-radius: 4px; overflow: hidden; }
        .comp-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }
        .comp-value { width: 50px; font-size: 12px; font-weight: 600; text-align: right; flex-shrink: 0; }
        .critical-alerts { margin-top: 14px; display: flex; flex-direction: column; gap: 6px; }
        .critical-alert { display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 8px; font-size: 12px; font-weight: 500; }
        .critical-alert.danger { background: var(--color-danger-bg); color: var(--color-danger); border: 1px solid #fecaca; }
        .critical-alert.warning { background: var(--color-warning-bg); color: #92400e; border: 1px solid #fed7aa; }
        .priority-badge { display: inline-flex; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .priority-badge.high { background: var(--color-danger-bg); color: var(--color-danger); }
        .priority-badge.medium { background: var(--color-warning-bg); color: #92400e; }
        .priority-badge.low { background: var(--color-success-bg); color: #065f46; }

        /* V2: PATH 2 OPTIONS */
        .path-options { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
        .path-option { background: var(--color-bg-primary); border-radius: 16px; padding: 28px; box-shadow: var(--shadow-md); cursor: pointer; border: 2px solid transparent; transition: all var(--transition-base); text-align: center; }
        .path-option:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); border-color: var(--color-primary); }
        .path-option.selected { border-color: var(--color-primary); background: var(--color-secondary-light); }
        .path-option .po-icon { font-size: 36px; margin-bottom: 14px; }
        .path-option h4 { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
        .path-option p { font-size: 13px; color: var(--color-text-muted); line-height: 1.5; }
        .prompt-box { background: #1e293b; border-radius: 12px; padding: 20px; position: relative; margin: 20px 0; }
        .prompt-box pre { font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.7; color: #e2e8f0; white-space: pre-wrap; margin: 0; }
        .prompt-copy-btn { position: absolute; top: 12px; right: 12px; padding: 6px 14px; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; background: rgba(255,255,255,0.1); color: #e2e8f0; font-size: 11px; font-weight: 500; cursor: pointer; font-family: var(--font-family); transition: all var(--transition-fast); }
        .prompt-copy-btn:hover { background: rgba(255,255,255,0.2); }
        .prompt-copy-btn.copied { background: var(--color-success); border-color: var(--color-success); }

        /* V2: WORKSHEET */
        .ws-section { background: var(--color-bg-primary); border-radius: 12px; margin-bottom: 12px; overflow: hidden; border: 1px solid #e5e7eb; box-shadow: var(--shadow-sm); }
        .ws-header { padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: background var(--transition-fast); user-select: none; }
        .ws-header:hover { background: var(--color-bg-secondary); }
        .ws-header h4 { font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 10px; }
        .ws-toggle { font-size: 16px; color: var(--color-text-muted); transition: transform var(--transition-fast); }
        .ws-section.expanded .ws-toggle { transform: rotate(180deg); }
        .ws-body { display: none; padding: 4px 20px 20px; border-top: 1px solid #f0f0f0; }
        .ws-section.expanded .ws-body { display: block; }
        .heuristic-row { margin-bottom: 14px; }
        .heuristic-label { font-size: 13px; font-weight: 500; margin-bottom: 2px; display: flex; justify-content: space-between; }
        .heuristic-desc { font-size: 11px; color: var(--color-text-muted); margin-bottom: 6px; }
        .heuristic-options { display: flex; gap: 6px; }
        .h-opt { flex: 1; padding: 6px; border: 1px solid #e5e7eb; border-radius: 6px; background: var(--color-bg-primary); text-align: center; font-size: 12px; font-weight: 500; cursor: pointer; transition: all var(--transition-fast); color: var(--color-text-muted); }
        .h-opt:hover { border-color: var(--color-primary); }
        .h-opt.sel-0 { background: var(--color-danger); color: white; border-color: var(--color-danger); }
        .h-opt.sel-1 { background: var(--color-warning); color: white; border-color: var(--color-warning); }
        .h-opt.sel-2 { background: var(--color-success); color: white; border-color: var(--color-success); }
        .live-score { position: fixed; bottom: 24px; right: 24px; background: var(--color-bg-primary); border-radius: 16px; padding: 14px 20px; box-shadow: var(--shadow-xl); border: 2px solid var(--color-primary); z-index: 200; display: none; min-width: 120px; text-align: center; }
        .live-score.visible { display: block; }
        .live-score-num { font-size: 32px; font-weight: 700; line-height: 1; }
        .live-score-txt { font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }

        /* V2: FOLLOW-UP ROW */
        .followup-row { margin-bottom: 32px; }
        .followup-btn-wide { display: flex; align-items: center; gap: 20px; background: var(--color-bg-primary); border-radius: 12px; padding: 20px 28px; box-shadow: var(--shadow-sm); cursor: pointer; border: 2px solid transparent; transition: all var(--transition-base); }
        .followup-btn-wide:hover { border-color: var(--color-primary); box-shadow: var(--shadow-md); }
        .followup-btn-wide .ficon { font-size: 28px; }
        .followup-btn-wide h4 { font-size: 15px; font-weight: 600; margin-bottom: 2px; }
        .followup-btn-wide p { font-size: 13px; color: var(--color-text-muted); }
        .followup-btn-wide .farrow { margin-left: auto; font-size: 20px; color: var(--color-text-muted); }
        .info-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; }
        .info-box p { font-size: 13px; color: #0369a1; line-height: 1.6; }
        .finding-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #f3f4f6; font-size: 13px; }
        .finding-item:last-child { border-bottom: none; }
"""

html = html.replace('    </style>', new_css + '    </style>')

# Add responsive overrides for new components
html = html.replace(
    '            .cover-title { font-size: 28px; }\n            .tabs { flex-wrap: nowrap; }',
    '            .cover-title { font-size: 28px; }\n            .tabs { flex-wrap: nowrap; }\n            .path-options { grid-template-columns: 1fr; }\n            .score-summary-grid { grid-template-columns: 1fr; }'
)

# ===========================
# 3. RESTRUCTURE DASHBOARD: 3 cards -> 2 + follow-up row
# ===========================
old_dashboard_grid = '''        <div class="dashboard-title">What would you like to do?</h1>
        <p class="dashboard-subtitle">Choose a flow to get started with generating your outreach messages.</p>
        <div class="dashboard-layout">
            <div>
                <div class="dashboard-grid">
                    <div class="flow-card" onclick="showSection('flowA')">
                        <div class="flow-card-icon">&#128196;</div>
                        <h3>I Have an Audit Report</h3>
                        <p>Upload a PDF or PPTX audit report. We'll auto-extract findings and generate personalized outreach messages.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('flowB')">
                        <div class="flow-card-icon">&#9997;&#65039;</div>
                        <h3>Manual Entry</h3>
                        <p>Enter CRO findings manually using our structured checklist. Perfect when you don't have a formal report yet.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('followUp')">
                        <div class="flow-card-icon">&#128260;</div>
                        <h3>Continue a Conversation</h3>
                        <p>Select a brand from history, provide conversation context, and get follow-up message suggestions.</p>
                    </div>
                </div>
            </div>'''

new_dashboard_grid = '''        <h1 class="dashboard-title">What would you like to do?</h1>
        <p class="dashboard-subtitle">Choose a path to generate personalized CRO outreach messages.</p>
        <div class="dashboard-layout">
            <div>
                <div class="dashboard-grid">
                    <div class="flow-card" onclick="showSection('flowA')">
                        <div class="flow-card-icon">&#128196;</div>
                        <h3>I Have a CRO Audit</h3>
                        <p>Upload a PDF or PPTX audit report. We'll auto-extract findings, score them by impact, and generate smart outreach messages.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('path2')">
                        <div class="flow-card-icon">&#128640;</div>
                        <h3>I Need a CRO Audit</h3>
                        <p>Enter brand details and either generate a Claude Code prompt for a full audit, or fill a self-guided worksheet.</p>
                    </div>
                </div>
                <div class="followup-row">
                    <div class="followup-btn-wide" onclick="showSection('followUp')">
                        <div class="ficon">&#128172;</div>
                        <div>
                            <h4>Follow-Up Mode</h4>
                            <p>Generate contextual follow-up replies for leads</p>
                        </div>
                        <div class="farrow">&rarr;</div>
                    </div>
                </div>
            </div>'''

# The old dashboard has <h1> tag but the content says </h1> after the class
# Let me match more carefully
html = html.replace(
    '<h1 class="dashboard-title">What would you like to do?</h1>\n        <p class="dashboard-subtitle">Choose a flow to get started with generating your outreach messages.</p>',
    '<h1 class="dashboard-title">What would you like to do?</h1>\n        <p class="dashboard-subtitle">Choose a path to generate personalized CRO outreach messages.</p>'
)

# Replace 3-card grid with 2-card grid
html = html.replace(
    '        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; margin-bottom: 40px; }',
    '        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }'
)

# Replace the 3 flow cards with 2 + follow-up row
old_cards = '''                <div class="dashboard-grid">
                    <div class="flow-card" onclick="showSection('flowA')">
                        <div class="flow-card-icon">&#128196;</div>
                        <h3>I Have an Audit Report</h3>
                        <p>Upload a PDF or PPTX audit report. We'll auto-extract findings and generate personalized outreach messages.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('flowB')">
                        <div class="flow-card-icon">&#9997;&#65039;</div>
                        <h3>Manual Entry</h3>
                        <p>Enter CRO findings manually using our structured checklist. Perfect when you don't have a formal report yet.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('followUp')">
                        <div class="flow-card-icon">&#128260;</div>
                        <h3>Continue a Conversation</h3>
                        <p>Select a brand from history, provide conversation context, and get follow-up message suggestions.</p>
                    </div>
                </div>'''

new_cards = '''                <div class="dashboard-grid">
                    <div class="flow-card" onclick="showSection('flowA')">
                        <div class="flow-card-icon">&#128196;</div>
                        <h3>I Have a CRO Audit</h3>
                        <p>Upload a PDF or PPTX audit report. We'll extract findings, score them by impact, and generate smart outreach messages.</p>
                    </div>
                    <div class="flow-card" onclick="showSection('path2')">
                        <div class="flow-card-icon">&#128640;</div>
                        <h3>I Need a CRO Audit</h3>
                        <p>Enter brand details and either generate a Claude Code prompt for a full audit, or fill a self-guided worksheet.</p>
                    </div>
                </div>
                <div class="followup-row">
                    <div class="followup-btn-wide" onclick="showSection('followUp')">
                        <div class="ficon">&#128172;</div>
                        <div>
                            <h4>Follow-Up Mode</h4>
                            <p>Generate contextual follow-up replies for existing leads</p>
                        </div>
                        <div class="farrow">&rarr;</div>
                    </div>
                </div>'''

html = html.replace(old_cards, new_cards)

# ===========================
# 4. ADD PATH 2 SECTION (before follow-up section)
# ===========================
path2_html = '''
    <!-- PATH 2: I Need a CRO Audit -->
    <div class="section" id="path2">
        <div class="section-header">
            <button class="back-btn" onclick="showDashboard()">&larr; Back</button>
            <h2 class="section-title">I Need a CRO Audit</h2>
        </div>

        <div class="form-row" style="margin-bottom:24px;">
            <div class="form-group">
                <label class="form-label">Brand Name *</label>
                <input class="form-input" type="text" id="p2_brandName" placeholder="e.g., Re'equil">
            </div>
            <div class="form-group">
                <label class="form-label">Website URL *</label>
                <input class="form-input" type="text" id="p2_websiteUrl" placeholder="e.g., reequil.com">
            </div>
        </div>

        <h3 style="margin-bottom:16px;">Choose your approach:</h3>
        <div class="path-options">
            <div class="path-option" onclick="showPath2Option('claude')" id="p2opt_claude">
                <div class="po-icon">&#129302;</div>
                <h4>Generate via Claude Code</h4>
                <p>Get a ready-to-copy prompt. Paste it into Claude Code to generate a full CRO audit report with scores, hosted on GitHub Pages.</p>
            </div>
            <div class="path-option" onclick="showPath2Option('worksheet')" id="p2opt_worksheet">
                <div class="po-icon">&#128221;</div>
                <h4>Self-Guided Audit Worksheet</h4>
                <p>Fill in findings as you browse the website. Organized by our 5-component scoring system with real-time score calculation.</p>
            </div>
        </div>

        <!-- Option A: Claude Code Prompt -->
        <div id="p2_claude" style="display:none;">
            <div class="info-box">
                <p><strong>How it works:</strong> Copy the prompt below and paste it into Claude Code. It will browse the website, run PageSpeed tests, check GA4 tracking, evaluate UX, and generate a full professional CRO audit report hosted on GitHub Pages. Once done, come back here and use "I Have a CRO Audit" to upload the report.</p>
            </div>
            <div class="prompt-box">
                <pre id="claudePrompt">Create a CRO audit report for [BRAND].
Website: [URL]</pre>
                <button class="prompt-copy-btn" onclick="copyClaudePrompt(this)">Copy Prompt</button>
            </div>
            <div style="margin-top:16px;">
                <div class="form-row">
                    <div class="form-group">
                        <label class="form-label">Recipient Name</label>
                        <input class="form-input" type="text" id="p2c_recipientName" placeholder="e.g., Rahul">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Sender Name</label>
                        <input class="form-input" type="text" id="p2c_senderName" placeholder="e.g., Naman">
                    </div>
                </div>
                <p style="font-size:13px;color:var(--color-text-muted);margin-bottom:16px;">Or skip the full audit and proceed directly with basic info to generate outreach messages:</p>
                <button class="btn-primary" onclick="proceedFromPath2Claude()">Generate Messages with Basic Info &rarr;</button>
            </div>
        </div>

        <!-- Option B: Self-Guided Worksheet -->
        <div id="p2_worksheet" style="display:none;">
            <div class="info-box">
                <p><strong>Instructions:</strong> Browse the website in another tab and fill in findings below. The form is organized by our 5-component CRO scoring system. Your estimated score updates in real-time as you fill in data.</p>
            </div>

            <div class="form-row" style="margin-bottom:20px;">
                <div class="form-group">
                    <label class="form-label">Recipient Name</label>
                    <input class="form-input" type="text" id="ws_recipientName" placeholder="e.g., Rahul">
                </div>
                <div class="form-group">
                    <label class="form-label">Sender Name</label>
                    <input class="form-input" type="text" id="ws_senderName" placeholder="e.g., Naman">
                </div>
            </div>

            <!-- Component 1: Analytics & Tracking -->
            <div class="ws-section expanded" onclick="toggleWS(this)">
                <div class="ws-header">
                    <h4>&#128202; Analytics & Tracking (25 pts)</h4>
                    <span class="ws-toggle">&#9660;</span>
                </div>
                <div class="ws-body" onclick="event.stopPropagation()">
                    <div class="checkbox-grid">
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_ga4" value="no_ga4"><label for="ws_no_ga4">GA4 not installed</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_gtm" value="no_gtm"><label for="ws_no_gtm">GTM not found</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_ecom_events" value="no_ecom_events"><label for="ws_no_ecom_events">GA4 ecommerce events not firing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_view_item_list" value="no_view_item_list"><label for="ws_no_view_item_list">view_item_list not firing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_view_item" value="no_view_item"><label for="ws_no_view_item">view_item not firing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_add_to_cart_event" value="no_add_to_cart_event"><label for="ws_no_add_to_cart_event">add_to_cart not firing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_begin_checkout" value="no_begin_checkout"><label for="ws_no_begin_checkout">begin_checkout not firing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_purchase_event" value="no_purchase_event"><label for="ws_no_purchase_event">purchase event not verified</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_fb_pixel" value="no_fb_pixel"><label for="ws_no_fb_pixel">Facebook Pixel missing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_clarity" value="no_clarity"><label for="ws_no_clarity">Microsoft Clarity missing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_gads" value="no_gads"><label for="ws_no_gads">Google Ads conversion missing</label></div>
                    </div>
                </div>
            </div>

            <!-- Component 2: Site Performance -->
            <div class="ws-section" onclick="toggleWS(this)">
                <div class="ws-header">
                    <h4>&#9889; Site Performance (20 pts)</h4>
                    <span class="ws-toggle">&#9660;</span>
                </div>
                <div class="ws-body" onclick="event.stopPropagation()">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label">Mobile PageSpeed Score</label>
                            <input class="form-input" type="number" id="ws_mobilePS" placeholder="0-100" min="0" max="100" oninput="updateLiveScore()">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Desktop PageSpeed Score</label>
                            <input class="form-input" type="number" id="ws_desktopPS" placeholder="0-100" min="0" max="100" oninput="updateLiveScore()">
                        </div>
                    </div>
                    <div class="checkbox-grid">
                        <div class="checkbox-item"><input type="checkbox" id="ws_poor_cwv" value="poor_cwv"><label for="ws_poor_cwv">Core Web Vitals failing</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_poor_mobile" value="poor_mobile"><label for="ws_poor_mobile">Poor mobile responsiveness</label></div>
                    </div>
                </div>
            </div>

            <!-- Component 3: SEO -->
            <div class="ws-section" onclick="toggleWS(this)">
                <div class="ws-header">
                    <h4>&#128269; SEO Fundamentals (15 pts)</h4>
                    <span class="ws-toggle">&#9660;</span>
                </div>
                <div class="ws-body" onclick="event.stopPropagation()">
                    <div class="checkbox-grid">
                        <div class="checkbox-item"><input type="checkbox" id="ws_multiple_h1" value="multiple_h1"><label for="ws_multiple_h1">Multiple H1 tags</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_meta_desc" value="no_meta_desc"><label for="ws_no_meta_desc">Missing/poor meta descriptions</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_product_schema" value="no_product_schema"><label for="ws_no_product_schema">No Product schema (JSON-LD)</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_breadcrumb_schema" value="no_breadcrumb_schema"><label for="ws_no_breadcrumb_schema">No Breadcrumb schema</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_og_tags" value="no_og_tags"><label for="ws_no_og_tags">Missing Open Graph tags</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_canonical" value="no_canonical"><label for="ws_no_canonical">Missing/incorrect canonical URL</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_alt_tags" value="no_alt_tags"><label for="ws_no_alt_tags">Missing image alt tags</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_sitemap" value="no_sitemap"><label for="ws_no_sitemap">Missing sitemap.xml</label></div>
                    </div>
                </div>
            </div>

            <!-- Component 4: UX & Usability -->
            <div class="ws-section" onclick="toggleWS(this)">
                <div class="ws-header">
                    <h4>&#127912; UX & Conversion Elements (40 pts)</h4>
                    <span class="ws-toggle">&#9660;</span>
                </div>
                <div class="ws-body" onclick="event.stopPropagation()">
                    <h4 style="margin:0 0 12px;font-size:13px;color:var(--color-text-muted);">Homepage</h4>
                    <div class="checkbox-grid" style="margin-bottom:16px;">
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_value_prop" value="no_value_prop"><label for="ws_no_value_prop">No clear value proposition</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_trust_badges" value="no_trust_badges"><label for="ws_no_trust_badges">No trust badges visible</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_social_proof" value="no_social_proof"><label for="ws_no_social_proof">No social proof</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_sticky_nav" value="no_sticky_nav"><label for="ws_no_sticky_nav">No sticky navigation</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_urgency_hp" value="no_urgency_hp"><label for="ws_no_urgency_hp">No urgency/scarcity elements</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_email_capture" value="no_email_capture"><label for="ws_no_email_capture">No email capture/popup</label></div>
                    </div>
                    <h4 style="margin:0 0 12px;font-size:13px;color:var(--color-text-muted);">Product Page (PDP)</h4>
                    <div class="checkbox-grid" style="margin-bottom:16px;">
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_sticky_atc" value="no_sticky_atc"><label for="ws_no_sticky_atc">No sticky Add to Cart on mobile</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_buy_now" value="no_buy_now"><label for="ws_no_buy_now">No "Buy Now" CTA</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_reviews_pdp" value="no_reviews_pdp"><label for="ws_no_reviews_pdp">No customer reviews section</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_size_chart" value="no_size_chart"><label for="ws_no_size_chart">No size chart</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_urgency_pdp" value="no_urgency_pdp"><label for="ws_no_urgency_pdp">No urgency elements on PDP</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_cross_sell_pdp" value="no_cross_sell_pdp"><label for="ws_no_cross_sell_pdp">No cross-sell on PDP</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_wishlist" value="no_wishlist"><label for="ws_no_wishlist">No wishlist option</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_recently_viewed" value="no_recently_viewed"><label for="ws_no_recently_viewed">No Recently Viewed section</label></div>
                    </div>
                    <h4 style="margin:0 0 12px;font-size:13px;color:var(--color-text-muted);">Cart & Checkout</h4>
                    <div class="checkbox-grid" style="margin-bottom:16px;">
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_quick_add" value="no_quick_add"><label for="ws_no_quick_add">No quick-add on collections</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_cross_sell" value="no_cross_sell"><label for="ws_no_cross_sell">No cross-sell/upsell on cart</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_shipping_bar" value="no_shipping_bar"><label for="ws_no_shipping_bar">No free shipping progress bar</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_checkout_friction" value="checkout_friction"><label for="ws_checkout_friction">Checkout friction (too many steps)</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_guest_checkout" value="no_guest_checkout"><label for="ws_no_guest_checkout">No guest checkout option</label></div>
                        <div class="checkbox-item"><input type="checkbox" id="ws_no_cart_abandonment" value="no_cart_abandonment"><label for="ws_no_cart_abandonment">No cart abandonment tools</label></div>
                    </div>
                </div>
            </div>

            <div class="form-group" style="margin-top:20px;">
                <label class="form-label">Competitor Insights</label>
                <textarea class="form-textarea" id="ws_competitorInsights" placeholder="What do competitors do better? e.g., Nykaa has sticky ATC, Dermaco shows reviews with photos..."></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Additional Notes</label>
                <textarea class="form-textarea" id="ws_additionalNotes" placeholder="Any other findings or context..."></textarea>
            </div>

            <div class="btn-group">
                <button class="btn-primary" onclick="generateFromWorksheet()">Score & Generate Messages &rarr;</button>
            </div>
        </div>
    </div>

    <!-- LIVE SCORE (for worksheet) -->
    <div class="live-score" id="liveScore">
        <div class="live-score-num" id="liveScoreNum">--</div>
        <div class="live-score-txt">CRO Score</div>
    </div>

'''

# Insert Path 2 before the follow-up section
html = html.replace(
    '    <!-- FOLLOW-UP MODE -->',
    path2_html + '    <!-- FOLLOW-UP MODE -->'
)

# ===========================
# 5. ADD SCORE SUMMARY CARD TO OUTPUT SECTION
# ===========================
score_card_html = '''
        <!-- Score Summary Card -->
        <div id="scoreSummaryCard" class="score-summary-card" style="display:none;">
            <div class="score-summary-grid">
                <div class="score-gauge-wrap">
                    <svg width="140" height="140" viewBox="0 0 120 120">
                        <circle cx="60" cy="60" r="52" fill="none" stroke="#e5e7eb" stroke-width="8"/>
                        <circle cx="60" cy="60" r="52" fill="none" stroke-width="8" stroke-linecap="round" transform="rotate(-90 60 60)" stroke-dasharray="326.7" id="scoreCircle" style="stroke-dashoffset:326.7;transition:stroke-dashoffset 1s ease;"/>
                        <text x="60" y="55" text-anchor="middle" font-size="28" font-weight="700" fill="#1d1d20" id="scoreText">--</text>
                        <text x="60" y="72" text-anchor="middle" font-size="11" fill="#5a5a5f">/100</text>
                    </svg>
                    <div class="score-gauge-label">Estimated CRO Score</div>
                </div>
                <div>
                    <div class="score-components" id="scoreComponents"></div>
                    <div class="critical-alerts" id="criticalAlerts"></div>
                </div>
            </div>
        </div>

'''

html = html.replace(
    '        <!-- Output Tabs -->',
    score_card_html + '        <!-- Output Tabs -->'
)

# ===========================
# 6. ADD SCORING ENGINE + SMART BULLETS TO JAVASCRIPT
# (Insert before the FINDING BULLET GENERATION section)
# ===========================
scoring_engine_js = '''
// ============================================
// V2: FINDING REGISTRY & SCORING ENGINE
// ============================================
const FINDING_REGISTRY = {
    no_ga4:              { category: 'Analytics', impactScore: 10, pointsAtStake: 5, criticalRule: 'caps_at_50', label: 'GA4 not installed', emailBullet: "GA4 is not installed \\u2014 you have zero visibility into user behavior or conversion funnel performance. This is the single most critical gap.", whatsappBullet: "\\ud83d\\udcca GA4 not installed \\u2014 zero visibility into your conversion funnel" },
    no_ecom_events:      { category: 'Analytics', impactScore: 10, pointsAtStake: 20, criticalRule: 'caps_at_50', label: 'GA4 ecommerce events not firing', emailBullet: "GA4 ecommerce tracking is not set up \\u2014 you're flying blind on where users drop off. Without this, every marketing rupee is a guess.", whatsappBullet: "\\ud83d\\udcca GA4 ecommerce tracking not set up \\u2014 flying blind on funnel drop-offs" },
    no_gtm:              { category: 'Analytics', impactScore: 7, pointsAtStake: 0, criticalRule: null, label: 'GTM not found', emailBullet: null, whatsappBullet: null },
    no_view_item_list:   { category: 'Analytics', impactScore: 5, pointsAtStake: 4, criticalRule: null, label: 'view_item_list not firing', emailBullet: null, whatsappBullet: null },
    no_view_item:        { category: 'Analytics', impactScore: 5, pointsAtStake: 4, criticalRule: null, label: 'view_item not firing', emailBullet: null, whatsappBullet: null },
    no_add_to_cart_event:{ category: 'Analytics', impactScore: 6, pointsAtStake: 4, criticalRule: null, label: 'add_to_cart not firing', emailBullet: null, whatsappBullet: null },
    no_begin_checkout:   { category: 'Analytics', impactScore: 6, pointsAtStake: 4, criticalRule: null, label: 'begin_checkout not firing', emailBullet: null, whatsappBullet: null },
    no_purchase_event:   { category: 'Analytics', impactScore: 6, pointsAtStake: 4, criticalRule: null, label: 'purchase event not verified', emailBullet: null, whatsappBullet: null },
    no_fb_pixel:         { category: 'Analytics', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'Facebook Pixel missing', emailBullet: null, whatsappBullet: null },
    no_fb_capi:          { category: 'Analytics', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'Facebook CAPI missing', emailBullet: null, whatsappBullet: null },
    no_clarity:          { category: 'Analytics', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'Microsoft Clarity missing', emailBullet: null, whatsappBullet: null },
    no_hotjar:           { category: 'Analytics', impactScore: 2, pointsAtStake: 0, criticalRule: null, label: 'Hotjar missing', emailBullet: null, whatsappBullet: null },
    no_gads:             { category: 'Analytics', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'Google Ads conversion missing', emailBullet: null, whatsappBullet: null },
    no_email_platform:   { category: 'Analytics', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No email platform', emailBullet: null, whatsappBullet: null },
    slow_mobile:         { category: 'Performance', impactScore: 9, pointsAtStake: 10, criticalRule: 'deduct_15', label: 'Poor mobile PageSpeed', emailBullet: null, whatsappBullet: null },
    very_slow_mobile:    { category: 'Performance', impactScore: 10, pointsAtStake: 10, criticalRule: 'deduct_15', label: 'Critical mobile PageSpeed', emailBullet: null, whatsappBullet: null },
    poor_cwv:            { category: 'Performance', impactScore: 7, pointsAtStake: 5, criticalRule: null, label: 'Poor Core Web Vitals', emailBullet: "Core Web Vitals are failing \\u2014 this directly impacts Google rankings and user experience, especially on mobile.", whatsappBullet: "\\u26a1 Core Web Vitals failing \\u2014 hurts Google rankings and mobile UX" },
    poor_mobile:         { category: 'Performance', impactScore: 6, pointsAtStake: 0, criticalRule: null, label: 'Poor mobile responsiveness', emailBullet: null, whatsappBullet: null },
    multiple_h1:         { category: 'SEO', impactScore: 8, pointsAtStake: 3, criticalRule: 'deduct_10_seo', label: 'Multiple H1 tags', emailBullet: "Multiple H1 tags detected \\u2014 this confuses search engines about page hierarchy and can hurt organic rankings.", whatsappBullet: "\\ud83d\\udd0d Multiple H1 tags \\u2014 hurting SEO rankings" },
    no_meta_desc:        { category: 'SEO', impactScore: 5, pointsAtStake: 2, criticalRule: null, label: 'Missing meta descriptions', emailBullet: null, whatsappBullet: null },
    no_product_schema:   { category: 'SEO', impactScore: 7, pointsAtStake: 3, criticalRule: null, label: 'No Product schema', emailBullet: "No Product schema (JSON-LD) \\u2014 you're missing rich snippets in Google results (star ratings, price), which significantly impacts click-through rates.", whatsappBullet: "\\ud83d\\udd0d No Product schema \\u2014 missing rich snippets in Google results" },
    no_breadcrumb_schema:{ category: 'SEO', impactScore: 4, pointsAtStake: 2, criticalRule: null, label: 'No Breadcrumb schema', emailBullet: null, whatsappBullet: null },
    no_og_tags:          { category: 'SEO', impactScore: 3, pointsAtStake: 1, criticalRule: null, label: 'Missing OG tags', emailBullet: null, whatsappBullet: null },
    no_canonical:        { category: 'SEO', impactScore: 5, pointsAtStake: 2, criticalRule: null, label: 'Missing canonical URL', emailBullet: null, whatsappBullet: null },
    no_alt_tags:         { category: 'SEO', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'Missing alt tags', emailBullet: null, whatsappBullet: null },
    no_sitemap:          { category: 'SEO', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'Missing sitemap', emailBullet: null, whatsappBullet: null },
    no_structured_data:  { category: 'SEO', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No structured data', emailBullet: null, whatsappBullet: null },
    no_value_prop:       { category: 'Conversion', impactScore: 7, pointsAtStake: 2, criticalRule: null, label: 'No value proposition', emailBullet: "No clear value proposition on the homepage \\u2014 first-time visitors can't immediately understand why to buy from you vs competitors.", whatsappBullet: "\\ud83c\\udfe0 No clear value proposition \\u2014 visitors don't know why to choose you" },
    no_hero_cta:         { category: 'Conversion', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'Hero missing CTA', emailBullet: null, whatsappBullet: null },
    no_trust_badges:     { category: 'Conversion', impactScore: 7, pointsAtStake: 2, criticalRule: null, label: 'No trust badges', emailBullet: "No trust badges visible \\u2014 this directly impacts purchase confidence, especially for first-time visitors.", whatsappBullet: "\\ud83d\\udee1\\ufe0f No trust badges \\u2014 impacts purchase confidence" },
    no_social_proof:     { category: 'Conversion', impactScore: 7, pointsAtStake: 3, criticalRule: null, label: 'No social proof', emailBullet: "No social proof visible (reviews, logos, testimonials) \\u2014 brands with visible social proof see 15-20% higher conversion rates.", whatsappBullet: "\\u2b50 No social proof visible \\u2014 15-20% conversion impact" },
    no_category_nav:     { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'Poor category nav', emailBullet: null, whatsappBullet: null },
    no_search:           { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'Weak search', emailBullet: null, whatsappBullet: null },
    no_announcement_bar: { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No announcement bar', emailBullet: null, whatsappBullet: null },
    no_email_capture:    { category: 'Conversion', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No email capture', emailBullet: null, whatsappBullet: null },
    no_urgency_hp:       { category: 'Conversion', impactScore: 5, pointsAtStake: 2, criticalRule: null, label: 'No urgency elements', emailBullet: null, whatsappBullet: null },
    no_sticky_nav:       { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No sticky nav', emailBullet: null, whatsappBullet: null },
    no_press_mentions:   { category: 'Conversion', impactScore: 2, pointsAtStake: 0, criticalRule: null, label: 'No press mentions', emailBullet: null, whatsappBullet: null },
    no_sticky_atc:       { category: 'Conversion', impactScore: 9, pointsAtStake: 0, criticalRule: null, label: 'No sticky ATC on mobile', emailBullet: "No sticky Add to Cart on mobile PDPs \\u2014 this one change alone usually improves conversions by 5-7%.", whatsappBullet: "\\ud83d\\uded2 No sticky Add to Cart on mobile \\u2014 usually a 5-7% conversion boost" },
    no_buy_now:          { category: 'Conversion', impactScore: 6, pointsAtStake: 0, criticalRule: null, label: 'No Buy Now CTA', emailBullet: "No 'Buy Now' CTA on the PDP \\u2014 this forces high-intent users through extra steps, reducing impulse purchases.", whatsappBullet: "\\u26a1 No Buy Now CTA \\u2014 extra steps for high-intent buyers" },
    no_size_chart:       { category: 'UX', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'No size chart', emailBullet: null, whatsappBullet: null },
    no_reviews_pdp:      { category: 'Conversion', impactScore: 7, pointsAtStake: 0, criticalRule: null, label: 'No reviews on PDP', emailBullet: "No customer reviews on product pages \\u2014 reviews are the #1 trust signal for online purchases.", whatsappBullet: "\\u2b50 No customer reviews on PDPs \\u2014 #1 trust signal missing" },
    no_image_zoom:       { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No image zoom', emailBullet: null, whatsappBullet: null },
    no_product_video:    { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No product video', emailBullet: null, whatsappBullet: null },
    no_wishlist:         { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No wishlist', emailBullet: null, whatsappBullet: null },
    no_recently_viewed:  { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No Recently Viewed', emailBullet: null, whatsappBullet: null },
    no_product_badges:   { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No product badges', emailBullet: null, whatsappBullet: null },
    no_notify_me:        { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No Notify Me', emailBullet: null, whatsappBullet: null },
    no_emi_bnpl:         { category: 'Conversion', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'No EMI/BNPL', emailBullet: null, whatsappBullet: null },
    no_shipping_info:    { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No shipping info', emailBullet: null, whatsappBullet: null },
    no_return_policy:    { category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No returns policy', emailBullet: null, whatsappBullet: null },
    no_stock_indicator:  { category: 'Conversion', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No stock indicator', emailBullet: null, whatsappBullet: null },
    no_urgency_pdp:      { category: 'Conversion', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'No urgency on PDP', emailBullet: null, whatsappBullet: null },
    no_cross_sell_pdp:   { category: 'Conversion', impactScore: 6, pointsAtStake: 2, criticalRule: null, label: 'No cross-sell on PDP', emailBullet: null, whatsappBullet: null },
    no_quick_add:        { category: 'Conversion', impactScore: 7, pointsAtStake: 0, criticalRule: null, label: 'No quick-add', emailBullet: "No quick-add on collection pages \\u2014 we've seen this boost add-to-cart rates significantly. For TyresNmore, our funnel optimizations drove a 120% increase in user-to-add-to-cart rate.", whatsappBullet: "\\ud83d\\uded2 No quick-add on collections \\u2014 can boost add-to-cart rates significantly" },
    no_cross_sell:       { category: 'Conversion', impactScore: 7, pointsAtStake: 2, criticalRule: null, label: 'No cross-sell on cart', emailBullet: "No product recommendations on the cart page \\u2014 a simple cross-sell setup can lift AOV by 5-10%. We helped a premium Ayurvedic brand increase AOV by 12%.", whatsappBullet: "\\ud83d\\udce6 No cross-sell on cart \\u2014 easy AOV lift of 5-10%" },
    no_shipping_bar:     { category: 'Conversion', impactScore: 6, pointsAtStake: 0, criticalRule: null, label: 'No shipping progress bar', emailBullet: "No free shipping progress bar in cart \\u2014 this simple addition consistently drives higher AOV.", whatsappBullet: "\\ud83d\\ude9a No free shipping progress bar \\u2014 easy AOV driver" },
    no_trust_cart:       { category: 'Conversion', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'No trust in cart', emailBullet: null, whatsappBullet: null },
    no_cart_drawer:      { category: 'UX', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'No cart drawer', emailBullet: null, whatsappBullet: null },
    no_discount_field:   { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No discount field', emailBullet: null, whatsappBullet: null },
    checkout_friction:   { category: 'Conversion', impactScore: 8, pointsAtStake: 3, criticalRule: null, label: 'Checkout friction', emailBullet: "Checkout flow has friction that's likely increasing cart abandonment. 46% peak conversion rate growth for TyresNmore came from systematic CRO including checkout optimization.", whatsappBullet: "\\ud83d\\udd04 Checkout friction \\u2014 streamlining can reduce abandonment significantly" },
    no_guest_checkout:   { category: 'UX', impactScore: 6, pointsAtStake: 0, criticalRule: null, label: 'No guest checkout', emailBullet: "No guest checkout option \\u2014 forcing account creation is one of the top reasons for cart abandonment.", whatsappBullet: "\\ud83d\\udeaa No guest checkout \\u2014 top cart abandonment reason" },
    no_payment_options:  { category: 'UX', impactScore: 5, pointsAtStake: 0, criticalRule: null, label: 'Limited payments', emailBullet: null, whatsappBullet: null },
    no_order_summary:    { category: 'UX', impactScore: 3, pointsAtStake: 0, criticalRule: null, label: 'No order summary', emailBullet: null, whatsappBullet: null },
    no_estimated_delivery:{ category: 'UX', impactScore: 4, pointsAtStake: 0, criticalRule: null, label: 'No delivery date', emailBullet: null, whatsappBullet: null },
    no_cart_abandonment: { category: 'Conversion', impactScore: 5, pointsAtStake: 2, criticalRule: null, label: 'No cart recovery', emailBullet: null, whatsappBullet: null },
    no_tracking:         { category: 'Analytics', impactScore: 8, pointsAtStake: 0, criticalRule: null, label: 'No tracking', emailBullet: null, whatsappBullet: null }
};

function scoreFindingsByImpact(issues, data) {
    const mps = data.mobilePS;
    let activeIssues = issues.filter(issue => {
        if ((issue === 'slow_mobile' || issue === 'very_slow_mobile') && mps !== null && mps >= 70) return false;
        return FINDING_REGISTRY[issue] !== undefined;
    });
    activeIssues.sort((a, b) => (FINDING_REGISTRY[b]?.impactScore || 0) - (FINDING_REGISTRY[a]?.impactScore || 0));
    return activeIssues.map(issue => {
        const reg = FINDING_REGISTRY[issue];
        let priority = 'LOW';
        if (reg.impactScore >= 8) priority = 'HIGH';
        else if (reg.impactScore >= 5) priority = 'MEDIUM';
        return { issue, ...reg, priority };
    });
}

function calculateEstimatedCROScore(issues, data) {
    const mps = data.mobilePS;
    const dps = data.desktopPS;
    let analytics = 25;
    if (issues.includes('no_ga4')) analytics -= 5;
    if (issues.includes('no_ecom_events')) analytics -= 20;
    else {
        ['no_view_item_list','no_view_item','no_add_to_cart_event','no_begin_checkout','no_purchase_event'].forEach(e => { if (issues.includes(e)) analytics -= 4; });
    }
    analytics = Math.max(0, analytics);
    let performance = 15;
    if (mps !== null) { performance = Math.min(10, Math.round(mps / 10)); if (dps !== null) performance += Math.min(5, Math.round(dps / 20)); else performance += 3; if (!issues.includes('poor_cwv')) performance += 3; performance = Math.min(20, performance); }
    else if (issues.includes('poor_cwv') || issues.includes('poor_mobile')) performance = 8;
    let seo = 15;
    if (issues.includes('multiple_h1')) seo -= 3;
    if (issues.includes('no_meta_desc')) seo -= 2;
    if (issues.includes('no_canonical')) seo -= 2;
    if (issues.includes('no_product_schema')) seo -= 3;
    if (issues.includes('no_breadcrumb_schema')) seo -= 2;
    if (issues.includes('no_og_tags')) seo -= 1;
    seo = Math.max(0, seo);
    let ux = 20;
    const uxIssues = issues.filter(i => FINDING_REGISTRY[i]?.category === 'UX');
    ux -= Math.min(14, uxIssues.length * 2);
    ux = Math.max(4, ux);
    let conversion = 20;
    const convIssues = issues.filter(i => FINDING_REGISTRY[i]?.category === 'Conversion');
    convIssues.forEach(i => { conversion -= (FINDING_REGISTRY[i]?.pointsAtStake > 0 ? FINDING_REGISTRY[i].pointsAtStake : 1); });
    conversion = Math.max(0, Math.min(20, conversion));
    let total = analytics + performance + seo + ux + conversion;
    const hasEcomGap = issues.includes('no_ecom_events') || (issues.includes('no_ga4'));
    if (hasEcomGap) total = Math.min(total, 50);
    if (mps !== null && mps < 40) total -= 15;
    total = Math.max(0, Math.min(100, total));
    const alerts = [];
    if (hasEcomGap) alerts.push({ type: 'danger', text: 'GA4 ecommerce tracking missing \\u2014 overall score capped at 50' });
    if (mps !== null && mps < 40) alerts.push({ type: 'danger', text: 'Mobile PageSpeed below 40 \\u2014 15 point deduction applied' });
    if (issues.includes('multiple_h1')) alerts.push({ type: 'warning', text: 'Multiple H1 tags \\u2014 SEO penalty applied' });
    return { overall: total, analytics, performance, seo, ux, conversion, alerts };
}

function generateSmartBullets(data, forWhatsApp) {
    const ranked = scoreFindingsByImpact(data.issues, data);
    const mps = data.mobilePS;
    const bullets = [];
    const max = forWhatsApp ? 4 : 5;
    for (const finding of ranked) {
        if (bullets.length >= max) break;
        const bt = forWhatsApp ? finding.whatsappBullet : finding.emailBullet;
        if (bt) { bullets.push(bt); }
        else if ((finding.issue === 'slow_mobile' || finding.issue === 'very_slow_mobile') && mps !== null && mps < 70) {
            const caseRef = mps < 50 ? " We took Atomberg's page speed scores up by 100% and saw a 362% conversion rate jump as part of a broader CRO program." : '';
            bullets.push(forWhatsApp
                ? '\\ud83d\\udcf1 Mobile speed score is ' + mps + ' \\u2014 ' + (mps < 40 ? 'critically low, fixing this can lift conversions 8-10%' : 'room to improve, typically lifts conversions 5-8%')
                : 'Mobile page speed is at ' + mps + ' \\u2014 getting this to 60-70 typically lifts conversions 8-10%.' + caseRef);
        }
    }
    return bullets;
}

function displayScoreSummary(data) {
    const score = calculateEstimatedCROScore(data.issues, data);
    const card = document.getElementById('scoreSummaryCard');
    card.style.display = 'block';
    // Gauge
    const circle = document.getElementById('scoreCircle');
    const dashoffset = 326.7 * (1 - score.overall / 100);
    circle.style.strokeDashoffset = dashoffset;
    let gaugeColor = '#ef4444';
    if (score.overall >= 70) gaugeColor = '#10b981';
    else if (score.overall >= 50) gaugeColor = '#f59e0b';
    circle.style.stroke = gaugeColor;
    document.getElementById('scoreText').textContent = score.overall;
    // Components
    const comps = [
        { label: 'Analytics & Tracking', score: score.analytics, max: 25 },
        { label: 'Site Performance', score: score.performance, max: 20 },
        { label: 'SEO Fundamentals', score: score.seo, max: 15 },
        { label: 'UX & Usability', score: score.ux, max: 20 },
        { label: 'Conversion Elements', score: score.conversion, max: 20 }
    ];
    const compsEl = document.getElementById('scoreComponents');
    compsEl.innerHTML = comps.map(c => {
        const pct = Math.round((c.score / c.max) * 100);
        let color = '#ef4444'; if (pct >= 70) color = '#10b981'; else if (pct >= 50) color = '#f59e0b';
        return '<div class="comp-row"><span class="comp-label">' + c.label + '</span><div class="comp-track"><div class="comp-fill" style="width:' + pct + '%;background:' + color + '"></div></div><span class="comp-value">' + c.score + '/' + c.max + '</span></div>';
    }).join('');
    // Alerts
    const alertsEl = document.getElementById('criticalAlerts');
    alertsEl.innerHTML = score.alerts.map(a => '<div class="critical-alert ' + a.type + '">\\u26a0\\ufe0f ' + a.text + '</div>').join('');
}

// V2: PATH 2 FUNCTIONS
function showPath2Option(opt) {
    document.getElementById('p2_claude').style.display = opt === 'claude' ? 'block' : 'none';
    document.getElementById('p2_worksheet').style.display = opt === 'worksheet' ? 'block' : 'none';
    document.getElementById('p2opt_claude').classList.toggle('selected', opt === 'claude');
    document.getElementById('p2opt_worksheet').classList.toggle('selected', opt === 'worksheet');
    if (opt === 'worksheet') {
        document.getElementById('liveScore').classList.add('visible');
        updateLiveScore();
    } else {
        document.getElementById('liveScore').classList.remove('visible');
    }
    // Update Claude Code prompt
    if (opt === 'claude') {
        const brand = document.getElementById('p2_brandName').value.trim() || '[BRAND]';
        const url = document.getElementById('p2_websiteUrl').value.trim() || '[URL]';
        document.getElementById('claudePrompt').textContent = 'Create a CRO audit report for ' + brand + '.\\nWebsite: ' + url;
    }
}

function copyClaudePrompt(btn) {
    const text = document.getElementById('claudePrompt').textContent;
    navigator.clipboard.writeText(text).then(() => {
        btn.classList.add('copied'); btn.textContent = 'Copied!';
        setTimeout(() => { btn.classList.remove('copied'); btn.textContent = 'Copy Prompt'; }, 2000);
    });
}

function toggleWS(el) { el.classList.toggle('expanded'); }

function updateLiveScore() {
    const issues = [];
    document.querySelectorAll('#p2_worksheet .checkbox-item input[type="checkbox"]:checked').forEach(cb => issues.push(cb.value));
    const mps = parseInt(document.getElementById('ws_mobilePS').value) || null;
    const dps = parseInt(document.getElementById('ws_desktopPS').value) || null;
    if (mps !== null && mps < 50) issues.push('slow_mobile');
    if (mps !== null && mps < 30) issues.push('very_slow_mobile');
    const score = calculateEstimatedCROScore([...new Set(issues)], { mobilePS: mps, desktopPS: dps });
    const el = document.getElementById('liveScoreNum');
    el.textContent = score.overall;
    let color = '#ef4444'; if (score.overall >= 70) color = '#10b981'; else if (score.overall >= 50) color = '#f59e0b';
    el.style.color = color;
}

function collectWorksheetData() {
    const data = {
        brandName: document.getElementById('p2_brandName').value.trim() || '[Brand Name]',
        websiteUrl: document.getElementById('p2_websiteUrl').value.trim(),
        recipientName: document.getElementById('ws_recipientName').value.trim() || '[Name]',
        senderName: document.getElementById('ws_senderName').value.trim() || '[Your Name]',
        mobilePS: parseInt(document.getElementById('ws_mobilePS').value) || null,
        desktopPS: parseInt(document.getElementById('ws_desktopPS').value) || null,
        industry: '',
        competitorInsights: document.getElementById('ws_competitorInsights').value.trim(),
        additionalNotes: document.getElementById('ws_additionalNotes').value.trim(),
        issues: []
    };
    document.querySelectorAll('#p2_worksheet .checkbox-item input[type="checkbox"]:checked').forEach(cb => data.issues.push(cb.value));
    if (data.mobilePS !== null && data.mobilePS < 50) data.issues.push('slow_mobile');
    if (data.mobilePS !== null && data.mobilePS < 30) data.issues.push('very_slow_mobile');
    data.issues = [...new Set(data.issues)];
    return data;
}

function generateFromWorksheet() {
    const data = collectWorksheetData();
    if (data.issues.length === 0 && !data.mobilePS) { showToast('Please select at least some findings.'); return; }
    window._lastGeneratedData = data;
    const email = generateEmail(data);
    const whatsapp = generateWhatsApp(data);
    document.getElementById('emailSubject').textContent = 'Subject: ' + email.subject;
    document.getElementById('emailBody').textContent = email.body;
    document.getElementById('whatsappBody').textContent = whatsapp;
    window._emailFull = 'Subject: ' + email.subject + '\\n\\n' + email.body;
    window._whatsappFull = whatsapp;
    displayScoreSummary(data);
    const followups = generateFollowUpSequence(data);
    renderFollowupCards(followups);
    window._followups = followups;
    document.getElementById('liveScore').classList.remove('visible');
    showSection('outputSection');
    showToast('Messages generated from worksheet!');
}

function proceedFromPath2Claude() {
    const data = {
        brandName: document.getElementById('p2_brandName').value.trim() || '[Brand Name]',
        websiteUrl: document.getElementById('p2_websiteUrl').value.trim(),
        recipientName: document.getElementById('p2c_recipientName').value.trim() || '[Name]',
        senderName: document.getElementById('p2c_senderName').value.trim() || '[Your Name]',
        mobilePS: null, desktopPS: null, industry: '', competitorInsights: '', additionalNotes: '', issues: []
    };
    if (!data.brandName || data.brandName === '[Brand Name]') { showToast('Please enter a brand name.'); return; }
    window._lastGeneratedData = data;
    const email = generateEmail(data);
    const whatsapp = generateWhatsApp(data);
    document.getElementById('emailSubject').textContent = 'Subject: ' + email.subject;
    document.getElementById('emailBody').textContent = email.body;
    document.getElementById('whatsappBody').textContent = whatsapp;
    window._emailFull = 'Subject: ' + email.subject + '\\n\\n' + email.body;
    window._whatsappFull = whatsapp;
    document.getElementById('scoreSummaryCard').style.display = 'none';
    const followups = generateFollowUpSequence(data);
    renderFollowupCards(followups);
    window._followups = followups;
    showSection('outputSection');
    showToast('Basic messages generated!');
}

function renderFollowupCards(followups) {
    const cardsContainer = document.getElementById('followupCards');
    cardsContainer.innerHTML = '';
    followups.forEach((msg, i) => {
        const card = document.createElement('div');
        card.className = 'followup-card';
        card.innerHTML = '<div class="followup-card-header"><span class="followup-card-title">' + msg.title + '</span><span class="followup-timing">' + msg.timing + '</span></div><div class="followup-panels"><div class="followup-panel"><div class="followup-panel-label">Email</div><div class="followup-text">' + escapeHtml(msg.email) + '</div><button class="copy-btn" onclick="copyDirect(this,' + i + ',\\'email\\')" style="margin-top:8px;">Copy Email</button></div><div class="followup-panel"><div class="followup-panel-label">WhatsApp</div><div class="followup-text">' + escapeHtml(msg.whatsapp) + '</div><button class="copy-btn" onclick="copyDirect(this,' + i + ',\\'whatsapp\\')" style="margin-top:8px;">Copy WhatsApp</button></div></div>';
        cardsContainer.appendChild(card);
    });
}

// Worksheet checkbox listener for live score
document.addEventListener('change', function(e) {
    if (e.target.closest('#p2_worksheet') && e.target.type === 'checkbox') updateLiveScore();
});

'''

# Insert the scoring engine before the FINDING BULLET GENERATION section
html = html.replace(
    '// ============================================\n// FINDING BULLET GENERATION\n// ============================================',
    scoring_engine_js + '// ============================================\n// FINDING BULLET GENERATION (V1 LEGACY - kept for compatibility)\n// ============================================'
)

# ===========================
# 7. UPDATE generateEmail and generateWhatsApp to use smart bullets
# ===========================
# Replace generateFindingBullets call in generateEmail with generateSmartBullets
html = html.replace(
    'function generateEmail(data) {\n    const bullets = generateFindingBullets(data, false);',
    'function generateEmail(data) {\n    const bullets = generateSmartBullets(data, false);'
)
html = html.replace(
    'function generateWhatsApp(data) {\n    const bullets = generateFindingBullets(data, true);',
    'function generateWhatsApp(data) {\n    const bullets = generateSmartBullets(data, true);'
)

# ===========================
# 8. ADD SMART LANGUAGE TO EMAIL BASED ON SCORE
# ===========================
html = html.replace(
    "I took a quick look at ${brandType} and spotted a few things that are likely leaving revenue on the table:",
    "${data.issues.length > 0 ? ((() => { const s = calculateEstimatedCROScore(data.issues, data); return s.overall < 40 ? 'I took a quick look at ' + brandType + ' and spotted some critical gaps that are likely costing significant revenue:' : s.overall < 60 ? 'I took a quick look at ' + brandType + ' and spotted a few high-impact opportunities that could meaningfully move your conversion numbers:' : 'I took a quick look at ' + brandType + ' and spotted some quick wins that could push your results even further:'; })()) : 'I took a quick look at ' + brandType + ' and spotted a few things that could improve your conversion numbers:'}"
)

# ===========================
# 9. UPDATE generateMessages and generateFromFlowA to show score card
# ===========================
html = html.replace(
    "    // Show output section\n    showSection('outputSection');\n    showToast('Messages generated successfully!');",
    "    // Show score summary\n    if (data.issues.length > 0) displayScoreSummary(data);\n    else document.getElementById('scoreSummaryCard').style.display = 'none';\n    // Show output section\n    showSection('outputSection');\n    showToast('Messages generated successfully!');"
)

html = html.replace(
    "    showSection('outputSection');\n    showToast('Messages generated from uploaded report!');",
    "    // Show score summary\n    if (data.issues.length > 0) displayScoreSummary(data);\n    else document.getElementById('scoreSummaryCard').style.display = 'none';\n    showSection('outputSection');\n    showToast('Messages generated from uploaded report!');"
)

# ===========================
# 10. REFACTOR followup card rendering to use shared function
# ===========================
# Replace the inline followup card rendering in generateMessages with renderFollowupCards
old_followup_render = """    followups.forEach((msg, i) => {
        const card = document.createElement('div');
        card.className = 'followup-card';
        card.innerHTML = `
            <div class="followup-card-header">
                <span class="followup-card-title">${msg.title}</span>
                <span class="followup-timing">${msg.timing}</span>
            </div>
            <div class="followup-panels">
                <div class="followup-panel">
                    <div class="followup-panel-label">Email</div>
                    <div class="followup-text">${escapeHtml(msg.email)}</div>
                    <button class="copy-btn" onclick="copyDirect(this, ${i}, 'email')" style="margin-top:8px;">Copy Email</button>
                </div>
                <div class="followup-panel">
                    <div class="followup-panel-label">WhatsApp</div>
                    <div class="followup-text">${escapeHtml(msg.whatsapp)}</div>
                    <button class="copy-btn" onclick="copyDirect(this, ${i}, 'whatsapp')" style="margin-top:8px;">Copy WhatsApp</button>
                </div>
            </div>
        `;
        cardsContainer.appendChild(card);
    });"""

# There are 2 occurrences of this pattern - replace both with renderFollowupCards
new_followup_render = "    renderFollowupCards(followups);"

# First occurrence (in generateMessages)
html = html.replace(
    """    const cardsContainer = document.getElementById('followupCards');
    cardsContainer.innerHTML = '';

""" + old_followup_render,
    new_followup_render
)

# Second occurrence (in generateFromFlowA) - find it
html = html.replace(
    """    const cardsContainer = document.getElementById('followupCards');
    cardsContainer.innerHTML = '';
    followups.forEach((msg, i) => {
        const card = document.createElement('div');
        card.className = 'followup-card';
        card.innerHTML = `
            <div class="followup-card-header">
                <span class="followup-card-title">${msg.title}</span>
                <span class="followup-timing">${msg.timing}</span>
            </div>
            <div class="followup-panels">
                <div class="followup-panel">
                    <div class="followup-panel-label">Email</div>
                    <div class="followup-text">${escapeHtml(msg.email)}</div>
                    <button class="copy-btn" onclick="copyDirect(this, ${i}, 'email')" style="margin-top:8px;">Copy Email</button>
                </div>
                <div class="followup-panel">
                    <div class="followup-panel-label">WhatsApp</div>
                    <div class="followup-text">${escapeHtml(msg.whatsapp)}</div>
                    <button class="copy-btn" onclick="copyDirect(this, ${i}, 'whatsapp')" style="margin-top:8px;">Copy WhatsApp</button>
                </div>
            </div>
        `;
        cardsContainer.appendChild(card);
    });""",
    "    renderFollowupCards(followups);"
)

# Write the final file
with open(OUTPUT_PATH, 'w') as f:
    f.write(html)

# Count lines
line_count = html.count('\n') + 1
print(f"V2 file written: {len(html)} chars, ~{line_count} lines")
print(f"Output: {OUTPUT_PATH}")
