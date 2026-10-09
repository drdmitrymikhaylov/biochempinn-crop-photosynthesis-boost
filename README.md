# Biochem PINN - Modelling How Biostimulants Alter Photosynthesis and Nutrient Uptake in Crops

A biostimulant is sold on yield trials. Yield is the end of a long causal chain. That is why the same product works in one season and not the next: nobody models the step where the molecule acts.

This project models that step, photosynthetic carbon assimilation and nutrient uptake, instead of correlating dose against harvest.

**Status.** Concept stage. The project code is not public. This repository holds the physics, reference calculations on published parameters (`analysis/`, `results/`, `tests/`), and results as they come.

## How it started

This work comes from the field. I run physics-informed crop models behind an AI-enabled biostimulant platform with pilots in Brazil, Zimbabwe, Kyrgyzstan, Uzbekistan, Saudi Arabia and the UAE, backed by a granted US patent on smart fertilizer delivery (US 12,439,844) and plant-physiology papers in *Plants* (2026) and *Agronomy* (2025, 2026). Growers and partners all ask the same thing: what is a treatment worth in the leaf, not just at harvest? This repository answers it with the photosynthesis equations themselves.

## Three laws and what they buy

- **Farquhar-von Caemmerer-Berry** photosynthesis. Assimilation is the minimum of the Rubisco-limited and RuBP-regeneration-limited rates, with a Beer-Lambert absorption profile through the canopy.
- **Michaelis-Menten and Hill kinetics** for enzyme-mediated uptake and dose response.
- **Mass action and reaction-diffusion** for transport of the active compound to the site where it acts.

Constraining the network with these laws means the fitted parameters are quantities an agronomist can argue with. They are carboxylation capacity and uptake affinity, not regression coefficients.

## Why a Vcmax gain can be worth nothing

Before any data, the FvCB model alone, with published parameters, already says why a dose-yield correlation cannot hold from one season to the next. Take a productive C3 leaf at 25 °C: V<sub>cmax</sub> = 100, J<sub>max</sub> = 167 µmol m⁻² s⁻¹, R<sub>d</sub> = 1.5, Bernacchi 2001 kinetics, α = 0.3, θ = 0.7. Then ask what a biostimulant that raises V<sub>cmax</sub> or J<sub>max</sub> by 10 % does to assimilation.

- A well-watered leaf at today's CO₂ is RuBP-regeneration-limited up to ~1840 µmol m⁻² s⁻¹, which is nearly full sun. A product that raises carboxylation capacity by 10 % changes its assimilation by **exactly nothing** at any light below that, and by 1 % at 2000. That light is where it is with these parameters at 25 °C, and it moves a long way when either changes: see [What the 1839 rests on](#what-the-1839-rests-on).
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

## What the 1839 rests on

The crossover light in the first bullet above comes out of four things the calculation holds fixed: the ratio J<sub>max</sub>:V<sub>cmax</sub> (1.67), the quantum yield α (0.3), the curvature θ (0.7) and the leaf temperature (25 °C). `analysis/fvcb_ratio_temperature.py` moves each one alone and `results/fvcb_ratio_temperature.json` holds every cell. Added 9 October 2026.

**The ratio.** At 25 °C. The gains are for the well-watered leaf at C<sub>i</sub> 290.

| J<sub>max</sub>:V<sub>cmax</sub> | RuBP-limited below PPFD, droughted | RuBP-limited below PPFD, well-watered | +10 % V<sub>cmax</sub> at 1000 / 1500 / 2000 | +10 % J<sub>max</sub> at 1000 / 1500 / 2000 |
|---|---|---|---|---|
| 1.5 | 1059 | never | 0 / 0 / 0 | +8.1 % / +9.1 % / +9.6 % |
| 1.6 | 874 | 2790 | 0 / 0 / 0 | +7.8 % / +7.1 % / +3.1 % |
| 1.67 | 797 | 1839 | 0 / 0 / +1.0 % | +7.6 % / +3.1 % / 0 |
| 1.8 | 707 | 1256 | 0 / +3.7 % / +8.4 % | +6.3 % / 0 / 0 |
| 1.9 | 662 | 1066 | 0 / +8.7 % / +10.6 % | +2.0 % / 0 / 0 |
| 2.0 | 629 | 953 | +1.7 % / +10.6 % / +10.6 % | 0 / 0 / 0 |
| 2.2 | 585 | 823 | +8.7 % / +10.6 % / +10.6 % | 0 / 0 / 0 |

The crossover sits between 1500 and 2000 only for a ratio between 1.65 and 1.73, a window 4.6 % wide. At 1.50 or below the well-watered leaf is RuBP-limited at every light, and a V<sub>cmax</sub> product is worth nothing anywhere. At 2.0 the crossover is at 953 and the same product is worth +10.6 % at 1500, where the table in the previous section says 0. This ratio differs between species and growing conditions by more than that window, so "worth exactly nothing below ~1840" describes one leaf, not well-watered crops.

The other two constants do the same. The crossover is exactly proportional to 1/α: 2298 / 1839 / 1532 for α = 0.24 / 0.30 / 0.36. For θ = 0.5 / 0.7 / 0.9 it is 2731 / 1839 / 947, and at θ = 0.9 the V<sub>cmax</sub> gain at 1500 is +5.8 %.

**Temperature.** The same leaf (ratio 1.67 at 25 °C) with Arrhenius scaling of V<sub>cmax</sub>, R<sub>d</sub>, Γ*, K<sub>c</sub>, K<sub>o</sub> (Bernacchi 2001) and J<sub>max</sub> (Bernacchi 2003), C<sub>i</sub> held.

| leaf temperature | J<sub>max</sub>:V<sub>cmax</sub> | RuBP-limited below PPFD, droughted | RuBP-limited below PPFD, well-watered | +10 % V<sub>cmax</sub>, well-watered, at 1000 / 1500 / 2000 | +10 % V<sub>cmax</sub>, droughted, at 1000 / 1500 / 2000 |
|---|---|---|---|---|---|
| 15 °C | 2.266 | 875 | never | 0 / 0 / 0 | +1.9 % / +6.2 % / +8.2 % |
| 20 °C | 1.940 | 838 | 5395 | 0 / 0 / 0 | +3.9 % / +10.4 % / +10.7 % |
| 25 °C | 1.670 | 797 | 1839 | 0 / 0 / +1.0 % | +7.7 % / +11.0 % / +11.0 % |
| 30 °C | 1.445 | 785 | 1312 | 0 / +3.6 % / +9.9 % | +11.3 % / +11.3 % / +11.3 % |
| 35 °C | 1.256 | 798 | 1152 | 0 / +11.2 % / +11.2 % | +12.0 % / +12.0 % / +12.0 % |

- Below 17.8 °C the well-watered leaf is RuBP-limited at every light. The crossover comes down through 2000 at 24.3 °C and through 1500 at 27.4 °C, so the 25 °C of the first calculation sits on the steep part of the curve.
- At 30 °C the V<sub>cmax</sub> product is worth +3.6 % at 1500 and +9.9 % at 2000 on a well-watered leaf, and at 35 °C +11.2 % from 1500 up. Heat does to the well-watered leaf what drought does.
- The capacity ratio falls with temperature, from 2.27 at 15 °C to 1.26 at 35 °C, and the leaf still moves towards Rubisco limitation. The electron transport a Rubisco-limited leaf needs per unit of V<sub>cmax</sub> falls faster, from 2.31 to 0.87, because Rubisco's effective K<sub>m</sub> for CO₂ rises from 300 to 1682 µmol mol⁻¹.
- The droughted leaf's crossover hardly moves, staying between 785 and 875. What the product is worth there at 1000 does move: +1.9 % at 15 °C, +7.7 % at 25 °C, +12.0 % at 35 °C. A +10 % gain is collected in full only where the RuBP-limited rate exceeds the Rubisco-limited one by more than 10 %.
- At C<sub>a</sub> 700 Rubisco limitation appears only above 32 °C, and then only above 4255 µmol m⁻² s⁻¹, a light no leaf sees.

**What survives.** Electron transport cannot exceed α times the light, so below 501 µmol m⁻² s⁻¹ (418 on the droughted leaf) no J<sub>max</sub>:V<sub>cmax</sub> ratio makes Rubisco limiting: "a V<sub>cmax</sub> gain is worth nothing in dim light" does not depend on the ratio. The direction also holds in every sweep: drought, heat and bright light push the leaf towards Rubisco limitation, while cool, well-watered, dim or CO₂-enriched conditions push it towards RuBP regeneration. What does not survive is the number 1839, and with it "nearly full sun".

**What this does not show.** Each choice is moved alone, so there is no joint uncertainty here. The temperature sweep uses one activation energy for J<sub>max</sub> and no deactivation above the optimum. With one, J<sub>max</sub> falls off in heat and the crossover moves back up, which is why the sweep stops at 35 °C. α and θ are held as temperature changes. C<sub>i</sub> is held too, although hot air is usually dry air, stomata close and C<sub>i</sub> falls, which pushes the same way. There is no acclimation: a leaf grown warm has a different ratio from one grown cool. The canopy calculation is not redone.

## Caveats

The grid in the reference calculation is for one leaf type at one temperature with textbook parameters; the section above moves the temperature and three of the parameters one at a time. There is no triose-phosphate-utilisation limit and no stomatal model (C<sub>i</sub> is prescribed). The canopy is layered without a sun/shade split, which overstates absolute canopy assimilation, so use the fractional gains and not the µmol figures. The calculation also assumes the biostimulant acts on one capacity cleanly. Whether it does is what the project is for.

## Where the time went

The reference calculation went in on 22 September 2026, as `analysis/fvcb_sensitivity.py` plus the JSON it writes. I ran a +10 % change in V<sub>cmax</sub> and in J<sub>max</sub> across light from 100 to 2000 µmol m⁻² s⁻¹, three values of C<sub>i</sub> (200 / 290 / 490), and a Beer-Lambert canopy of LAI 4. The headline came out of that grid: a well-watered leaf at ambient CO₂ stays RuBP-limited up to 1839 µmol m⁻² s⁻¹, so a V<sub>cmax</sub> gain is worth 0 % there and +11 % on a droughted leaf in bright light. The same day I added `tests/test_readme_numbers.py`, six tests that pin the README table to the JSON and the JSON to the script, so that neither can drift on its own.

## Source

Not public.

## Licence

Documentation, figures and result files in this repository: CC BY 4.0. Source code is held in a private repository, all rights reserved, and is available under NDA. See `LICENSE`.
