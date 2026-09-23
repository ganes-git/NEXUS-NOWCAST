# Technical Requirements Document (TRD)
## NEXUS-NOWCAST: Mathematical Architecture & Engineering Specifications
**Problem Statement ID**: SIH26072 | **Ministry of Earth Sciences (MoES)**  
**Official PS Title**: *"AIML based Nowcasting of thunderstorm and lightning using atmospheric observation including multiple radars, satellite, lightning and model data."*  
**Core Framework**: STGAT-PIE (Spatio-Temporal Graph Attention Network with Physics-Informed Edges)

---

## 1. Mathematical Architecture & Graph Formalism

### 1.1 The Heterogeneous Atmospheric Observation Graph $\mathcal{G}_t = (\mathcal{V}_t, \mathcal{E}_t)$
Rather than coercing spherical and irregular atmospheric observations onto a rigid 2D grid, our AIML based engine defines a dynamic heterogeneous graph at each 10-minute epoch $t$:

$$\mathcal{V}_t = \mathcal{V}_t^{\text{radars}} \cup \mathcal{V}_t^{\text{sat}} \cup \mathcal{V}_t^{\text{light}} \cup \mathcal{V}_t^{\text{model}}$$

#### A. Multiple Radars Network Nodes & Mosaicking $\mathcal{V}_t^{\text{radars}}$
- Ingests polar/Cartesian volumes across **multiple radars** (India's 37-station IMD DWR network) without resampling onto a lossy uniform grid.
- Each radar station $s \in \mathcal{S}$ is segmented via Simple Linear Iterative Clustering (SLIC) superpixels at native beam elevations $\theta_k$.
- 3D Beam Height calculation with 4/3 Earth radius approximation:
  $$h(r, \theta) = r \sin\theta + \frac{r^2}{2 k_e R_E}, \quad k_e = \frac{4}{3}, \, R_E = 6371\text{ km}$$
- **Multi-Radar Mosaic & Overlap Reconciliation**: Where multiple radar stations have overlapping coverage (e.g., DWR Delhi Palam and DWR Patiala; DWR Kolkata and DWR Paradeep):
  $$Z_{\text{composite}}(\mathbf{p}) = \max_{s \in \mathcal{S}_{\mathbf{p}}} \left[ Z_s(\mathbf{p}) \cdot \omega_{\text{range}}(r_s) \cdot \omega_{\text{blockage}}(s, \mathbf{p}) \right]$$
  Where $\omega_{\text{range}}(r) = \exp(-r / 250\text{ km})$ and $\omega_{\text{blockage}}$ mitigates terrain beam blockage.
- Each node $v_i \in \mathcal{V}_t^{\text{radars}}$ carries feature vector:
  $$\mathbf{x}_i^{\text{radar}} = \left[ \bar{Z}_H, \bar{V}_r, \sigma_{V}, Z_{\text{max}}, \Delta Z / \Delta t, \text{lat}, \text{lon}, \text{alt}, \text{station\_id} \right]^T \in \mathbb{R}^9$$

#### B. Satellite Nodes $\mathcal{V}_t^{\text{sat}}$
- Generated from INSAT-3D thermal IR and water vapor bands using adaptive cloud-top temperature thresholding ($T_B < 240\text{ K}$).
  $$\mathbf{x}_j^{\text{sat}} = \left[ BT_{10.8}, BT_{12.0}, BT_{6.7}, (BT_{10.8} - BT_{12.0}), (BT_{6.7} - BT_{10.8}), \frac{dBT_{10.8}}{dt} \right]^T \in \mathbb{R}^6$$

#### C. Lightning Nodes $\mathcal{V}_t^{\text{light}}$
- Clusters formed via Density-Based Spatial Clustering of Applications with Noise (DBSCAN) on lightning strike coordinates over $[t-10\text{m}, t]$ ($\epsilon = 12\text{ km}$, $\text{min\_pts} = 3$).
  $$\mathbf{x}_k^{\text{light}} = \left[ N_{\text{strikes}}, \text{FlashRate}, \bar{I}_{\text{peak}}, \text{PolarityRatio}, \Delta \text{FR}_{10\text{m}} \right]^T \in \mathbb{R}^5$$

#### D. NWP Thermodynamic Nodes $\mathcal{V}_t^{\text{nwp}}$
- Sampled at 25 km mesoscale grid points from operational GFS/WRF forecasts.
  $$\mathbf{x}_l^{\text{nwp}} = \left[ \text{CAPE}, \text{CIN}, \text{BulkShear}_{0-6\text{km}}, \text{PWAT}, U_{700}, V_{700} \right]^T \in \mathbb{R}^6$$

---

### 1.2 Physics-Informed Edge Formulation $\mathcal{E}_t$

Edges connect nodes across modalities based on atmospheric mechanics rather than naive geometric proximity:

1. **Wind Advection Edges ($e_{ij}^{\text{wind}}$)**:
   Connect node $i$ to node $j$ along the 700 hPa steering wind vector $\mathbf{v}_{\text{wind}} = (U_{700}, V_{700})$:
   $$w_{ij}^{\text{wind}} = \exp\left( -\frac{\|\mathbf{p}_j - (\mathbf{p}_i + \mathbf{v}_{\text{wind}} \cdot \Delta t)\|^2}{2\sigma_d^2} \right)$$
2. **CAPE-Gradient Convective Edges ($e_{ij}^{\text{cape}}$)**:
   Connect nodes along the maximum spatial gradient of atmospheric instability:
   $$\mathbf{w}_{ij}^{\text{cape}} = \max(0, \nabla \text{CAPE} \cdot \hat{\mathbf{u}}_{ij})$$
3. **Cross-Modal Teleconnection Edges ($e_{ij}^{\text{cross}}$)**:
   Connect satellite cloud-top cooling nodes to underlying radar superpixels and lightning strike clusters within the radar beam column.

---

## 2. STGAT-PIE Neural Engine Mechanics

### 2.1 Spatial Message Passing: GATv2 with Heterogeneous Attention
At timestep $t$, spatial feature representations are updated using dynamic attention coefficients:

$$\mathbf{h}_i^{(l)} = \sigma \left( \sum_{j \in \mathcal{N}(i)} \alpha_{ij}^{(l)} \mathbf{W}_v \mathbf{h}_j^{(l-1)} \right)$$

Where the attention score $\alpha_{ij}$ is computed with dynamic multi-head GATv2:

$$\alpha_{ij} = \frac{\exp\left( \mathbf{a}^T \text{LeakyReLU}\left( \mathbf{W}_s [\mathbf{h}_i \,\|\, \mathbf{h}_j \,\|\, \mathbf{e}_{ij}] \right) \right)}{\sum_{k \in \mathcal{N}(i)} \exp\left( \mathbf{a}^T \text{LeakyReLU}\left( \mathbf{W}_s [\mathbf{h}_i \,\|\, \mathbf{h}_k \,\|\, \mathbf{e}_{ik}] \right) \right)}$$

Here $\mathbf{e}_{ij}$ encodes the physical edge features (wind velocity vector, CAPE gradient, and distance decay).

### 2.2 Temporal Dynamics: Graph Convolutional Gated Recurrent Unit (GConvGRU)
To model cell evolution across $T=12$ history steps (2 hours at 10-min cadence):

$$\mathbf{r}_t = \sigma\left( \mathcal{G}\text{Conv}(\mathbf{X}_t, \mathbf{W}_r) + \mathcal{G}\text{Conv}(\mathbf{H}_{t-1}, \mathbf{U}_r) + \mathbf{b}_r \right)$$
$$\mathbf{z}_t = \sigma\left( \mathcal{G}\text{Conv}(\mathbf{X}_t, \mathbf{W}_z) + \mathcal{G}\text{Conv}(\mathbf{H}_{t-1}, \mathbf{U}_z) + \mathbf{b}_z \right)$$
$$\tilde{\mathbf{H}}_t = \tanh\left( \mathcal{G}\text{Conv}(\mathbf{X}_t, \mathbf{W}_h) + \mathcal{G}\text{Conv}(\mathbf{r}_t \odot \mathbf{H}_{t-1}, \mathbf{U}_h) + \mathbf{b}_h \right)$$
$$\mathbf{H}_t = (1 - \mathbf{z}_t) \odot \mathbf{H}_{t-1} + \mathbf{z}_t \odot \tilde{\mathbf{H}}_t$$

---

## 3. Specialized Meteorological Algorithms

### 3.1 Dynamic 0–6 Hour Lead-Time Blending Curve
Standard radar nowcasts fail past $t=90$ minutes, while NWP models fail at $t<120$ minutes due to spin-up errors. We compute the nowcast prediction $\hat{\mathbf{Y}}(\Delta t)$ as a lead-time dependent blend:

$$\hat{\mathbf{Y}}(\Delta t) = W_{\text{radar}}(\Delta t) \cdot \hat{\mathbf{Y}}_{\text{STGAT}}(\Delta t) + W_{\text{NWP}}(\Delta t) \cdot \mathbf{Y}_{\text{NWP}}(\Delta t)$$

With blending weights governed by exponential decay:
$$W_{\text{radar}}(\Delta t) = \exp\left( -\frac{\Delta t}{\tau} \right), \quad \tau = 120\text{ minutes}$$
$$W_{\text{NWP}}(\Delta t) = 1 - W_{\text{radar}}(\Delta t)$$

| Lead Time $\Delta t$ | Radar / STGAT Weight | NWP Instability Weight | Dominant Physical Mechanism |
|---|---|---|---|
| **15 min** | **88.2%** | **11.8%** | Kinematic radar advection + Lightning density |
| **30 min** | **77.9%** | **22.1%** | Cell morphology + GAT spatial attention |
| **60 min** | **60.7%** | **39.3%** | Advection + CAPE instability gradient |
| **120 min** | **36.8%** | **63.2%** | Transition: Convective Initiation & Steering Winds |
| **180 min** | **22.3%** | **77.7%** | NWP thermodynamic moisture & shear convergence |
| **360 min (6h)**| **5.0%** | **95.0%** | Mesoscale synoptic NWP forcing |

---

### 3.2 Satellite Convective Initiation (CI) Precursor Detection
Pre-radar storm genesis is identified using INSAT-3D split-window cooling rates:
1. **Cloud-Top Cooling Rate (CTC)**:
   $$\text{CTC} = \frac{BT_{10.8}(t) - BT_{10.8}(t - 15\text{m})}{\Delta t} \le -1.5^\circ\text{C} / 15\text{ min}$$
2. **Split-Window Difference (SWD)**:
   $$\text{SWD} = BT_{10.8} - BT_{12.0} < 0.0^\circ\text{C}$$
   *(Signifies thick glaciated cirrus/cumulonimbus cloud anvil penetrating the tropopause).*
3. **Tri-Spectral Water Vapor Difference**:
   $$(BT_{6.7} - BT_{10.8}) \ge -5.0^\circ\text{C}$$
   *(Indicates deep atmospheric moisture reaching the upper troposphere).*

When all three conditions hold, the engine triggers a **Pre-Convective Initiation Alert** 30–45 minutes before reflectivity reaches 35 dBZ.

---

### 3.3 Standalone Lightning Nowcasting (Onset & Strike Probability Field)
Unlike legacy alert systems that only monitor strikes after lightning is already occurring, NEXUS-NOWCAST performs proactive **lightning nowcasting** across two distinct physical regimes:

1. **Pre-Strike Lightning Onset Prediction (15–45 min Lead Time)**:
   - Evaluates mixed-phase hydrometeor charge separation conditions using fused multi-radar reflectivity and INSAT-3D cloud cooling:
     $$P(\text{Lightning Onset} > 0) = \sigma\left( w_1 Z_{\text{mixed}} + w_2 \frac{dBT_{10.8}}{dt} + w_3 \text{CAPE} - \theta_L \right)$$
     Where $Z_{\text{mixed}}$ is maximum radar reflectivity in the $-10^\circ\text{C}$ to $-20^\circ\text{C}$ mixed-phase charging layer (typically $Z > 35\text{–}40\text{ dBZ}$ for non-inductive electrification).
   - Generates a **1km spatial ground-strike probability grid** and issues early warnings 15–45 minutes before the first cloud-to-ground flash hits.

2. **Forecast Spatial Flash Density Field**:
   - For lead times $\Delta t \in [0, 360\text{ min}]$, Head B of the STGAT model outputs continuous flash rate density $\hat{\rho}_{\text{light}}(\mathbf{p}, t + \Delta t)$ ($\text{flashes/km}^2/\text{hr}$), calibrated against historical Indian Lightning Detection Network observations.

### 3.4 Operational Lightning Jump Algorithm (Severe Squall Escalation)
Once an electrified convective cell is active, sudden surges in total flash rate signify intense updraft acceleration preceding severe ground strikes, hail, and squalls:
1. Compute total flash rate in 2-minute rolling bins: $FR(t)$.
2. Compute time rate of change:
   $$DFR(t) = \frac{FR(t) - FR(t - 12\text{m})}{12\text{ min}}$$
3. Track historical mean $\mu_{DFR}$ and standard deviation $\sigma_{DFR}$ over the preceding 60 minutes:
   $$\text{Lightning Jump Metric } J(t) = \frac{DFR(t) - \mu_{DFR}}{\sigma_{DFR}}$$
4. **Trigger Condition**: If $J(t) \ge 2.0$ (2-sigma jump) and $FR(t) \ge 10\text{ flashes/min}$, issue an immediate **Severe Lightning & Downburst Alert**.

---

## 4. Multi-Task Training & Loss Functions

The STGAT-PIE network is optimized end-to-end with a compound physics-guided loss function:

$$\mathcal{L}_{\text{total}} = \alpha \mathcal{L}_{\text{storm}} + \beta \mathcal{L}_{\text{light}} + \gamma \mathcal{L}_{\text{traj}} + \lambda \mathcal{L}_{\text{advection}}$$

1. **Storm Intensity Loss ($\mathcal{L}_{\text{storm}}$)**:
   Combination of Focal Loss (to counteract the 95% clear-sky class imbalance) and Smooth L1 Loss on dBZ:
   $$\mathcal{L}_{\text{storm}} = \text{FL}(p_{\text{storm}}, y_{\text{storm}}; \gamma_{\text{focal}}=2.0) + 0.5 \cdot \text{SmoothL1}(\hat{Z}, Z)$$
2. **Lightning Density Loss ($\mathcal{L}_{\text{light}}$)**:
   $$\mathcal{L}_{\text{light}} = \text{DiceLoss}(p_{\text{light}}, y_{\text{light}}) + \text{MSE}(\hat{\text{FR}}, \text{FR})$$
3. **Trajectory Displacement Loss ($\mathcal{L}_{\text{traj}}$)**:
   $$\mathcal{L}_{\text{traj}} = \frac{1}{N_{\text{cells}}} \sum_{c=1}^{N_{\text{cells}}} \|\Delta \hat{\mathbf{x}}_c - \Delta \mathbf{x}_c\|_2$$
4. **Physics Advection Consistency Loss ($\mathcal{L}_{\text{advection}}$)**:
   Penalizes predicted cell displacement $\Delta \hat{\mathbf{x}}$ that deviates unphysically from the environmental steering wind $\mathbf{v}_{700}$:
   $$\mathcal{L}_{\text{advection}} = 1 - \frac{\Delta \hat{\mathbf{x}} \cdot \mathbf{v}_{700}}{\|\Delta \hat{\mathbf{x}}\| \|\mathbf{v}_{700}\| + \epsilon}$$

---

## 5. Meteorological Verification Metrics Suite

Evaluated using the standard $2 \times 2$ contingency table across lead times ($t+15\text{m}, \dots, t+360\text{m}$):

| Observed / Predicted | Predicted YES | Predicted NO |
|---|---|---|
| **Observed YES** | Hits ($a$) | Misses ($c$) |
| **Observed NO** | False Alarms ($b$) | Correct Rejections ($d$) |

- **Critical Success Index (CSI)**:
  $$\text{CSI} = \frac{a}{a + b + c}$$
- **Probability of Detection (POD)**:
  $$\text{POD} = \frac{a}{a + c}$$
- **False Alarm Ratio (FAR)**:
  $$\text{FAR} = \frac{b}{a + b}$$
- **Equitable Threat Score (ETS)**:
  $$\text{ETS} = \frac{a - a_{\text{random}}}{a + b + c - a_{\text{random}}}, \quad a_{\text{random}} = \frac{(a + b)(a + c)}{a + b + c + d}$$
- **Heidke Skill Score (HSS)**:
  $$\text{HSS} = \frac{2(ad - bc)}{(a+c)(c+d) + (a+b)(b+d)}$$

---
*End of Technical Requirements Document*
