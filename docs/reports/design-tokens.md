# Design Tokens — Locked Typography & Spacing System
**Project**: NEXUS-NOWCAST (SIH26072)
**Authority**: uiux-spec.md + Phase 2-3 of styling cleanup pass

---

## Phase 2 — Locked Typography Scale

Exactly **5 sizes**. Every text element maps to one of these; no one-off sizes anywhere.

| Token | Size / Weight | Line-Height | Font Family | Usage |
|-------|---------------|-------------|-------------|-------|
| `--type-heading-lg` | 18px / 700 | 24px | Inter | Brand title, large section headers |
| `--type-heading-md` | 14px / 700 | 20px | Inter | Card titles, modal headers, alert h3, metric values (via mono override) |
| `--type-body`       | 13px / 500 | 20px | Inter | Body text, descriptions, dropdown labels, blending desc |
| `--type-caption`    | 11px / 600 | 16px | Inter | Labels, badges, ticks, HUD rows, button text, card-title, telemetry-label |
| `--type-metric`     | 20px / 700 | 24px | JetBrains Mono | Live telemetry readouts (dBZ, σ, CI score), timeline readout-value |

**Eliminated one-off sizes:**
- `.metric-num` was 16px → now `--type-heading-md` (14px, mono override)
- `.readout-value` was 18px → now `--type-metric` (20px)
- `modal-body pre` font-size remains 11px — maps to `caption` size, using mono family ✓

---

## Phase 3 — Locked Spacing System

**Base unit: 4px.** All spacing values are multiples.

| Token | Value | Usage |
|-------|-------|-------|
| `--space-1` |  4px | Micro gaps: badge padding, icon offsets |
| `--space-2` |  8px | Gap between label+value pairs, tag gaps |
| `--space-3` | 12px | Internal card padding (compact), clock/button padding |
| `--space-4` | 16px | Card padding, section gaps, header padding |
| `--space-5` | 20px | (Reserved for future use) |
| `--space-6` | 24px | (Reserved for large section separators) |

**Alignment rules applied:**
- Sidebar cards: left-aligned labels, right-aligned values — consistent throughout
- Header controls: all vertically center-aligned, gap=`--space-3`
- Timeline bar: items aligned center, gap=`--space-4` between groups
- HUD overlay: flex column, gap=6px between rows
- No mixed centering and left-alignment within the same component

---

## Color Palette (From uiux-spec.md — unchanged)

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-canvas`         | `#f1f5f9` | Main canvas |
| `--bg-surface`        | `#ffffff` | Cards |
| `--bg-surface-subtle` | `#f8fafc` | Inset telemetry boxes |
| `--bg-header`         | `#0f172a` | Top bar |
| `--accent-emerald`    | `#059669` | Primary accent (online, active, radar) |
| `--accent-amber`      | `#d97706` | NWP / CAPE / warning |
| `--accent-red`        | `#dc2626` | RED alert / lightning surge |
| `--accent-magenta`    | `#c026d3` | Catastrophic core / hail |
| `--text-primary`      | `#0f172a` | Headings, values |
| `--text-secondary`    | `#475569` | Descriptions, labels |
| `--text-muted`        | `#64748b` | Units, ticks, inactive |

**Zero blue, zero cyan confirmed** — palette contains no hue in the 180°–240° range.
