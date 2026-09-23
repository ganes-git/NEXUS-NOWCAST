"""
Generate Black-and-White Charts for NEXUS-NOWCAST Technical Report
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUTPUT_DIR = r"c:\Users\ganes\Desktop\PS72\scratch_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set global black & white / grayscale aesthetics
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 10,
    'text.color': '#000000',
    'axes.labelcolor': '#000000',
    'xtick.color': '#000000',
    'ytick.color': '#000000',
    'axes.edgecolor': '#000000',
    'axes.linewidth': 1.2,
    'grid.color': '#cccccc',
    'grid.linestyle': '--',
    'grid.linewidth': 0.7,
    'figure.facecolor': '#ffffff',
    'axes.facecolor': '#ffffff'
})

# 1. Dynamic 0-6h Blending Curve Figure
def make_blending_curve():
    t = np.linspace(0, 360, 500)
    tau = 120.0
    w_radar = np.exp(-t / tau)
    w_nwp = 1.0 - w_radar

    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=300)
    ax.plot(t, w_radar * 100, color='#000000', linewidth=2.2, linestyle='-', label='Radar Kinematic Advection Weight $W_{radar}(t)$')
    ax.plot(t, w_nwp * 100, color='#555555', linewidth=2.0, linestyle='--', label='NWP Thermodynamic CAPE Weight $W_{NWP}(t)$')
    
    # 2-hour radar wall line
    ax.axvline(x=120, color='#000000', linestyle=':', linewidth=1.5)
    ax.annotate('The 2-Hour Radar Wall\n($t = 120$ min, Transition Point)', xy=(120, 50), xytext=(145, 60),
                arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
                fontsize=9, fontweight='bold', bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#000000", lw=1))
    
    ax.set_title('Dynamic Lead-Time Blending Curve (0 to 6 Hours)', fontsize=11, fontweight='bold', pad=10)
    ax.set_xlabel('Forecast Lead Time $\\Delta t$ (minutes)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Blending Contribution Weight (%)', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 105)
    ax.set_xticks([0, 30, 60, 90, 120, 180, 240, 300, 360])
    ax.set_xticklabels(['0m', '+30m', '+1h', '+1.5h', '+2h', '+3h', '+4h', '+5h', '+6h'])
    ax.grid(True)
    ax.legend(loc='center right', framealpha=1.0, edgecolor='#000000')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_blending_curve.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)

# 2. Operational Lightning Jump Detection
def make_lightning_jump():
    time_min = np.arange(0, 65, 5)
    # Baseline flash rate gradually rising then surging at t=45m
    fr = np.array([8.0, 9.2, 10.5, 11.2, 12.0, 13.5, 14.8, 16.0, 18.5, 38.5, 46.0, 42.0, 35.0])
    
    fig, ax1 = plt.subplots(figsize=(7, 3.8), dpi=300)
    
    ax1.plot(time_min, fr, color='#000000', marker='s', markersize=4.5, linewidth=1.8, label='Calibrated Flash Rate (flashes/min)')
    ax1.axvline(x=45, color='#333333', linestyle=':', linewidth=1.5)
    ax1.annotate('2-Sigma Lightning Jump Trigger\n$J(t) = +2.4\\sigma$ ($DFR = +20.0$ fl/min)\n15-30 min warning for CG strikes', 
                xy=(45, 38.5), xytext=(10, 36),
                arrowprops=dict(facecolor='black', shrink=0.08, width=1, headwidth=5),
                fontsize=8.5, fontweight='bold', bbox=dict(boxstyle="square,pad=0.3", fc="#ffffff", ec="#000000", lw=1))
    
    ax1.set_title('Operational 2-Sigma Lightning Jump Detection Surge', fontsize=11, fontweight='bold', pad=10)
    ax1.set_xlabel('Observation Timeline (minutes)', fontsize=10, fontweight='bold')
    ax1.set_ylabel('Total Flash Rate (flashes/min)', fontsize=10, fontweight='bold')
    ax1.set_xlim(0, 60)
    ax1.set_ylim(0, 52)
    ax1.grid(True)
    ax1.legend(loc='upper left', framealpha=1.0, edgecolor='#000000')
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_lightning_jump.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)

# 3. Contingency Verification Scores across Lead Times
def make_contingency_scores():
    lead_times = ['1-Hour Lead', '3-Hour Lead', '6-Hour Lead']
    csi = [0.641, 0.468, 0.312]
    pod = [0.840, 0.739, 0.636]
    far = [0.270, 0.390, 0.484]
    ets = [0.582, 0.401, 0.245]

    x = np.arange(len(lead_times))
    width = 0.18

    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=300)
    ax.bar(x - 1.5*width, csi, width, label='CSI (Critical Success)', color='#000000', edgecolor='#000000')
    ax.bar(x - 0.5*width, pod, width, label='POD (Detection Prob)', color='#555555', edgecolor='#000000')
    ax.bar(x + 0.5*width, far, width, label='FAR (False Alarm)', color='#aaaaaa', edgecolor='#000000')
    ax.bar(x + 1.5*width, ets, width, label='ETS (Equitable Threat)', color='#ffffff', edgecolor='#000000', hatch='//')

    ax.set_title('Meteorological Verification Contingency Scores Across Lead Times', fontsize=11, fontweight='bold', pad=10)
    ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(lead_times, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.axhline(0.35, color='#444444', linestyle=':', label='IMD Operational CSI Target (0.35)')
    ax.legend(loc='upper right', framealpha=1.0, edgecolor='#000000', fontsize=8.5)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_contingency_scores.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)

# 4. System Block Diagram (Black and White)
def make_architecture_diagram():
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    ax.axis('off')

    # Draw boxes
    boxes = [
        ("MULTI-SENSOR INGESTION\n• Radar DWR (1 km, 10 min)\n• INSAT-3D Sat (4 km, 15 min)\n• Lightning Strike Stream\n• NWP GFS/WRF (25 km, 6 hr)", (0.05, 0.65, 0.40, 0.30)),
        ("HETEROGENEOUS GRAPH\nCONSTRUCTOR (HGC)\n• Radar superpixel nodes\n• Satellite cloud ROIs\n• Lightning DBSCAN clusters\n• NWP instability grid nodes", (0.55, 0.65, 0.40, 0.30)),
        ("PHYSICS-INFORMED EDGES\n• 700 hPa Wind Steering Vectors\n• CAPE Convective Gradients\n• Split-Window Column Attention", (0.05, 0.28, 0.40, 0.25)),
        ("STGAT-PIE NEURAL ENGINE\n• Dynamic GATv2 Multi-Head Attention\n• GConvGRU Temporal Recurrence\n• Physics Advection Loss Constraint", (0.55, 0.28, 0.40, 0.25)),
        ("DISASTER OUTPUTS & CIVIL DEFENSE\n• 0-6h Blended Reflectivity & Strike Forecasts • ITU X.1303 / NDMA CAP v1.2 XML\n• Tactical Leaflet GIS C2 HUD • Pre-Radar Convective Initiation & 2-Sigma Lightning Jump Alerts", (0.05, 0.02, 0.90, 0.18))
    ]

    for title, (x, y, w, h) in boxes:
        rect = plt.Rectangle((x, y), w, h, facecolor='#ffffff', edgecolor='#000000', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=8, fontweight='bold', linespacing=1.3)

    # Arrows
    arrow_args = dict(facecolor='black', width=1.2, headwidth=6, shrink=0.08)
    ax.annotate('', xy=(0.55, 0.80), xytext=(0.45, 0.80), arrowprops=arrow_args)
    ax.annotate('', xy=(0.25, 0.53), xytext=(0.25, 0.65), arrowprops=arrow_args)
    ax.annotate('', xy=(0.75, 0.53), xytext=(0.75, 0.65), arrowprops=arrow_args)
    ax.annotate('', xy=(0.55, 0.40), xytext=(0.45, 0.40), arrowprops=arrow_args)
    ax.annotate('', xy=(0.50, 0.20), xytext=(0.50, 0.28), arrowprops=arrow_args)

    ax.set_title('NEXUS-NOWCAST: STGAT-PIE End-to-End System Architecture', fontsize=11, fontweight='bold', pad=12)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_system_architecture.png")
    plt.savefig(path)
    plt.close()
    print("Saved:", path)

if __name__ == '__main__':
    make_blending_curve()
    make_lightning_jump()
    make_contingency_scores()
    make_architecture_diagram()
    print("All charts successfully generated!")
