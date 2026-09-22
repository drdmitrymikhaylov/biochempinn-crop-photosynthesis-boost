# Changelog

## 2026-09-22

- Added `analysis/fvcb_sensitivity.py` and `results/fvcb_sensitivity.json`: FvCB reference calculation of what a +10 % change in V<sub>cmax</sub> or J<sub>max</sub> is worth across light (100–2000 µmol m⁻² s⁻¹), C<sub>i</sub> (200 / 290 / 490) and a Beer–Lambert canopy of LAI 4. Headline: a well-watered leaf at ambient CO₂ is RuBP-limited up to 1839 µmol m⁻² s⁻¹, so a V<sub>cmax</sub> gain is worth 0 % there and +11 % on a droughted leaf in bright light. New README section with the table and a "what this does not show" paragraph; `tests/test_readme_numbers.py` (6 tests) pins the README to the JSON and the JSON to the script.
