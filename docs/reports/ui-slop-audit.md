# UI Slop Audit — Phase 1 Findings
**Project**: NEXUS-NOWCAST (SIH26072 / MoES-IMD)
**Scope**: Single-screen operational HUD (index.html + style.css + app.js)
**Date**: 2026-09-20

---

## Screen: Main Operational HUD (the only screen)

| # | Violation | Location | Severity |
|---|-----------|----------|----------|
| 1 | **Wrong font loaded** — `uiux-spec.md` mandates `Inter` but `<link>` loads `Plus Jakarta Sans`. One-off deviation from spec, invisible but foundational. | `index.html` `<head>` | **High** |
| 2 | **Decorative `<span class="pulse-ring">` element** — CSS-animated ring on brand logo. No PRD feature behind it; purely decorative AI-slop flourish. | `index.html` brand-logo | **High** |
| 3 | **Inaccurate map style labels** — Dropdown options read "Dark Tactical OSM (Zero Blue)" and "Monochrome OSM (Zero Blue)" but the map IS already the standard light OSM. The label contradicts the actual visual. | `index.html` `#mapStyleSelect` | **Medium** |
| 4 | **One-off font size on `.metric-num`** — Set to `font-size: 16px` in isolation instead of mapping to any scale step. Two elements with headings at different sizes. | `style.css` `.metric-num` | **Medium** |
| 5 | **One-off font size on `.readout-value`** — Set to `font-size: 18px`, also not in the declared scale. | `style.css` `.readout-value` | **Medium** |
| 6 | **Excessive decorative `box-shadow`** on `.modal-box` — `0 8px 30px rgba(0,0,0,0.2)` is heavier than warranted; modal is a functional element, 4px is sufficient. | `style.css` `.modal-box` | **Low** |
| 7 | **`.pulse-ring` CSS class exists** — Animation keyframes for a decorative pulse with no functional purpose tied to any PRD story. | `style.css` (implied via element) | **Low** |

**No violations found for:**
- Color palette (no blue/cyan present once `pulse-ring` removed)
- Glassmorphism/neumorphism (none used)
- Stock hero graphics / particle effects (none)
- Emoji used as icons (none)
- Filler stats / placeholder copy (all values trace to schema.md/PRD)
- Inconsistent spacing (8px grid applied throughout)
- Gradient abuse (only the functional dBZ legend bar uses a gradient — acceptable)
