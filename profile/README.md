# Complexity Economics

Agent-based modeling of AI-driven labor market transitions. Seven papers and 45,400+ Monte Carlo simulations exploring how universal basic income, monetary regimes, endogenous technology dynamics, household heterogeneity, and supply chain coupling interact to produce phase transitions in automation adoption.

![Automation cascade spreading through a firm network](network_cascade.gif)

## Research program

A stock-flow consistent agent-based model (SFC-ABM) with 10,000 heterogeneous firms and 100,000 individual households across 6 sectors, calibrated to the Polish economy (GUS 2024). The series progressively relaxes assumptions — from static parameters to endogenous technology, dynamic networks, and heterogeneous household agents — testing whether the core finding (a reentrant phase transition at BDP ~500 PLN) survives each extension, and what it hides.

## Methods

- **Agent-based modeling** with stock-flow consistent balance-sheet accounting
- **Phase transitions & critical phenomena** — bifurcation diagrams, susceptibility peaks, critical exponents
- **Finite-size scaling** and data collapse for universality class identification
- **Network science** — Watts-Strogatz, Erdos-Renyi, Barabasi-Albert topologies + endogenous rewiring
- **Empirical estimation** — GMM and hierarchical Bayesian (PyMC) on OECD panel data
- **Input-output analysis** — Leontief technical coefficient matrix calibrated from GUS symmetric I-O tables
- **Factorial experimental design** for mechanism isolation
- **Heterogeneous households** — 100,000 individual agents with savings, debt, skill decay, and health scarring
- **Monte Carlo robustness** — 30–100 seeds per parameter point across multi-dimensional sweeps

## Papers

| # | Repo | Title | Sims | DOI |
|---|------|-------|-----:|-----|
| 1 | [`paper-01-acceleration-paradox`](https://github.com/complexity-econ/paper-01-acceleration-paradox) | The Acceleration Paradox | 6,300 | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18727928.svg)](https://doi.org/10.5281/zenodo.18727928) |
| 2 | [`paper-02-monetary-regimes`](https://github.com/complexity-econ/paper-02-monetary-regimes) | PLN vs EUR with SGP Constraint | 1,260 | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18740933.svg)](https://doi.org/10.5281/zenodo.18740933) |
| 3 | [`paper-03-empirical-sigma`](https://github.com/complexity-econ/paper-03-empirical-sigma) | Empirical CES σ Estimation (OECD, GMM + Bayesian) | 120 | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18743780.svg)](https://doi.org/10.5281/zenodo.18743780) |
| 4 | [`paper-04-phase-diagram`](https://github.com/complexity-econ/paper-04-phase-diagram) | Phase Diagram & Universality | 18,540 | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18751083.svg)](https://doi.org/10.5281/zenodo.18751083) |
| 5 | [`paper-05-endogenous`](https://github.com/complexity-econ/paper-05-endogenous) | Endogenous Technology & Network Dynamics | 10,080 | [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18758365.svg)](https://doi.org/10.5281/zenodo.18758365) |
| 6 | [`paper-06-heterogeneous-households`](https://github.com/complexity-econ/paper-06-heterogeneous-households) | Heterogeneous Households & Limits of UBI | 1,500 | *pending* |
| 7 | [`paper-07-io-coupling`](https://github.com/complexity-econ/paper-07-io-coupling) | SFC-IO Sectoral Coupling: Three Propagation Channels | 3,630 | *pending* |

**Engine**: [`core`](https://github.com/complexity-econ/core) — reusable Scala 3 SFC-ABM engine (sbt)

## Key findings

- **Acceleration paradox**: moderate UBI *causes* automation rather than responding to it (Paper 1)
- **Monetary sovereignty matters**: PLN float permits the transition; EUR + SGP kills it (Paper 2)
- **σ calibration doesn't**: 5–9× change in elasticity shifts adoption by only 1.5 pp (Paper 3)
- **Topology universality**: BDP_c = 500 PLN across all four network topologies, mean-field γ ≈ 1.0 (Paper 4)
- **Endogenization preserves universality**: reentrant shape survives; BDP_c shifts by at most 250 PLN (Paper 5)
- **Aggregate metrics mask destruction**: BDP_c = 500 appears as a "sweet spot" in aggregates but is the point of peak bankruptcy (17.3%), peak poverty (45%), and peak income Gini (0.50) at the household level (Paper 6)
- **Scarring catch-22**: unemployment erodes skills and health, making retraining least effective for those who need it most — even doubled intensity yields only 18% success (Paper 6)
- **Supply chains are transformative**: I-O coupling at κ=0.50 boosts adoption from ~12% to ~43% (+30 pp); bell-shaped response with NPL-driven reversal at κ ≈ 0.75 (Paper 7)

## Tech Stack

![Scala](https://img.shields.io/badge/Scala_3-DC322F?logo=scala&logoColor=white)
![Python](https://img.shields.io/badge/Python_3-3776AB?logo=python&logoColor=white)
![LaTeX](https://img.shields.io/badge/XeLaTeX-008080?logo=latex&logoColor=white)
![sbt](https://img.shields.io/badge/sbt-1.10-blue)

## License

All repositories are released under the MIT License.
