"""How much of the FvCB reference calculation rests on its fixed choices?

analysis/fvcb_sensitivity.py puts the light at which a well-watered leaf stops being
RuBP-limited at 1839 umol m-2 s-1.  That number comes from four things the script
holds fixed: the ratio Jmax:Vcmax (1.67), the quantum yield alpha (0.3), the curvature
theta (0.7) and the leaf temperature (25 C).  This script moves each one, alone, over
a published range and reports where the crossover goes and what a +10 % gain in
Vcmax or Jmax is then worth.

Temperature: Arrhenius scaling from 25 C, activation energies (kJ/mol) of Vcmax, Rd,
Gamma*, Kc, Ko from Bernacchi et al., Plant Cell Environ. 24 (2001) 253, and of Jmax
from Bernacchi, Pimentel & Long, Plant Cell Environ. 26 (2003) 1419.  No
high-temperature deactivation term, so the sweep stops at 35 C.  alpha, theta and Ci
are held at their 25 C values.

Writes results/fvcb_ratio_temperature.json.  Pure numpy.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fvcb_sensitivity as base          # constants of the 25 C calculation  # noqa: E402

R, T25 = 8.314462618e-3, 298.15          # kJ mol-1 K-1, K
EA = {"Vcmax": 65.33, "Rd": 46.39, "Gamma_star": 37.83, "Kc": 79.43, "Ko": 36.38, "Jmax": 43.54}
RATIOS = [1.4, 1.5, 1.6, 1.67, 1.8, 1.9, 2.0, 2.2, 2.5]
ALPHAS = [0.24, 0.30, 0.36]
THETAS = [0.5, 0.7, 0.9]
TEMPS = [15, 20, 25, 30, 35]
PPFD = np.array([1000.0, 1500.0, 2000.0])
OUT = Path(__file__).resolve().parents[1] / "results" / "fvcb_ratio_temperature.json"


def arrhenius(ea, t_c):
    tk = t_c + 273.15
    return float(np.exp(ea * (tk - T25) / (T25 * R * tk)))


def state(t_c=25.0, ratio=1.67, alpha=base.ALPHA, theta=base.THETA):
    """Model parameters at leaf temperature t_c; ratio is Jmax:Vcmax at 25 C."""
    kc = base.KC * arrhenius(EA["Kc"], t_c)
    ko = base.KO * arrhenius(EA["Ko"], t_c)
    return {"vcmax": base.VCMAX * arrhenius(EA["Vcmax"], t_c),
            "jmax": ratio * base.VCMAX * arrhenius(EA["Jmax"], t_c),
            "rd": base.RD * arrhenius(EA["Rd"], t_c),
            "gstar": base.GSTAR * arrhenius(EA["Gamma_star"], t_c),
            "km": kc * (1 + base.O2 / ko), "alpha": alpha, "theta": theta}


def net_a(I, ci, p, fv=1.0, fj=1.0):
    vc, jm = fv * p["vcmax"], fj * p["jmax"]
    b = p["alpha"] * I + jm
    j = (b - np.sqrt(b * b - 4 * p["theta"] * p["alpha"] * I * jm)) / (2 * p["theta"])
    wj = j * (ci - p["gstar"]) / (4 * ci + 8 * p["gstar"])
    wc = vc * (ci - p["gstar"]) / (ci + p["km"])
    return np.minimum(wc, wj) - p["rd"]


def j_needed(ci, p):
    """Electron transport rate at which the RuBP-limited rate equals the Rubisco-limited one."""
    return p["vcmax"] * (4 * ci + 8 * p["gstar"]) / (ci + p["km"])


def crossover(ci, p):
    """Light below which the leaf is RuBP-limited; None if it is at every light."""
    j = j_needed(ci, p)
    if j >= p["jmax"]:
        return None
    return float(j * (p["theta"] * j - p["jmax"]) / (p["alpha"] * (j - p["jmax"])))


def cell(ci, p):
    a0 = net_a(PPFD, ci, p)
    x = crossover(ci, p)
    return {"crossover_ppfd": None if x is None else round(x, 2),
            "J_needed_to_Vcmax": round(j_needed(ci, p) / p["vcmax"], 3),
            "A": a0.round(3).tolist(),
            "gain_Vcmax_10pct": ((net_a(PPFD, ci, p, fv=1.1) - a0) / a0).round(6).tolist(),
            "gain_Jmax_10pct": ((net_a(PPFD, ci, p, fj=1.1) - a0) / a0).round(6).tolist()}


def ratio_for_crossover(ci, light, p):
    """Jmax:Vcmax that puts the crossover at `light` (closed form); None if no ratio does."""
    j, ai = j_needed(ci, p), p["alpha"] * light
    if j >= ai:                              # even an unlimited Jmax cannot deliver j at this light
        return None
    return round(float(j * (p["theta"] * j - ai) / (j - ai) / p["vcmax"]), 4)


def temperature_for_crossover(ci, light):
    """Lowest leaf temperature (0.01 C grid, 10-40 C) at which the crossover is at or below `light`."""
    for t in np.arange(10.0, 40.0001, 0.01):
        x = crossover(ci, state(t_c=float(t)))
        if x is not None and x <= light:
            return round(float(t), 2)
    return None


def main():
    p25 = state()
    lights = [int(v) for v in PPFD]
    out = {"parameters": {"base": "analysis/fvcb_sensitivity.py (Vcmax 100, Rd 1.5, Bernacchi 2001 kinetics at 25 C)",
                          "activation_energy_kJ_mol": EA, "ratios": RATIOS, "alphas": ALPHAS,
                          "thetas": THETAS, "temperatures_C": TEMPS, "PPFD": lights,
                          "Ci_umol_mol": base.CI},
           "units": {"crossover_ppfd": "umol photons m-2 s-1; null = RuBP-limited at every light",
                     "gain": "fractional change in net A for a +10 % change in the named capacity, "
                             "at PPFD 1000 / 1500 / 2000"},
           "ratio": {"never_rubisco_limited_at_or_below_ratio": {}, "ratio_for_crossover_at_ppfd": {},
                     "lowest_possible_crossover_ppfd": {}, "by_ratio": {}},
           "alpha": {}, "theta": {},
           "temperature": {"by_temperature": {}, "temperature_for_crossover_at_ppfd": {},
                           "never_rubisco_limited_below_C": {}}}
    for name, ci in base.CI.items():
        out["ratio"]["never_rubisco_limited_at_or_below_ratio"][name] = round(j_needed(ci, p25) / p25["vcmax"], 4)
        out["ratio"]["ratio_for_crossover_at_ppfd"][name] = {str(l): ratio_for_crossover(ci, l, p25) for l in lights}
        out["ratio"]["lowest_possible_crossover_ppfd"][name] = round(j_needed(ci, p25) / p25["alpha"], 2)
        out["temperature"]["temperature_for_crossover_at_ppfd"][name] = {
            str(l): temperature_for_crossover(ci, l) for l in lights}
        out["temperature"]["never_rubisco_limited_below_C"][name] = temperature_for_crossover(ci, float("inf"))
    for r in RATIOS:
        out["ratio"]["by_ratio"][str(r)] = {n: cell(ci, state(ratio=r)) for n, ci in base.CI.items()}
    for a in ALPHAS:
        out["alpha"][str(a)] = {n: cell(ci, state(alpha=a)) for n, ci in base.CI.items()}
    for th in THETAS:
        out["theta"][str(th)] = {n: cell(ci, state(theta=th)) for n, ci in base.CI.items()}
    for t in TEMPS:
        p = state(t_c=float(t))
        row = {"Vcmax": round(p["vcmax"], 2), "Jmax": round(p["jmax"], 2), "Rd": round(p["rd"], 3),
               "Km": round(p["km"], 1), "Gamma_star": round(p["gstar"], 2),
               "Jmax_to_Vcmax": round(p["jmax"] / p["vcmax"], 3)}
        row.update({n: cell(ci, p) for n, ci in base.CI.items()})
        out["temperature"]["by_temperature"][str(t)] = row

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2))
    print(f"wrote {OUT}\n")
    amb = "ambient_Ci_290"
    pct = lambda g: " ".join(f"{100 * x:+5.1f}" for x in g)
    for key, label in (("ratio", "Jmax:Vcmax"), ("alpha", "alpha"), ("theta", "theta")):
        table = out[key]["by_ratio"] if key == "ratio" else out[key]
        print(f"== {label}: crossover PPFD (drought / ambient / elevated), ambient dV and dJ at 1000/1500/2000")
        for k, v in table.items():
            xs = " / ".join(str(v[n]["crossover_ppfd"]) for n in base.CI)
            print(f"{k:>5s}  {xs:28s} dV {pct(v[amb]['gain_Vcmax_10pct'])}   dJ {pct(v[amb]['gain_Jmax_10pct'])}")
        print()
    print("== temperature: Jmax:Vcmax, crossover (drought / ambient / elevated), dV at 1000/1500/2000 for each")
    for k, v in out["temperature"]["by_temperature"].items():
        xs = " / ".join(str(v[n]["crossover_ppfd"]) for n in base.CI)
        dv = " | ".join(pct(v[n]["gain_Vcmax_10pct"]) for n in base.CI)
        print(f"{k:>3s} C  {v['Jmax_to_Vcmax']:.3f}  {xs:26s} {dv}")
    print()
    for k in ("never_rubisco_limited_at_or_below_ratio", "ratio_for_crossover_at_ppfd", "lowest_possible_crossover_ppfd"):
        print(k, out["ratio"][k])
    for k in ("temperature_for_crossover_at_ppfd", "never_rubisco_limited_below_C"):
        print(k, out["temperature"][k])


if __name__ == "__main__":
    main()
