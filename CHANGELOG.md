# Changelog

## 2026-10-19

- LICENSE now holds the standard CC BY 4.0 legal text, so GitHub recognises the licence (it showed "Other" before). The terms are unchanged; the note on what each licence covers moved to `NOTICE.md`.

## 2026-10-09

- Added `analysis/fvcb_ratio_temperature.py` and `results/fvcb_ratio_temperature.json`: the light below which the well-watered leaf is RuBP-limited (1839 µmol m⁻² s⁻¹ in the first calculation) re-computed with each fixed choice moved alone. J<sub>max</sub>:V<sub>cmax</sub> 1.5 / 1.67 / 2.0 gives never / 1839 / 953; the crossover is between 1500 and 2000 only for a ratio of 1.65–1.73. α 0.24–0.36 gives 2298–1532, θ 0.5–0.9 gives 2731–947. Leaf temperature 15–35 °C (Bernacchi 2001 and 2003 activation energies): RuBP-limited at every light below 17.8 °C, crossover 1312 at 30 °C and 1152 at 35 °C, so a +10 % V<sub>cmax</sub> gain on a well-watered leaf at 1500 is worth 0 at 25 °C, +3.6 % at 30 °C and +11.2 % at 35 °C. What does not move: below 501 µmol m⁻² s⁻¹ no ratio makes Rubisco limiting. New README section "What the 1839 rests on" with both tables and a "what this does not show" paragraph; the first bullet of the headline now says it is a 25 °C statement. `tests/test_ratio_temperature.py` (8 tests) pins the section to the JSON, the JSON to the script and its base point to the first calculation.
- Removed three macOS `._*` files that had been committed; `._*` is now ignored.

## 2026-09-22

- Added `analysis/fvcb_sensitivity.py` and `results/fvcb_sensitivity.json`: FvCB reference calculation of what a +10 % change in V<sub>cmax</sub> or J<sub>max</sub> is worth across light (100–2000 µmol m⁻² s⁻¹), C<sub>i</sub> (200 / 290 / 490) and a Beer–Lambert canopy of LAI 4. Headline: a well-watered leaf at ambient CO₂ is RuBP-limited up to 1839 µmol m⁻² s⁻¹, so a V<sub>cmax</sub> gain is worth 0 % there and +11 % on a droughted leaf in bright light. New README section with the table and a "what this does not show" paragraph; `tests/test_readme_numbers.py` (6 tests) pins the README to the JSON and the JSON to the script.
