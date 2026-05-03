# Stokel: An Empirical Energy Confinement Scaling for Mainline Tokamaks

A symbolic regression + physics-constrained scaling law derived from the ITPA HDB5 v2.3 database, with full validation pipeline.

---

## Quick Start

```bash
pip install pandas numpy scipy openpyxl
# Place HDB5V2.3.xlsx in this directory
python stokel.py
```

This runs the full validation report: per-reactor breakdown, LOMO, OOD tests, ITER prediction.

---

## The Formula

```
τ_E = 0.099 · (ne20/nGW)^0.062 · Ip^1.314 · P^(-0.661) · R^1.206 · κ^0.646 · (1+δ)^0.623
```

| Symbol | Meaning | Unit |
|--------|---------|------|
| `Ip`   | plasma current | MA |
| `P`    | total heating power | MW |
| `R`    | major radius | m |
| `ne20` | electron density | 10²⁰ m⁻³ |
| `nGW`  | Greenwald density = Ip/(π·a²) | 10²⁰ m⁻³ |
| `κ`    | elongation | — |
| `δ`    | triangularity | — |

**Kadomtsev dimensional constraint satisfied:** `4·α_R - 8·α_n - α_I - 3·α_P - 5 = 0`

---

## Results Summary

### Per-Reactor Error

| Reactor | N | Stokel % | IPB98 % |
|---------|---|----------|---------|
| AUG     | 2183 | 16.1 | 35.9 |
| CMOD    | 85   | 15.6 | 33.0 |
| D3D     | 601  | 20.2 | 32.9 |
| JET     | 3399 | 17.4 | 60.3 |
| JT60U   | 76   | 15.4 | 86.7 |
| **All** | **6344** | **17.1** | **49.3** |

### Leave-One-Machine-Out (LOMO)

The model is trained without one reactor, then tested on it.

| Left out | LOMO % | Full data % |
|----------|--------|-------------|
| AUG      | 16.5 | 16.1 |
| CMOD     | 27.1 | 15.6 |
| D3D      | 21.9 | 20.2 |
| JET      | 21.4 | 17.4 |
| JT60U    | 16.3 | 15.4 |

All under 35% — the model is not memorizing device-specific patterns.

### Bootstrap (500 resamples, 80%)

Coefficient stability:

| Param | Mean | Std | 5% | 95% |
|-------|------|-----|-----|-----|
| α_I (Ip)    |  1.339 | 0.017 |  1.310 |  1.369 |
| α_P (P)     | -0.655 | 0.013 | -0.676 | -0.634 |
| α_R (R)     |  1.162 | 0.030 |  1.112 |  1.210 |
| α_κ (kappa) |  0.566 | 0.092 |  0.426 |  0.724 |
| α_δ (delta) |  0.609 | 0.052 |  0.515 |  0.689 |

### OOD Boundary Tests

| Region | N | Stokel % | IPB98 % |
|--------|---|----------|---------|
| High-P (>14.7 MW)  | 635 | 16.3 | 70.1 |
| High-Ip (>3.16 MA) | 635 | 22.1 | 44.7 |
| TFTR (limiter)     | 104 | 55.9 | 23.7 |

TFTR result is expected — limiter configuration is outside the model's scope.

---

## Findings

**1. Bt drops out cleanly.** With Bt left free, its coefficient optimizes near zero (-0.04). Fixing it to IPB98's value (0.15) raises overall error by only 0.18 percentage points. This reflects the operational coupling between Ip and Bt via the q95 stability constraint — when the model knows Ip, it already has Bt's information.

**2. Density dependence is weak** (α_n ≈ 0.06 vs IPB98's 0.41). Likely reflects the dataset's shift toward metal-wall devices, where high density degrades pedestal performance rather than improving confinement.

**3. ITER extrapolation is unreliable.** The model gives 2.69 s for ITER design parameters vs IPB98's 5.97 s vs the 3.7 s design target. ITER is far outside the training distribution. **Neither value should be trusted.** The two models bracket the design point — that's the most that can be said.

---

## Files

- `stokel.py` — main module (load, fit, validate, predict)
- `simulation.html` — interactive 2D tokamak particle simulation with SymReg engine (the precursor to this work)
- `README.md` — this file

---

## What This Is Not

- Not a universal scaling law
- Not a replacement for IPB98 in all regimes
- Not validated for spherical tokamaks, small devices, or limiter plasmas
- Not a reliable ITER predictor

## What This Is

- An empirical scaling law that outperforms IPB98 on 5 mainline H-mode tokamaks
- Physically constrained (Kadomtsev) and statistically validated (LOMO, bootstrap)
- Reproducible — code and methodology open

---

## Validity Domain

- **Ip > 0.5 MA, Bt > 1.0 T**
- **Diverted H-mode** (PHASE: H, HSELM, HGELM)
- **Mainline tokamaks**: AUG, CMOD, D3D, JET, JT60U
- **Excluded**: spherical tokamaks (MAST, NSTX), small devices (COMPASS, TCV, TDEV), limiter (TFTR)

---

## Background

Started as a 2D particle simulation of a tokamak (`simulation.html`) with a symbolic regression engine searching for confinement formulas from simulated trajectories. The simulation-derived formula did not generalize to real reactor data.

The simulation provided the conceptual framework — symbolic regression, physics toolkit, dimensional reasoning. The final scaling law was then fit directly to HDB5 with the Kadomtsev dimensional constraint as a hard equality constraint.

---

## Data

ITPA HDB5 v2.3. Not included in this repository. Available through the ITPA community.

---

*Built over a long day. Results are reproducible. Limitations are real.*
