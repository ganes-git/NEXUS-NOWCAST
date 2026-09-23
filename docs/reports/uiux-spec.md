# UI/UX Specification: Mission Control Meteorological HUD
## Multi-Sensor Thunderstorm & Lightning Nowcasting Platform
**Problem Statement**: SIH26072 | Ministry of Earth Sciences (MoES) / IMD

---

### 1. Visual Design Tokens & Palette (Strictly No Blue / No Cyan)

Ultra-premium tactical meteorological mission-control dark palette designed for zero eye strain in 24/7 emergency control rooms, completely devoid of blue and cyan tones:

| Token | Hex / RGBA Value | Semantic Usage |
|---|---|---|
| `--bg-dark` | `#08090c` | Deep neutral obsidian / carbon black background |
| `--bg-surface` | `#0e0f14` | Matte graphite surface |
| `--panel-bg` | `rgba(16, 18, 24, 0.88)` | High-tech glassmorphic card surface with 20px blur |
| `--panel-border` | `rgba(255, 255, 255, 0.08)` | Thin precision hairline boundary lines |
| `--panel-border-hover` | `rgba(16, 185, 129, 0.35)` | Emerald boundary glow on hover |
| `--accent-primary` | `#10b981` | Neon Emerald Green: radar telemetry, online status, active controls |
| `--accent-green` | `#22c55e` | Light rain reflectivity (15–25 dBZ), normal status |
| `--accent-yellow` | `#ffd600` | Moderate thunderstorm (35–42 dBZ), advisory alerts |
| `--accent-amber` | `#f59e0b` | Heavy convection (42–50 dBZ), CAPE gradients, NWP progress |
| `--accent-red` | `#ff1744` | Severe storm core (>50 dBZ), Lightning Jump, RED civil warnings |
| `--accent-magenta` | `#d500f9` | Catastrophic hail core (>60 dBZ) |
| `--text-primary` | `#f8fafc` | High-contrast white for primary numbers and headings |
| `--text-secondary` | `#94a3b8` | Cool metallic silver for units, metrics, and secondary labels |
| `--text-muted` | `#64748b` | Muted charcoal for ticks and inactive elements |

### 2. Typography Constraints
- **Primary Interface Font**: `Inter`, sans-serif (weights: 400, 500, 600, 700, 800).
- **Telemetry & Timestamp Font**: `JetBrains Mono`, monospace (weights: 500, 700) for numeric readouts, dBZ values, coordinates, and CAP IDs.

### 3. Layout Architecture
1. **Top Application Bar**:
   - Fixed height 64px, brand title, corridor selector (Delhi NCR, Kolkata, Chennai, Mumbai), live engine status pill, XAI attention toggle, and NDMA CAP XML export action button.
2. **Main Split Layout**:
   - **Left Sidebar (380px)**: Active Civil Protection Alert card, Convective Core Telemetry grid, Dynamic Blending weight gauge, and Model Skill Verification contingency scores.
   - **Center/Right Map Viewport**: High-performance local Canvas & vector GIS map with 0ms network latency.
3. **Tactical Map HUD Overlay (Top-Right of Map)**:
   - Live mouse coordinate tracker (`LAT: ...°N | LON: ...°E`), DWR station status, and interactive layer toggles (`[RINGS]`, `[RADIALS]`, `[BOUNDARIES]`).
4. **Bottom Floating Timeline HUD**:
   - 0 to 360 minute (0–6 hour) scrubbing slider with 15-minute intervals, play/pause animation, and dynamic blend indicator showing Radar vs. NWP balance.
