# Biochem PINN — Modelling How Biostimulants Alter Photosynthesis and Nutrient Uptake in Crops

A biostimulant is sold on yield trials. Yield is the end of a long causal chain, which is why the same product works in one season and not the next: nobody models the step where the molecule acts.

This project models that step — photosynthetic carbon assimilation and nutrient uptake — instead of correlating dose against harvest.

**Status.** Concept stage. The project code is not public; this repository holds the physics, reference calculations on published parameters (`analysis/`, `results/`, `tests/`), and results as they come.

## The physics

- **Farquhar–von Caemmerer–Berry** photosynthesis: assimilation as the minimum of the Rubisco-limited and RuBP-regeneration-limited rates, with the Beer–Lambert absorption profile through the canopy.
- **Michaelis–Menten and Hill kinetics** for enzyme-mediated uptake and dose response.
- **Mass action and reaction–diffusion** for transport of the active compound to the site where it acts.

Constraining the network with these laws means the fitted parameters are quantities an agronomist can argue with — carboxylation capacity, uptake affinity — rather than regression coefficients.

## What a 10 % gain in capacity is worth, and when

Before any data: the FvCB model alone, with published parameters, already says why a dose–yield correlation cannot hold from one season to the next. Take a productive C3 leaf at 25 °C (V<sub>cmax</sub> = 100, J<sub>max</sub> = 167 µmol m⁻² s⁻¹, R<sub>d</sub> = 1.5; Bernacchi 2001 kinetics; α = 0.3, θ = 0.7) and ask what a biostimulant that raises V<sub>cmax</sub> or J<sub>max</sub> by 10 % does to assimilation. `analysis/fvcb_sensitivity.py` computes it; `results/fvcb_sensitivity.json` holds the full grid.

| leaf, C<sub>i</sub> (µmol mol⁻¹) | RuBP-limited below PPFD | +10 % V<sub>cmax</sub> at 1000 / 1500 / 2000 | +10 % J<sub>max</sub> at 1000 / 1500 / 2000 |
|---|---|---|---|
| 200 (droughted, C<sub>a</sub> 420) | 797 | +7.7 % / **+11.0 %** / +11.0 % | 0 / 0 / 0 |
| 290 (well-watered, C<sub>a</sub> 420) | 1839 | 0 / 0 / +1.0 % | **+7.6 %** / +3.1 % / 0 |
| 490 (well-watered, C<sub>a</sub> 700) | never | 0 / 0 / 0 | +7.6 % / +8.7 % / +9.3 % |

Gains are the fractional change in net A for that leaf and light; PPFD in µmol photons m⁻² s⁻¹.

- A well-watered leaf at today's CO₂ is RuBP-regeneration-limited up to ~1840 µmol m⁻² s⁻¹ — nearly full sun. A product that raises carboxylation capacity by 10 % changes its assimilation by **exactly nothing** at any light below that, and by 1 % at 2000.
- The same product on a droughted leaf (stomata pulling C<sub>i</sub> to 200) is worth **+11 %** from 1500 µmol m⁻² s⁻¹ up (+7.7 % at 1000) — more than the 10 % it added, because respiration is subtracted after the gain.
- A product acting on electron transport does the opposite: +7.6 % on the well-watered leaf at 1000, zero on the droughted one in bright light.
- Over a canopy of LAI 4 (Beer–Lambert, k = 0.5), the two limitations coexist at different depths and both gains shrink: the J<sub>max</sub> gain at ambient CO₂ peaks at +5.3 % (PPFD 1500), the V<sub>cmax</sub> gain under drought reaches +4.8 % only at 2000, is +0.7 % at 1000 and zero at 800 and below.

So the same molecule, at the same dose, is worth 0 % or 11 % depending on the week's weather and the soil's water — before any biology of the product itself is considered. Fitting dose against yield averages over exactly this, which is the case for fitting the mechanism instead.

**What this does not show.** It is a one-leaf-type, one-temperature calculation with textbook parameters, no triose-phosphate-utilisation limit, no stomatal model (C<sub>i</sub> is prescribed), and a layered canopy without a sun/shade split, which overstates absolute canopy assimilation — use the fractional gains, not the µmol figures. It also assumes the biostimulant acts on one capacity cleanly; whether it does is what the project is for.

## Source

Not public.
