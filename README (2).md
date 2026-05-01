# Stokel: A Data-Driven Energy Confinement Scaling for Mainline Tokamaks

A symbolic regression + physics-constrained approach to tokamak energy confinement scaling, tested against the ITPA HDB5 database.

---

## What This Is

An alternative energy confinement time scaling law derived from the HDB5 database (v2.3), constrained by the Kadomtsev dimensionless physics requirement. Tested on 5 mainline tokamaks (AUG, CMOD, D3D, JET, JT60U).

**Not a revolution. Not a paper. Just a result worth sharing.**

---

## The Formula

```
τ_E = 0.099 · (ne20/nGW)^0.062 · Ip^1.314 · P^(-0.661) · R^1.206 · κ^0.646 · (1+δ)^0.623
```

Where:
- `Ip` in MA
- `P` in MW  
- `R` in m
- `ne20` = electron density in 10²⁰ m⁻³
- `nGW` = Greenwald density = Ip / (π·a²)

Kadomtsev constraint satisfied: `4·α_R - 8·α_n - α_I - 3·α_P - 5·α_B - 5 ≈ 0`

---

## Results

| Reactor | Stokel % error | IPB98 % error |
|---------|---------------|---------------|
| AUG     | 16.1          | 35.9          |
| CMOD    | 15.6          | 33.0          |
| D3D     | 20.2          | 32.9          |
| JET     | 17.4          | 60.3          |
| JT60U   | 15.4          | 86.7          |
| **Overall** | **17.1**  | **49.3**      |

---

## Validation

**Leave-One-Machine-Out (LOMO):**

| Left out | LOMO error | Full data error |
|----------|-----------|-----------------|
| AUG      | 16.5%     | 16.1%           |
| CMOD     | 27.1%     | 15.6%           |
| D3D      | 21.9%     | 20.2%           |
| JET      | 21.4%     | 17.4%           |
| JT60U    | 16.3%     | 15.4%           |

All under 35% — suggests the model is not simply memorizing device-specific patterns.

Bootstrap (500 iterations, 80% resampling): exponents are stable across runs.

---

## What We Found Along the Way

- **Bt dropped out**: Toroidal field coefficient optimizes near zero. Fixing it at IPB98's value (0.15) increases error by only 0.18%. Likely due to operational coupling between Ip and Bt via the q95 safety factor constraint.

- **Density dependence is weak** (α_n ≈ 0.06 vs IPB98's 0.41): May reflect the shift toward metal-wall devices in the dataset, where high density degrades pedestal performance.

- **ITER extrapolation is unreliable**: The model gives ~2.7s for ITER parameters, vs IPB98's ~6.0s, vs the design target of 3.7s. ITER is far outside the training distribution. Neither number should be trusted for ITER specifically.

---

## Honest Limitations

- Only 5 mainline tokamaks (Ip > 0.5 MA, Bt > 1.0 T)
- TFTR excluded (limiter configuration)
- Spherical tokamaks (MAST, NSTX) and small devices not covered
- Single global calibration constant
- No turbulent transport physics (ETG, ITG)
- ITER extrapolation is out-of-distribution

---

## Data

ITPA HDB5 v2.3 database. Not included in this repo — available through the ITPA community.

---

## How to Run

```bash
pip install pandas numpy scipy openpyxl matplotlib
python test2.py       # Full reactor comparison
python lomo_nobt.py   # LOMO validation
```

Place `HDB5V2.3.xlsx` in the same directory.

---

## Background

Started as a tokamak particle simulation (Sandbox) with symbolic regression (SymReg) finding confinement formulas from simulation data. The simulation-derived formula didn't generalize. So we went directly to real data.

This is the result.

---

*Built with HDB5, scipy, and too much coffee. Feedback welcome.*
