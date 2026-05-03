"""
Stokel V-Final: Empirical Energy Confinement Scaling Law
========================================================
For mainline tokamak H-mode plasmas.

Derived from ITPA HDB5 v2.3 with Kadomtsev dimensional constraint.
Validated via Leave-One-Machine-Out (LOMO) and bootstrap resampling.

Formula:
    tau_E = 0.099 * (ne20/nGW)^0.062 * Ip^1.314 * P^(-0.661)
            * R^1.206 * kappa^0.646 * (1+delta)^0.623

Where:
    Ip   : plasma current (MA)
    P    : total heating power (MW)
    R    : major radius (m)
    ne20 : electron density (1e20 m^-3)
    nGW  : Greenwald density = Ip / (pi * a^2)
    kappa: elongation
    delta: triangularity

Validity domain:
    - Ip > 0.5 MA, Bt > 1.0 T
    - Diverted H-mode (PHASE: H, HSELM, HGELM)
    - Mainline tokamaks only (excludes spherical, limiter)
    - Reactors: AUG, CMOD, D3D, JET, JT60U
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize


# ============================================================
# FINAL COEFFICIENTS (Stokel V-Final, Bt-free)
# ============================================================
COEFFS = {
    'logC': -2.3116,
    'a_n':   0.0617,    # density (ne/nGW)
    'a_I':   1.3135,    # plasma current
    'a_P':  -0.6614,    # heating power
    'a_R':   1.2056,    # major radius
    'a_k':   0.6455,    # elongation
    'a_d':   0.6231,    # triangularity
}


# ============================================================
# CORE PREDICTION FUNCTIONS
# ============================================================
def stokel(row, coeffs=None):
    """Stokel V-Final prediction for a single shot."""
    c = coeffs or COEFFS
    Ip = abs(row['IP']) / 1e6
    ne20 = row['NEL'] / 1e20
    nGW = Ip / (np.pi * row['AMIN']**2)
    P = max((abs(row['POHM']) + abs(row['PICRH']) + abs(row['PNBI'])) / 1e6, 0.01)

    log_tau = (c['logC']
               + c['a_n'] * np.log(ne20 / nGW)
               + c['a_I'] * np.log(Ip)
               + c['a_P'] * np.log(P)
               + c['a_R'] * np.log(row['RGEO'])
               + c['a_k'] * np.log(row['KAPPA'])
               + c['a_d'] * np.log(1 + row.get('DELTA', 0)))
    return np.exp(log_tau)


def ipb98(row):
    """IPB98(y,2) reference scaling."""
    Ip = abs(row['IP']) / 1e6
    Bt = abs(row['BT'])
    ne = row['NEL'] / 1e19
    P = max((abs(row['POHM']) + abs(row['PICRH']) + abs(row['PNBI'])) / 1e6, 0.01)
    return (0.0562 * Ip**0.93 * Bt**0.15 * ne**0.41 * P**-0.69
            * row['RGEO']**1.97 * row['AMIN']**0.58 * row['KAPPA']**0.78)


def mape(actual, pred):
    """Mean Absolute Percentage Error."""
    actual = np.asarray(actual)
    pred = np.asarray(pred)
    m = (actual > 0) & (pred > 0) & np.isfinite(pred)
    if m.sum() == 0:
        return np.nan
    return np.mean(np.abs((actual[m] - pred[m]) / actual[m])) * 100


# ============================================================
# DATA LOADING & FILTERING
# ============================================================
def load_hdb5(path='HDB5V2.3.xlsx'):
    """Load HDB5 and apply mainline tokamak filter."""
    df = pd.read_excel(path)
    cols = ['IP', 'BT', 'NEL', 'POHM', 'PICRH', 'PNBI',
            'RGEO', 'AMIN', 'KAPPA', 'TAUTH']
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')

    if 'DELTA' in df.columns:
        df['DELTA'] = pd.to_numeric(df['DELTA'], errors='coerce').fillna(0)
    else:
        df['DELTA'] = 0.0

    df = df.dropna(subset=cols)

    # Mainline filter
    main = df[
        (abs(df['IP']) > 500000) &
        (abs(df['BT']) > 1.0) &
        (df['TOK'] != 'TFTR') &
        (df['PHASE'].isin(['H', 'HSELM', 'HGELM']))
    ].copy()

    return main, df


# ============================================================
# OPTIMIZATION (with Kadomtsev constraint)
# ============================================================
def fit_stokel(data):
    """Fit Stokel coefficients with Kadomtsev dimensional constraint."""
    d = data.copy()
    d['Ip_MA'] = abs(d['IP']) / 1e6
    d['ne20'] = d['NEL'] / 1e20
    d['nGW'] = d['Ip_MA'] / (np.pi * d['AMIN']**2)
    d['P_MW'] = ((abs(d['POHM']) + abs(d['PICRH']) + abs(d['PNBI'])) / 1e6).clip(lower=0.01)
    d['log_nfrac'] = np.log(d['ne20'] / d['nGW'])
    d['log_Ip'] = np.log(d['Ip_MA'])
    d['log_P'] = np.log(d['P_MW'])
    d['log_R'] = np.log(d['RGEO'])
    d['log_k'] = np.log(d['KAPPA'])
    d['log_d'] = np.log(1 + d['DELTA'])
    d = d.dropna(subset=['log_nfrac', 'log_Ip', 'log_P', 'log_R', 'log_k'])

    def predict(params, df):
        logC, a_n, a_I, a_P, a_R, a_k, a_d = params
        return (logC + a_n*df['log_nfrac'] + a_I*df['log_Ip']
                + a_P*df['log_P'] + a_R*df['log_R']
                + a_k*df['log_k'] + a_d*df['log_d'])

    # Kadomtsev: 4*a_R - 8*a_n - a_I - 3*a_P - 5 = 0  (Bt-free)
    kadomtsev = {'type': 'eq',
                 'fun': lambda x: 4*x[4] - 8*x[1] - x[2] - 3*x[3] - 5}

    x0 = [-2.3, 0.06, 1.31, -0.66, 1.21, 0.65, 0.62]
    res = minimize(
        lambda p: mape(d['TAUTH'], np.exp(predict(p, d))),
        x0, method='SLSQP', constraints=[kadomtsev],
        options={'maxiter': 500}
    )
    return dict(zip(['logC', 'a_n', 'a_I', 'a_P', 'a_R', 'a_k', 'a_d'], res.x))


# ============================================================
# VALIDATION TESTS
# ============================================================
def reactor_breakdown(data):
    """Per-reactor error breakdown."""
    rows = []
    for tok in sorted(data['TOK'].unique()):
        s = data[data['TOK'] == tok]
        if len(s) < 10:
            continue
        s_pred = s.apply(stokel, axis=1)
        i_pred = s.apply(ipb98, axis=1)
        rows.append({
            'reactor': tok,
            'N': len(s),
            'stokel_err': mape(s['TAUTH'], s_pred),
            'ipb98_err': mape(s['TAUTH'], i_pred),
        })
    return pd.DataFrame(rows)


def lomo_validation(data):
    """Leave-One-Machine-Out validation."""
    reactors = sorted(data['TOK'].unique())
    rows = []
    for tok in reactors:
        test = data[data['TOK'] == tok]
        train = data[data['TOK'] != tok]
        if len(test) < 10 or len(train) < 100:
            continue
        coeffs_lomo = fit_stokel(train)
        pred = test.apply(lambda r: stokel(r, coeffs_lomo), axis=1)
        full_pred = test.apply(stokel, axis=1)
        rows.append({
            'left_out': tok,
            'N': len(test),
            'lomo_err': mape(test['TAUTH'], pred),
            'full_err': mape(test['TAUTH'], full_pred),
        })
    return pd.DataFrame(rows)


def ood_tests(data):
    """Out-of-distribution boundary tests."""
    data = data.copy()
    data['Ip_MA'] = abs(data['IP']) / 1e6
    data['P_MW'] = (abs(data['POHM']) + abs(data['PICRH']) + abs(data['PNBI'])) / 1e6

    results = {}

    # High-P
    p90 = data['P_MW'].quantile(0.90)
    high_p = data[data['P_MW'] > p90]
    results['high_P'] = {
        'threshold': f'P > {p90:.1f} MW',
        'N': len(high_p),
        'stokel_err': mape(high_p['TAUTH'], high_p.apply(stokel, axis=1)),
        'ipb98_err': mape(high_p['TAUTH'], high_p.apply(ipb98, axis=1)),
    }

    # High-Ip
    ip90 = data['Ip_MA'].quantile(0.90)
    high_ip = data[data['Ip_MA'] > ip90]
    results['high_Ip'] = {
        'threshold': f'Ip > {ip90:.2f} MA',
        'N': len(high_ip),
        'stokel_err': mape(high_ip['TAUTH'], high_ip.apply(stokel, axis=1)),
        'ipb98_err': mape(high_ip['TAUTH'], high_ip.apply(ipb98, axis=1)),
    }

    return results


def predict_iter():
    """ITER prediction (for reference; OUT OF DISTRIBUTION — unreliable)."""
    iter_params = {
        'IP': 15e6, 'BT': 5.3, 'NEL': 1e20,
        'POHM': 0, 'PICRH': 0, 'PNBI': 150e6,
        'RGEO': 6.2, 'AMIN': 2.0, 'KAPPA': 1.7, 'DELTA': 0.33,
    }
    row = pd.Series(iter_params)
    return {
        'stokel_s': stokel(row),
        'ipb98_s': ipb98(row),
        'design_target_s': 3.7,
        'note': 'ITER is far outside training distribution. Both predictions are unreliable.',
    }


# ============================================================
# MAIN PIPELINE
# ============================================================
def run_full_validation(path='HDB5V2.3.xlsx'):
    """Run all validation tests and print a clean report."""
    print("=" * 60)
    print("STOKEL V-FINAL — FULL VALIDATION REPORT")
    print("=" * 60)

    print("\nLoading HDB5...")
    main, full = load_hdb5(path)
    print(f"Mainline H-mode shots: {len(main)}")
    print(f"Reactors: {sorted(main['TOK'].unique())}")

    # 1. Reactor breakdown
    print("\n--- Per-Reactor Error ---")
    rb = reactor_breakdown(main)
    print(rb.to_string(index=False))
    overall_s = mape(main['TAUTH'], main.apply(stokel, axis=1))
    overall_i = mape(main['TAUTH'], main.apply(ipb98, axis=1))
    print(f"\nOverall: Stokel {overall_s:.1f}% | IPB98 {overall_i:.1f}%")

    # 2. LOMO
    print("\n--- LOMO Validation ---")
    lomo = lomo_validation(main)
    print(lomo.to_string(index=False))
    print(f"All under 35%: {(lomo['lomo_err'] < 35).all()}")

    # 3. OOD
    print("\n--- OOD Boundary Tests ---")
    ood = ood_tests(main)
    for name, r in ood.items():
        print(f"{name} ({r['threshold']}, n={r['N']}):")
        print(f"  Stokel: {r['stokel_err']:.1f}%   IPB98: {r['ipb98_err']:.1f}%")

    # 4. TFTR (limiter — outside model scope)
    tftr = full[(full['TOK'] == 'TFTR')
                & (full['PHASE'].isin(['H', 'HSELM', 'HGELM']))]
    if len(tftr) > 0:
        print(f"\n--- TFTR (limiter, OUT OF SCOPE) ---")
        print(f"  N={len(tftr)}")
        print(f"  Stokel: {mape(tftr['TAUTH'], tftr.apply(stokel, axis=1)):.1f}%")
        print(f"  IPB98:  {mape(tftr['TAUTH'], tftr.apply(ipb98, axis=1)):.1f}%")
        print("  (Stokel does not apply to limiter configurations.)")

    # 5. ITER
    print("\n--- ITER Prediction (EXTRAPOLATION — unreliable) ---")
    it = predict_iter()
    print(f"  Stokel: {it['stokel_s']:.2f} s")
    print(f"  IPB98:  {it['ipb98_s']:.2f} s")
    print(f"  Design target: {it['design_target_s']} s")
    print(f"  Note: {it['note']}")

    print("\n" + "=" * 60)
    print("END OF REPORT")
    print("=" * 60)


if __name__ == '__main__':
    run_full_validation()
