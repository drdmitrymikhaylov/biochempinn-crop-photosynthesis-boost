# Biochem PINN - Modelling How Biostimulants Alter Photosynthesis and Nutrient Uptake in Crops

A biostimulant is sold on yield trials. Yield is the end of a long causal chain. That is why the same product works in one season and not the next: nobody models the step where the molecule acts.

This project models that step, photosynthetic carbon assimilation and nutrient uptake, instead of correlating dose against harvest.

**Status.** Concept stage. The project code is not public. This repository holds the physics, reference calculations on published parameters (`analysis/`, `results/`, `tests/`), and results as they come.

## Three laws and what they buy

- **Farquhar-von Caemmerer-Berry** photosynthesis. Assimilation is the minimum of the Rubisco-limited and RuBP-regeneration-limited rates, with a Beer-Lambert absorption profile through the canopy.
- **Michaelis-Menten and Hill kinetics** for enzyme-mediated uptake and dose response.
- **Mass action and reaction-diffusion** for transport of the active compound to the site where it acts.

Constraining the network with these laws means the fitted parameters are quantities an agronomist can argue with. They are carboxylation capacity and uptake affinity, not regression coefficients.

## Why a Vcmax gain can be worth nothing

Before any data, the FvCB model alone, with published parameters, already says why a dose-yield correlation cannot hold from one season to the next. Take a productive C3 leaf at 25 °C: V<sub>cmax</sub> = 100, J<sub>max</sub> = 167 µmol m⁻² s⁻¹, R<sub>d</sub> = 1.5, Bernacchi 2001 kinetics, α = 0.3, θ = 0.7. Then ask what a biostimulant that raises V<sub>cmax</sub> or J<sub>max</sub> by 10 % does to assimilation.

- A well-watered leaf at today's CO₂ is RuBP-regeneration-limited up to ~1840 µmol m⁻² s⁻¹, which is nearly full sun. A product that raises carboxylation capacity by 10 % changes its assimilation by **exactly nothing** at any light below that, and by 1 % at 2000.
- The same product on a droughted leaf, with stomata pulling C<sub>i</sub> to 200, is worth **+11 %** from 1500 µmol m⁻² s⁻¹ up (+7.7 % at 1000). That is more than the 10 % it added, because respiration is subtracted after the gain.
- A product acting on electron transport does the opposite: +7.6 % on the well-watered leaf at 1000, zero on the droughted one in bright light.
- Over a canopy of LAI 4 (Beer-Lambert, k = 0.5), the two limitations coexist at different depths and both gains shrink. The J<sub>max</sub> gain at ambient CO₂ peaks at +5.3 % (PPFD 1500). The V<sub>cmax</sub> gain under drought reaches +4.8 % only at 2000, is +0.7 % at 1000, and is zero at 800 and below.

So the same molecule, at the same dose, is worth 0 % or 11 % depending on the week's weather and the soil's water. That is before any biology of the product itself is considered. Fitting dose against yield averages over exactly this, which is the case for fitting the mechanism instead.

## Reference calculation

`analysis/fvcb_sensitivity.py` computes the numbers above and `results/fvcb_sensitivity.json` holds the full grid.

| leaf, C<sub>i</sub> (µmol mol⁻¹) | RuBP-limited below PPFD | +10 % V<sub>cmax</sub> at 1000 / 1500 / 2000 | +10 % J<sub>max</sub> at 1000 / 1500 / 2000 |
|---|---|---|---|
| 200 (droughted, C<sub>a</sub> 420) | 797 | +7.7 % / **+11.0 %** / +11.0 % | 0 / 0 / 0 |
| 290 (well-watered, C<sub>a</sub> 420) | 1839 | 0 / 0 / +1.0 % | **+7.6 %** / +3.1 % / 0 |
| 490 (well-watered, C<sub>a</sub> 700) | never | 0 / 0 / 0 | +7.6 % / +8.7 % / +9.3 % |

Gains are the fractional change in net A for that leaf and light. PPFD is in µmol photons m⁻² s⁻¹.

## Caveats

This is a one-leaf-type, one-temperature calculation with textbook parameters. There is no triose-phosphate-utilisation limit and no stomatal model (C<sub>i</sub> is prescribed). The canopy is layered without a sun/shade split, which overstates absolute canopy assimilation, so use the fractional gains and not the µmol figures. The calculation also assumes the biostimulant acts on one capacity cleanly. Whether it does is what the project is for.

## Where the time went

The reference calculation went in on 22 September 2026, as `analysis/fvcb_sensitivity.py` plus the JSON it writes. I ran a +10 % change in V<sub>cmax</sub> and in J<sub>max</sub> across light from 100 to 2000 µmol m⁻² s⁻¹, three values of C<sub>i</sub> (200 / 290 / 490), and a Beer-Lambert canopy of LAI 4. The headline came out of that grid: a well-watered leaf at ambient CO₂ stays RuBP-limited up to 1839 µmol m⁻² s⁻¹, so a V<sub>cmax</sub> gain is worth 0 % there and +11 % on a droughted leaf in bright light. The same day I added `tests/test_readme_numbers.py`, six tests that pin the README table to the JSON and the JSON to the script, so that neither can drift on its own.

## Source

Not public.

## Licence

Documentation, figures and result files in this repository: CC BY 4.0. Source code is held in a private repository, all rights reserved, and is available under NDA. See `LICENSE`.
