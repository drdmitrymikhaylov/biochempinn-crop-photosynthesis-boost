"""Pins the README section "What the 1839 rests on" to results/fvcb_ratio_temperature.json,
the JSON to analysis/fvcb_ratio_temperature.py, and its base point to the first calculation.
Run: python -m pytest tests/
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = json.loads((ROOT / "results" / "fvcb_ratio_temperature.json").read_text())
BASE = json.loads((ROOT / "results" / "fvcb_sensitivity.json").read_text())
README = " ".join((ROOT / "README.md").read_text().split())       # whitespace collapsed
DRY, AMB, ELE = "drought_Ci_200", "ambient_Ci_290", "elevated_Ci_490"


def light(x):
    return "never" if x is None else str(int(x + 0.5))


def pct(g):
    return "0" if round(100 * g, 1) == 0 else f"+{100 * g:.1f} %"


def gains(cell, key):
    return " / ".join(pct(g) for g in cell[key])


def ratio_row(r):
    c = RES["ratio"]["by_ratio"][r]
    return (f"| {r} | {light(c[DRY]['crossover_ppfd'])} | {light(c[AMB]['crossover_ppfd'])} | "
            f"{gains(c[AMB], 'gain_Vcmax_10pct')} | {gains(c[AMB], 'gain_Jmax_10pct')} |")


def temperature_row(t):
    c = RES["temperature"]["by_temperature"][t]
    return (f"| {t} °C | {c['Jmax_to_Vcmax']:.3f} | {light(c[DRY]['crossover_ppfd'])} | "
            f"{light(c[AMB]['crossover_ppfd'])} | {gains(c[AMB], 'gain_Vcmax_10pct')} | "
            f"{gains(c[DRY], 'gain_Vcmax_10pct')} |")


RATIO_ROWS = ("1.5", "1.6", "1.67", "1.8", "1.9", "2.0", "2.2")
TEMPERATURE_ROWS = ("15", "20", "25", "30", "35")


def test_script_reproduces_json(tmp_path):
    """The committed JSON is what the committed script writes."""
    shutil.copytree(ROOT / "analysis", tmp_path / "analysis",
                    ignore=shutil.ignore_patterns("._*", "__pycache__"))
    subprocess.run([sys.executable, str(tmp_path / "analysis" / "fvcb_ratio_temperature.py")],
                   check=True, capture_output=True)
    assert json.loads((tmp_path / "results" / "fvcb_ratio_temperature.json").read_text()) == RES


def test_base_point_is_the_first_calculation():
    """Ratio 1.67, alpha 0.3, theta 0.7 and 25 C must each give back fvcb_sensitivity.json."""
    ppfd = BASE["parameters"]["PPFD"]
    idx = [ppfd.index(v) for v in RES["parameters"]["PPFD"]]
    for cells in (RES["ratio"]["by_ratio"]["1.67"], RES["alpha"]["0.3"], RES["theta"]["0.7"],
                  RES["temperature"]["by_temperature"]["25"]):
        for name in (DRY, AMB, ELE):
            x = cells[name]["crossover_ppfd"]
            assert (None if x is None else round(x, 1)) == BASE["crossover_ppfd"][name]
            for key in ("gain_Vcmax_10pct", "gain_Jmax_10pct"):
                want = [BASE["leaf"][name][key][i] for i in idx]
                assert all(abs(a - b) < 1e-6 for a, b in zip(cells[name][key], want))


def test_readme_tables():
    for r in RATIO_ROWS:
        assert ratio_row(r) in README, ratio_row(r)
    for t in TEMPERATURE_ROWS:
        assert temperature_row(t) in README, temperature_row(t)


def test_ratio_window_and_floor():
    r = RES["ratio"]
    assert round(r["never_rubisco_limited_at_or_below_ratio"][AMB], 2) == 1.50
    assert round(r["never_rubisco_limited_at_or_below_ratio"][ELE], 2) == 1.92
    w = r["ratio_for_crossover_at_ppfd"][AMB]
    assert (round(w["2000"], 2), round(w["1500"], 2), round(w["1000"], 2)) == (1.65, 1.73, 1.95)
    assert "between 1.65 and 1.73" in README
    assert round(100 * (w["1500"] / w["2000"] - 1), 1) == 4.6 and "4.6 % wide" in README
    floor = r["lowest_possible_crossover_ppfd"]
    assert (light(floor[AMB]), light(floor[DRY])) == ("501", "418")
    assert "below 501 µmol" in README and "(418 on the droughted leaf)" in README
    # the floor is j_needed / alpha: the ratio sweep never goes under it
    for cells in r["by_ratio"].values():
        for name in (DRY, AMB, ELE):
            x = cells[name]["crossover_ppfd"]
            assert x is None or x > floor[name]


def test_alpha_and_theta():
    a, th = RES["alpha"], RES["theta"]
    xs = [a[k][AMB]["crossover_ppfd"] for k in ("0.24", "0.3", "0.36")]
    assert [light(x) for x in xs] == ["2298", "1839", "1532"]
    assert all(abs(x * float(k) - xs[1] * 0.3) < 0.1 for x, k in zip(xs, ("0.24", "0.3", "0.36")))  # exactly 1/alpha
    assert [light(th[k][AMB]["crossover_ppfd"]) for k in ("0.5", "0.7", "0.9")] == ["2731", "1839", "947"]
    assert "2298 / 1839 / 1532" in README and "2731 / 1839 / 947" in README
    assert pct(th["0.9"][AMB]["gain_Vcmax_10pct"][1]) == "+5.8 %" and "+5.8 %" in README


def test_temperature_reading():
    t = RES["temperature"]
    assert round(t["never_rubisco_limited_below_C"][AMB], 1) == 17.8
    assert round(t["never_rubisco_limited_below_C"][ELE], 1) == 32.0
    x = t["temperature_for_crossover_at_ppfd"][AMB]
    assert (round(x["2000"], 1), round(x["1500"], 1)) == (24.3, 27.4) and x["1000"] is None
    for s in ("Below 17.8 °C", "24.3 °C", "27.4 °C", "above 32 °C"):
        assert s in README, s
    by = t["by_temperature"]
    assert [pct(by[k][AMB]["gain_Vcmax_10pct"][1]) for k in TEMPERATURE_ROWS] == ["0", "0", "0", "+3.6 %", "+11.2 %"]
    assert pct(by["30"][AMB]["gain_Vcmax_10pct"][2]) == "+9.9 %"
    dry = [by[k][DRY]["crossover_ppfd"] for k in TEMPERATURE_ROWS]
    assert 785 <= min(dry) and max(dry) <= 875 and "785 and 875" in README
    assert [pct(by[k][DRY]["gain_Vcmax_10pct"][0]) for k in ("15", "25", "35")] == ["+1.9 %", "+7.7 %", "+12.0 %"]
    # the capacity ratio falls with temperature while the leaf moves towards Rubisco limitation
    ratios = [by[k]["Jmax_to_Vcmax"] for k in TEMPERATURE_ROWS]
    assert ratios == sorted(ratios, reverse=True)
    assert by["15"][AMB]["crossover_ppfd"] is None and by["35"][AMB]["crossover_ppfd"] < 1200
    assert (f"{ratios[0]:.2f}", f"{ratios[-1]:.2f}") == ("2.27", "1.26")
    assert "from 2.27 at 15 °C to 1.26 at 35 °C" in README
    need = [by[k][AMB]["J_needed_to_Vcmax"] for k in ("15", "35")]
    assert [f"{x:.2f}" for x in need] == ["2.31", "0.87"] and "from 2.31 to 0.87" in README
    assert need[0] > ratios[0] and need[1] < ratios[-1]            # RuBP-limited at 15 C, crossover at 35 C
    assert (light(by["15"]["Km"]), light(by["35"]["Km"])) == ("300", "1682")
    assert "rises from 300 to 1682" in README
    assert light(by["35"][ELE]["crossover_ppfd"]) == "4255" and "above 4255" in README
    assert all(by[k][ELE]["crossover_ppfd"] is None for k in ("15", "20", "25", "30"))


def test_ratio_two_point_zero():
    c = RES["ratio"]["by_ratio"]["2.0"][AMB]
    assert light(c["crossover_ppfd"]) == "953" and pct(c["gain_Vcmax_10pct"][1]) == "+10.6 %"
    assert "At 2.0 the crossover is at 953 and the same product is worth +10.6 % at 1500" in README
    assert RES["ratio"]["by_ratio"]["1.5"][AMB]["crossover_ppfd"] is None


def test_headline_is_qualified_in_place():
    assert "with these parameters at 25 °C" in README
    assert "What the 1839 rests on" in README


if __name__ == "__main__":
    for r in RATIO_ROWS:
        print(ratio_row(r))
    print()
    for t in TEMPERATURE_ROWS:
        print(temperature_row(t))
