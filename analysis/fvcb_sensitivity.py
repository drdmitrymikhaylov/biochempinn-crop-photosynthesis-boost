"""How much does a 10 % gain in carboxylation capacity buy, and when?

A reference calculation with the Farquhar-von Caemmerer-Berry (FvCB) model of C3
photosynthesis, using standard published parameters -- no project data, no fitted
model. It answers one question the README poses: if a biostimulant raises Rubisco
capacity (Vcmax) or electron transport capacity (Jmax) by 10 %, how much does leaf
and canopy assimilation change, as a function of light and intercellular CO2?

Leaf model (Farquhar, von Caemmerer & Berry, Planta 149 (1980) 78):
    Wc = Vcmax (Ci - G*) / (Ci + Kc (1 + O/Ko))         Rubisco-limited
    Wj = J (Ci - G*) / (4 Ci + 8 G*)                     RuBP-regeneration-limited
    A  = min(Wc, Wj) - Rd
    J from the non-rectangular hyperbola  theta J^2 - (alpha I + Jmax) J + alpha I Jmax = 0
Kinetic constants at 25 C from Bernacchi et al., Plant Cell Environ. 24 (2001) 253.
Canopy: Beer-Lambert light profile I(L) = I0 exp(-k L), leaf-level FvCB at each depth,
integrated over leaf area index LAI (big-leaf-by-layers, no sun/shade split).

Writes results/fvcb_sensitivity.json.  Pure numpy.
"""
import json
from pathlib import Path

import numpy as np

# --- parameters (25 C) ---------------------------------------------------------
KC, KO, GSTAR, O2 = 404.9, 278.4, 42.75, 210.0     # umol/mol, mmol/mol, umol/mol, mmol/mol
VCMAX = 100.0                                       # umol CO2 m-2 s-1, a productive C3 crop leaf
JMAX = 1.67 * VCMAX                                 # Jmax:Vcmax ratio at 25 C (Medlyn et al. 2002)
RD = 0.015 * VCMAX                                  # day respiration
ALPHA, THETA = 0.3, 0.7                             # quantum yield (mol e- / mol incident photons), curvature
KM = KC * (1 + O2 / KO)                             # effective Michaelis constant, umol/mol

PPFD = np.array([100, 200, 400, 600, 800, 1000, 1500, 2000], float)   # umol photons m-2 s-1
CI = {"drought_Ci_200": 200.0, "ambient_Ci_290": 290.0, "elevated_Ci_490": 490.0}
# Ci ~ 0.7 Ca for a well-watered C3 leaf (Ca 420 -> 290; Ca 700 -> 490); stomatal closure
# under drought pulls Ci to ~200 while Ca stays at 420.
LAI, K_EXT = 4.0, 0.5
OUT = Path(__file__).resolve().parents[1] / "results" / "fvcb_sensitivity.json"


def j_light(I, jmax):
    b = ALPHA * I + jmax
    return (b - np.sqrt(b * b - 4 * THETA * ALPHA * I * jmax)) / (2 * THETA)


def leaf(I, ci, vcmax=VCMAX, jmax=JMAX):
    wj = j_light(np.asarray(I, float), jmax) * (ci - GSTAR) / (4 * ci + 8 * GSTAR)
    wc = np.full_like(wj, vcmax * (ci - GSTAR) / (ci + KM))
    return np.minimum(wc, wj) - RD, wc, wj


def canopy(I0, ci, vcmax=VCMAX, jmax=JMAX, n=400):
    L = (np.arange(n) + 0.5) * LAI / n
    I = I0 * np.exp(-K_EXT * L)                     # incident flux on a leaf at depth L
    a, _, _ = leaf(I, ci, vcmax, jmax)
    return a.sum() * LAI / n                        # umol CO2 m-2 ground s-1


def crossover_ppfd(ci):
    """Light at which Wc = Wj for this Ci: below it the leaf is RuBP-limited."""
    wc = VCMAX * (ci - GSTAR) / (ci + KM)
    j_needed = wc * (4 * ci + 8 * GSTAR) / (ci - GSTAR)
    if j_needed >= JMAX:
        return None
    # invert the hyperbola for I
    return j_needed * (THETA * j_needed - JMAX) / (ALPHA * (j_needed - JMAX))


def main():
    out = {"parameters": {"Vcmax": VCMAX, "Jmax": JMAX, "Rd": RD, "Kc": KC, "Ko": KO,
                          "Gamma_star": GSTAR, "O2": O2, "alpha": ALPHA, "theta": THETA,
                          "LAI": LAI, "k_extinction": K_EXT, "temperature_C": 25,
                          "Ci_umol_mol": CI, "PPFD": PPFD.tolist()},
           "units": {"A": "umol CO2 m-2 s-1 (leaf: per leaf area; canopy: per ground area)",
                     "gain": "fractional change in A for a +10 % change in the named parameter"},
           "leaf": {}, "canopy": {}, "crossover_ppfd": {}}
    for name, ci in CI.items():
        a0, wc, wj = leaf(PPFD, ci)
        a_v, _, _ = leaf(PPFD, ci, vcmax=1.1 * VCMAX)
        a_j, _, _ = leaf(PPFD, ci, jmax=1.1 * JMAX)
        a_b, _, _ = leaf(PPFD, ci, vcmax=1.1 * VCMAX, jmax=1.1 * JMAX)
        out["leaf"][name] = {
            "A": a0.round(3).tolist(),
            "limiting": ["Rubisco" if c < j else "RuBP" for c, j in zip(wc, wj)],
            "gain_Vcmax_10pct": ((a_v - a0) / a0).round(6).tolist(),
            "gain_Jmax_10pct": ((a_j - a0) / a0).round(6).tolist(),
            "gain_both_10pct": ((a_b - a0) / a0).round(6).tolist(),
        }
        c0 = np.array([canopy(I, ci) for I in PPFD])
        cv = np.array([canopy(I, ci, vcmax=1.1 * VCMAX) for I in PPFD])
        cj = np.array([canopy(I, ci, jmax=1.1 * JMAX) for I in PPFD])
        out["canopy"][name] = {
            "A": c0.round(3).tolist(),
            "gain_Vcmax_10pct": ((cv - c0) / c0).round(6).tolist(),
            "gain_Jmax_10pct": ((cj - c0) / c0).round(6).tolist(),
        }
        x = crossover_ppfd(ci)
        out["crossover_ppfd"][name] = None if x is None else round(float(x), 1)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}\n")
    for name in CI:
        print(f"== {name}  crossover PPFD {out['crossover_ppfd'][name]}")
        L, C = out["leaf"][name], out["canopy"][name]
        print("PPFD   A_leaf  lim      dV     dJ   | A_canopy   dV     dJ")
        for i, I in enumerate(PPFD):
            print(f"{I:5.0f} {L['A'][i]:7.2f}  {L['limiting'][i]:8s} "
                  f"{L['gain_Vcmax_10pct'][i]:+.3f} {L['gain_Jmax_10pct'][i]:+.3f} | "
                  f"{C['A'][i]:8.2f} {C['gain_Vcmax_10pct'][i]:+.3f} {C['gain_Jmax_10pct'][i]:+.3f}")
        print()


if __name__ == "__main__":
    main()
