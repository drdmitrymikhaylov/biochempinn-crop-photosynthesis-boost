"""Pins the numbers quoted in README to results/fvcb_sensitivity.json, and the JSON
to the script, so neither can drift silently.  Run: python -m pytest tests/
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = json.loads((ROOT / "results" / "fvcb_sensitivity.json").read_text())
PPFD = RES["parameters"]["PPFD"]
i1000, i1500, i2000, i800 = (PPFD.index(v) for v in (1000, 1500, 2000, 800))


def test_script_reproduces_json(tmp_path):
    """The committed JSON is what the committed script writes."""
    src = (ROOT / "analysis" / "fvcb_sensitivity.py").read_text()
    out = tmp_path / "results" / "fvcb_sensitivity.json"
    patched = src.replace('OUT = Path(__file__).resolve().parents[1] / "results" / "fvcb_sensitivity.json"',
                          f'OUT = Path(r"{out}")')
    assert patched != src
    (tmp_path / "run.py").write_text(patched)
    subprocess.run([sys.executable, str(tmp_path / "run.py")], check=True, capture_output=True)
    assert json.loads(out.read_text()) == RES


def test_crossover_ppfd():
    x = RES["crossover_ppfd"]
    assert round(x["drought_Ci_200"]) == 797
    assert round(x["ambient_Ci_290"]) == 1839
    assert x["elevated_Ci_490"] is None


def test_leaf_gains_table():
    L = RES["leaf"]
    d, a, e = L["drought_Ci_200"], L["ambient_Ci_290"], L["elevated_Ci_490"]
    assert [round(100 * d["gain_Vcmax_10pct"][i], 1) for i in (i1000, i1500, i2000)] == [7.7, 11.0, 11.0]
    assert [d["gain_Jmax_10pct"][i] for i in (i1000, i1500, i2000)] == [0.0, 0.0, 0.0]
    assert [round(100 * a["gain_Vcmax_10pct"][i], 1) for i in (i1000, i1500, i2000)] == [0.0, 0.0, 1.0]
    assert [round(100 * a["gain_Jmax_10pct"][i], 1) for i in (i1000, i1500, i2000)] == [7.6, 3.1, 0.0]
    assert [e["gain_Vcmax_10pct"][i] for i in (i1000, i1500, i2000)] == [0.0, 0.0, 0.0]
    assert [round(100 * e["gain_Jmax_10pct"][i], 1) for i in (i1000, i1500, i2000)] == [7.6, 8.7, 9.3]


def test_vcmax_gain_is_zero_below_crossover_ambient():
    a = RES["leaf"]["ambient_Ci_290"]
    assert all(g == 0.0 for I, g in zip(PPFD, a["gain_Vcmax_10pct"]) if I < 1839)
    assert all(lim == "RuBP" for I, lim in zip(PPFD, a["limiting"]) if I < 1839)


def test_drought_gain_exceeds_ten_percent_because_of_rd():
    d = RES["leaf"]["drought_Ci_200"]
    p = RES["parameters"]
    a1500 = d["A"][i1500]
    gross = a1500 + p["Rd"]
    assert abs(d["gain_Vcmax_10pct"][i1500] - 0.1 * gross / a1500) < 5e-4
    assert d["gain_Vcmax_10pct"][i1500] > 0.10


def test_canopy_gains():
    c = RES["canopy"]
    amb, dr = c["ambient_Ci_290"], c["drought_Ci_200"]
    assert max(amb["gain_Jmax_10pct"]) == amb["gain_Jmax_10pct"][i1500]
    assert round(100 * amb["gain_Jmax_10pct"][i1500], 1) == 5.3
    assert max(amb["gain_Vcmax_10pct"]) < 0.0005  # 0.03 % at 2000, zero below
    assert round(100 * dr["gain_Vcmax_10pct"][i2000], 1) == 4.8
    assert round(100 * dr["gain_Vcmax_10pct"][i1000], 1) == 0.7
    assert all(g < 1e-5 for I, g in zip(PPFD, dr["gain_Vcmax_10pct"]) if I <= 800)
