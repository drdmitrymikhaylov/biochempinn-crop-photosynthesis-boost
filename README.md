# Biochem PINN — Modelling How Biostimulants Alter Photosynthesis and Nutrient Uptake in Crops

A biostimulant is sold on yield trials. Yield is the end of a long causal chain, which is why the same product works in one season and not the next: nobody models the step where the molecule acts.

This project models that step — photosynthetic carbon assimilation and nutrient uptake — instead of correlating dose against harvest.

**Status.** Concept stage. No code in this repository yet.

## The physics

- **Farquhar–von Caemmerer–Berry** photosynthesis: assimilation as the minimum of the Rubisco-limited and RuBP-regeneration-limited rates, with the Beer–Lambert absorption profile through the canopy.
- **Michaelis–Menten and Hill kinetics** for enzyme-mediated uptake and dose response.
- **Mass action and reaction–diffusion** for transport of the active compound to the site where it acts.

Constraining the network with these laws means the fitted parameters are quantities an agronomist can argue with — carboxylation capacity, uptake affinity — rather than regression coefficients.

## Source

Not public.
