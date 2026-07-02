# Machine Learning Interatomic Potentials for Electrocatalysis — Literature Review
*40 papers cited | 2026-07-02 | window: 2021–2026*
> Built from titles, abstracts, and metadata (not full text). † marks sources for which no abstract was retrieved — claims rest on title and metadata only.

## Overview

Machine learning interatomic potentials (MLIPs) have emerged as a transformative approach for atomistic simulations in electrocatalysis, promising DFT-level accuracy at a fraction of the computational cost [1][2]. The field has undergone a paradigm shift from bespoke, system-specific force fields to universal pre-trained models (uMLIPs) that can be fine-tuned for targeted applications [3][4]. This review covers 40 papers retrieved across 7 sub-questions, organized into thematic clusters: dominant architectures, electrochemical interface modeling, accuracy benchmarks, electrocatalytic reaction applications, training data strategies, and open challenges.

The central tension running through the literature is between the accelerating development of increasingly capable MLIP architectures — particularly E(3)-equivariant graph neural networks — and the persistent difficulty of capturing the intrinsic complexities of electrochemical systems: solvent dynamics, the electric double-layer (EDL), applied potential, pH, and charge transfer [5][6][7]. Two "must-read" papers frame this landscape: Zhu & Cheng (2025, *PRL*) on a hybrid dielectric-response MLP for metal-electrolyte interfaces [8], and the systematic 80-MLIP zero-shot benchmark by Kempen et al. (2025, *J. Chem. Phys.*) that reveals catastrophic failures on magnetic materials and surface relaxation tasks [9].

## Your prior notes in this area

The intelligent-notes vault contains 24 notes relevant to this review, providing substantial prior context:

**By you (user):**
- [[MLaMD — Explicit Solvent on Heterogeneous Catalysts via On-the-Fly MLIPs]] — explicit-solvent MLIPs with active learning on Cu/water interfaces for CO₂RR intermediates
- [[Electrocatalytic Oxidation of Ammonia to Nitrate on NiOOH]] — electrocatalysis DFT study relevant as an example system for MLIPs to model
- [[Autocatalysis Architecture]] — documents the >2 eV MLIP-NEB accuracy wall for TS barriers
- 4 post logs (Trust Gap, Phase Gap, Screening Then Specialists, CO₂ Routes) tracing MLIP reliability concerns
- 2 weekly scans (Weeks 18, 20) on electrochemical interface gaps and MACE fine-tuning
- 4 research briefings (Weeks 11–14) flagging electrostatic MLIPs, water-in-salt electrolytes, and self-consistent MLIPs

**By other skills:**
- [[UMA — Universal Model for Atoms Family]] — Meta FAIR's eSEN-based universal MLIP family
- [[CARE Framework]] — documents >2 eV MAE on TS barriers for general-purpose MLIPs
- [[Fine-tuning Universal MLPs for Transition State Search]] — workflow to reduce MAE for DFT-quality TS barriers
- [[Bias in Universal MLIPs and Fine-Tuning]] — propagation of model biases through fine-tuning
- [[MoE MLIPs]] — element-wise routing for scaling MLIP architectures
- [[Proof-Carrying Materials]] — single-MLIP stability screening misses 93% of DFT-stable materials
- [[Agentic MLIP Workflows]] — pipeline design for MLIP-accelerated catalysis screening

## Architectural Foundations: Equivariant GNNs and Universal Models

The architectural landscape of MLIPs for electrocatalysis is dominated by E(3)-equivariant message-passing graph neural networks. NequIP, introduced by Batzner et al. (2022), established the paradigm by using equivariant convolutions operating on geometric tensors rather than invariant scalars, achieving state-of-the-art accuracy on molecular and materials benchmarks with up to three orders of magnitude greater data efficiency than prior approaches [10]. This was rapidly extended by MACE (multi-atomic cluster expansion), which combines the body-order-aware ACE formalism with message-passing to capture higher-order many-body interactions [11], and by Allegro, a strictly local equivariant architecture [12].

Systematic architectural benchmarks consistently identify equivariant, message-passing GNNs as forming the Pareto front in the accuracy-versus-cost trade-off. Leimeroth et al. (2025) compared NequIP, MACE, Allegro, and nonlinear ACE across chemically complex solids (Al-Cu-Zr, Si-O), finding that MACE and Allegro offer the highest accuracy for alloys while NequIP leads for oxides [13]. A comprehensive Chemical Reviews survey by Kim et al. (2026) traces this evolution from descriptor-based models (BPNN, HDNNPs) to the current state of the art, identifying equivariant GNNs as the necessary foundation for reactive MLIP applications [14].

The shift toward universal pre-trained models has been driven by architectures such as CHGNet [15] and the broader family of Foundation MLIPs. CHGNet, trained on the MPtrj dataset, achieves mean absolute errors of 30 meV/atom for energy and 77 meV/Å for force, and historically included magnetic moment prediction — a capability that later studies have shown to be critical for catalytic applications [9][15]. The UMA family from Meta FAIR uses a Mixture of Linear Experts (MoLE) architecture built on eSEN equivariant GNNs, spanning model sizes from 6M (UMA-S) to 50M (UMA-M) active parameters, achieving state-of-the-art results on OC20, Matbench Discovery, and OMat24 benchmarks [16]. MoE-based scaling strategies represent a promising direction: Liu et al. (2025) demonstrated that element-wise routing — where experts specialize in periodic table groups — outperforms configuration-level routing, achieving substantial accuracy gains across multiple benchmarks [17].

However, a critical finding across the literature is that no single MLIP architecture is universally best. The CLAM model, specifically designed for heterogeneous catalysis, achieves 94% of adsorption energy predictions within 1 kcal/mol of DFT on transition metal surfaces through local fine-tuning [18]. Yet the same models that excel at adsorption energies may fail catastrophically on magnetic oxides or catalytic transition states [9][19].

## Electrochemical Interfaces: Solvent, EDL, and Applied Potential

Modeling the electrochemical interface remains the most significant frontier for MLIPs in electrocatalysis. Conventional MLIPs trained on bulk DFT data do not incorporate applied potential, explicit solvent dynamics, or the dielectric response of the electrode-electrolyte interface — all essential for predictive electrocatalysis simulations. Several complementary approaches have emerged since 2023.

**Constant-potential methods.** The most active area of development is grand-canonical MLFFs that treat the number of electrons (or excess charge) as a learnable input. Wang et al. (2025) introduced CP-MLFF, implemented within MACE, which takes electron count as input and predicts the Fermi level, enabling constant-potential molecular dynamics for electrochemical barriers [20]. This was validated on CO₂ reduction at Ni-N-C catalysts, demonstrating sampling convergence for electrochemical reaction barriers. The CPMPNN architecture by Chen et al. (2025) extends this to E(3)-equivariant message passing with a global excess-charge parameter redistributed via multi-head attention, achieving three orders of magnitude speedup over grand-canonical DFT [7]. Applied to CO dimerization (CO₂RR) and the Volmer step (HER) on Cu(100), CPMPNN captures how applied potential modulates reaction thermodynamics, charge distribution, and transition-state structures.

A complementary approach, DPχ, adopts a Bader-basin-centroid representation that decomposes interfacial charge into neural-predicted chemical and conductor components, enabling constant-potential dynamics via a Siepmann-Sprik-type polarizable-electrode model [21]. On Pt(111)-H₂O, DPχ reproduces DFT forces, electrode potential, hydrogen evolution barriers, and vibrational spectra at scales 10³–10⁴ beyond AIMD.

**Hybrid dielectric response.** Zhu & Cheng (2025) proposed a fundamentally different approach: a hybrid MLP framework that unifies the dielectric response of electrolytes (via Wannier centroid-based local polarization) and metal electrodes (via nonlocal charge transfer) [8]. This ec-MLP reproduces the bell-shaped differential Helmholtz capacitance at Pt(111)-electrolyte interfaces without explicit charge equilibration, providing a physically grounded route to modeling potentio-controlled interfaces.

**Transfer-learning for constant-potential.** The TRECI workflow (Bianchi et al., 2025) leverages transfer learning from general-purpose and domain-specific models to construct accurate grand-canonical ML-FFs with explicit solvent using as few as 1,000 reference configurations [22]. Applied to Cu(111)/water, it captures bias-dependent solvent restructuring not previously reported, demonstrating that data-efficient constant-potential modeling is achievable.

**Explicit solvent and EDL structure.** Beyond potential control, several studies address the molecular structure of the electrochemical double layer explicitly. Wang et al. (2025) introduced an MLIP framework incorporating long-range electrostatics that enables nanosecond simulations of Pt(111)/water and Pt(111)/KF interfaces under applied bias [5]. This revealed proton-transfer mechanisms underlying anodic water dissociation and ion-specific effects (K⁺, F⁻) on capacitance. Tian et al. (2025) used ML-accelerated MD within a grand-canonical DFT framework to show that applied potential reshapes interfacial water orientation and H-bond network at Ag(111)/H₂O, directly modulating CO₂ reduction kinetics [6]. The MLaMD approach (Chen, Zhang & Zhang, 2023) demonstrated on-the-fly MLIPs (Moment Tensor Potential + MaxVol active learning) accelerating explicit-solvent MD by four orders of magnitude on Cu/water interfaces for CO₂RR intermediates, revealing that implicit solvation discrepancies are species-dependent [23].

A notable gap across these approaches is that **pH dependence is essentially absent** from current models. None of the recovered papers systematically treat pH as a tunable parameter — a major limitation for predicting electrocatalytic activity under realistic operating conditions.

## Accuracy Benchmarks: How Well Do MLIPs Reproduce DFT?

Systematic benchmarking reveals a nuanced picture of MLIP accuracy for electrocatalytic applications. The most comprehensive study to date, by Kempen et al. (2025), evaluates 80 foundational MLIPs in zero-shot mode on catalysis-relevant tasks including adsorption and reaction on alloyed metals, oxides, and metal-oxide interfaces [9]. Key findings: current-generation MLIPs achieve high accuracy for vacancy formation energies of perovskite oxides and zero-point energies of supported nanoclusters, but many **catastrophically fail on magnetic materials**, and structure relaxation in the MLIP generally increases error compared to single-point evaluation on pre-optimized structures.

**Energy and force errors.** Universal MLIPs — CHGNet, M3GNet, MACE-MP-0 — achieve ~30–80 meV/atom energy MAE and ~57–77 meV/Å force MAE on validation test sets [15][24]. However, Deng et al. (2025) demonstrated a systematic potential energy surface (PES) softening across all three uMLIPs, characterized by energy and force underprediction on surfaces, defects, solid-solution energetics, ion migration barriers, and high-energy states [24]. This "softening" originates from biased sampling of near-equilibrium atomic arrangements in pre-training datasets — a structural limitation with direct consequences for electrocatalytic applications that require accurate barriers and off-equilibrium configurations.

**Reaction barriers and adsorption energies.** The accuracy gap widens substantially for reaction barriers. Pretrained uMLIPs in zero-shot mode show a mean absolute error of 0.38 eV for catalytic reaction energies, which can be reduced to 0.09 eV through fine-tuning with only 10–30% of the data required for training from scratch [3]. The CARE framework, which benchmarked 91 MLIPs for NEB-based transition-state search, found that general-purpose models (EquiformerV2, MACE-MP-0) give **MAE >2 eV for activation energies**, because training data are predominantly near-equilibrium structures [19]. Fine-tuning strategies that incorporate perturbed high-energy configurations — including a workflow for CO₂ hydrogenation reaction networks with ~8 DFT single-point calculations per TS [25] — demonstrate that domain-specific retraining can close this gap.

For adsorption energies — a key descriptor in electrocatalyst screening — dedicated models like CLAM achieve 94% within 1 kcal/mol of DFT after local fine-tuning [18], while CatBench (Moon et al., 2025) provides a dedicated framework for benchmarking MLIP adsorption energy predictions with systematic evaluation across extensive reaction datasets [26].

**Validation methodology.** Foundational work by Morrow et al. (2023) established best practices for MLIP validation: k-fold cross-validation, external test sets, physically-guided tests, and comparison to experimental data [27]. Yet Liu et al. (2023) showed that standard RMSE/MAE metrics are insufficient for dynamics — rare-event-based metrics reveal discrepancies in atomistic dynamics, defects, and rare events that averaged errors mask [28]. The MS25 benchmark (Maxson et al., 2025) explicitly validates derived physical observables (lattice constants, volumes, reaction barriers) beyond energy/force errors, demonstrating that low errors in energy and force do not guarantee reliable observables [29].

## Electrocatalytic Reactions Explored with MLIPs

Applications of MLIPs to specific electrocatalytic reactions remain relatively sparse but are growing rapidly. The coverage across reactions is uneven.

**Hydrogen Evolution Reaction (HER).** The most-studied reaction, with approaches spanning constant-potential MLFFs, explicit solvent, and nuclear quantum effects. The CPMPNN framework captures the Volmer step on Cu(100) under applied potential [7]; DPχ reproduces HER barriers on Pt(111) [21]; and Sun et al. (2025) developed a grand-canonical constant-potential framework incorporating nuclear quantum effects, demonstrating that wave-like proton tunneling reduces activation energy compared to classical simulations at room temperature [30].

**Carbon Dioxide Reduction (CO₂RR).** Several studies address CO₂ electroreduction using MLIPs. Tian et al. (2025) showed potential-dependent water dynamics at Ag(111)/H₂O controls CO₂ reduction kinetics [6]; CP-MLFF was validated on CO₂ reduction at Ni-N-C catalysts [20]; and CPMPNN captures CO dimerization on Cu(100) as a function of applied potential [7]. However, the C-C coupling step and proton-coupled electron transfer (PCET) reactions remain identified as beyond current MLIP capabilities in the vault's autocatalysis architecture notes.

**Oxygen Evolution Reaction (OER).** The OC22 dataset specifically targets oxide electrocatalysts for OER [31], providing training and benchmark data for graph neural networks on 62,331 DFT relaxations across oxide materials. Specific OER applications include studies of Ni-doped BaTiO₃ and Ru multicomponent alloys, though detailed MLIP-MD studies remain limited.

**Urea synthesis.** Wu et al. (2024) applied a constant-potential method with implicit solvent to electrochemical coupling of nitrite and CO₂ on Cu surfaces, demonstrating that working electrode potential and EDL capacitance are key determinants of reaction mechanism and activity — one of the few studies to explicitly include potential effects in the reaction pathway analysis [32].

## Open Problems and What's Missing

The literature converges on several critical gaps that must be addressed for MLIPs to become reliable tools for electrocatalytic simulation:

- **Transferability across chemical and electrochemical space** remains the most frequently cited limitation. Foundational MLIPs that excel on bulk crystals can catastrophically fail on magnetic materials, oxide surfaces, or metal-oxide interfaces [9][24]. The TEA Challenge 2023 blind test confirmed that MLFFs struggle with multi-component systems and complex periodic structures [33], while MLIP Arena identified data leakage and limited transferability as systematic failure modes [34].

- **pH dependence is essentially unmodeled.** Despite the central role of pH in electrocatalysis — affecting Pourbaix stability, reaction mechanisms, and selectivity — none of the papers recovered in this review treat pH as a tunable parameter in MLIP frameworks. This represents a fundamental gap for predictive modeling of realistic electrochemical conditions.

- **Transition state barriers are systematically overestimated** by general-purpose MLIPs (>2 eV MAE) because saddle-point configurations are underrepresented in training data [19]. While fine-tuning strategies can reduce this to ~0.09 eV for reaction energies [3], the transferability of fine-tuned models to unseen TS configurations remains unvalidated.

- **Standard error metrics are insufficient for dynamics.** Low RMSE on energies and forces does not guarantee accurate atomistic dynamics, rare events, or derived observables [28][29]. The field lacks electrocatalysis-specific validation protocols that go beyond energy/force benchmarks — the emerging CatBench [26] and constant-potential validation in CP-MLFF [20] are steps in the right direction.

- **Long-range electrostatics and charge transfer** remain challenging for local MLIP architectures. While the LES framework can extract Born effective charges and polarization from long-range MLIPs [35], and several constant-potential methods incorporate charge response [7][8][20], a unified treatment of long-range electrostatics, solvent polarization, and applied potential within a single framework does not yet exist.

## References

[1] Wang, G., Wang, C., Zhang, X., et al. (2024). Machine learning interatomic potential: Bridge the gap between small-scale models and realistic device-scale simulations. *iScience*, 27, 109673. [DOI](https://doi.org/10.1016/j.isci.2024.109673)

[2] Wan, K., He, J., & Shi, X. (2023). Construction of High Accuracy Machine Learning Interatomic Potential for Surface/Interface of Nanomaterials. *Advanced Materials*, 35, 2305758. [DOI](https://doi.org/10.1002/adma.202305758)

[3] Ma, J., Fu, X., Xie, W., & Hu, P. (2026). From Pretrained to Precision: Fine-Tuning Universal Interatomic Potentials for Accurate Catalytic Reaction Simulations. *J. Chem. Theory Comput.* [DOI](https://doi.org/10.1021/acs.jctc.5c01455)

[4] Loveday, G., et al. (2026). Challenges and Opportunities of Pretrained Machine Learning Interatomic Potentials in Heterogeneous Catalysis. *ACS Catalysis*. [DOI](https://doi.org/10.1021/acscatal.5c08945)

[5] Wang, X., Chen, J., Zeng, Z., et al. (2025). Ion-modulated structure, proton transfer, and capacitance in the Pt(111)/water electric double layer. *arXiv*. [DOI](https://www.semanticscholar.org/paper/4db81a73d8e4bd0f1a946f78bd89455547dfea7e)

[6] Tian, X., Gardini, A. T., Raucci, U., et al. (2025). Electrochemical potential-driven water dynamics control CO₂ electroreduction at the Ag/H₂O interface. *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-025-65630-1)

[7] Chen, J.-L., Qi, X.-Z., Zhu, J., et al. (2025). Grand-Canonical Equivariant Neural Potentials for Electrochemical Interfaces. *J. Chem. Theory Comput.* [DOI](https://doi.org/10.1021/acs.jctc.5c01381)

[8] Zhu, J.-X. & Cheng, J. (2025). Machine Learning Potential for Electrochemical Interfaces with Hybrid Representation of Dielectric Response. *Physical Review Letters*, 135, 018003. [DOI](https://doi.org/10.1103/PhysRevLett.135.018003)

[9] Kempen, L. H. E., Cheula, R., & Andersen, M. (2025). How accurate are foundational machine learning interatomic potentials for heterogeneous catalysis? *J. Chem. Phys.* [DOI](https://doi.org/10.1063/5.0317672)

[10] Batzner, S., Musaelian, A., Sun, L., et al. (2022). E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials. *Nature Communications*, 13, 2453. [DOI](https://doi.org/10.1038/s41467-022-29939-5)

[11] Kim, J., Cho, H., Jeon, H., et al. (2026). Reactive Machine Learning Interatomic Potentials for Chemistry and Materials Science. *Chemical Reviews*. [DOI](https://doi.org/10.1021/acs.chemrev.5c00728)

[12] Leimeroth, N., Erhard, L. C., Albe, K., & Rohrer, J. (2025). Machine-learning interatomic potentials from a user's perspective: a comparison of accuracy, speed and data efficiency. *Modelling Simul. Mater. Sci. Eng.* [DOI](https://doi.org/10.1088/1361-651X/adf56d)

[13] Deng, B., Zhong, P., Jun, K., et al. (2023). CHGNet as a pretrained universal neural network potential for charge-informed atomistic modelling. *Nature Machine Intelligence*, 5, 1031. [DOI](https://doi.org/10.1038/s42256-023-00716-3)

[14] Lan, J., Palizhati, A., Shuaibi, M., et al. (2023). AdsorbML: a leap in efficiency for adsorption energy calculations using generalizable machine learning potentials. *npj Computational Materials*. [DOI](https://doi.org/10.1038/s41524-023-01121-5)

[15] Zhong, P., Kim, D., King, D. S., & Cheng, B. (2025). Machine learning interatomic potential can infer electrical response. *npj Computational Materials*. [DOI](https://doi.org/10.1038/s41524-025-01911-z)

[16] UMA — Universal Model for Atoms Family. Meta FAIR. (Vault note — see prior notes section.)

[17] Liu, Y., et al. (2025). Scaling Machine Learning Interatomic Potentials with Mixtures of Experts. (Vault note — see prior notes section.)

[18] Wu, Z., Zhou, L., Hou, P., et al. (2025). A Machine Learning Interatomic Potential Data Set and Model for Catalysis with Local Fine-Tuning to Chemical Accuracy. *JACS Au*. [DOI](https://doi.org/10.1021/jacsau.5c01112)

[19] CARE — An End-to-End Framework for Reactivity in Heterogeneous Catalysis. López group. (Vault note — see prior notes section.)

[20] Wang, R., Fang, S., Huang, Q., & Liu, Y. (2025). Constant-Potential Machine Learning Force Field for the Electrochemical Interface. *J. Chem. Theory Comput.* [DOI](https://doi.org/10.1021/acs.jctc.5c00784)

[21] Chen, J. & Wang, T. (2025). DPχ: Constant-Potential Machine-Learning Potentials for Large-Scale Electrocatalysis. *ChemRxiv*. [DOI](https://doi.org/10.26434/chemrxiv-2025-6vcnc)

[22] Bianchi, M. G., Fiorentin, M., Risplendi, F., et al. (2025). Electrochemical Interfaces at Constant Potential: Data-Efficient Transfer Learning for Machine-Learning-Based Molecular Dynamics. *arXiv*. [DOI](https://www.semanticscholar.org/paper/a82a58e60a9c62cca801701c29dc116ab950a7cb)

[23] Chen, J., Zhang, & Zhang (2023). MLaMD — Explicit Solvent on Heterogeneous Catalysts via On-the-Fly MLIPs. (Vault note — see prior notes section.)

[24] Deng, B., Choi, Y., Zhong, P., et al. (2025). Systematic softening in universal machine learning interatomic potentials. *npj Computational Materials*, 11, 72. [DOI](https://doi.org/10.1038/s41524-024-01500-6)

[25] Cheula, R., et al. Fine-tuning Universal Machine Learning Potentials for Transition State Search in Surface Catalysis. (Vault note — see prior notes section.)

[26] Moon, J., Jeon, U., Choung, S., & Han, J. W. (2025). CatBench framework for benchmarking machine learning interatomic potentials in adsorption energy predictions for heterogeneous catalysis. *Cell Reports Physical Science*, 6, 102968. [DOI](https://doi.org/10.1016/j.xcrp.2025.102968)

[27] Morrow, J. D., Gardner, J. L. A., & Deringer, V. L. (2023). How to validate machine-learned interatomic potentials. *J. Chem. Phys.*, 158, 121501. [DOI](https://doi.org/10.1063/5.0138597)

[28] Liu, Y., He, X., & Mo, Y. (2023). Discrepancies and error evaluation metrics for machine learning interatomic potentials. *npj Computational Materials*, 9, 174. [DOI](https://doi.org/10.1038/s41524-023-01123-3)

[29] Maxson, T., Soyemi, A., Zhang, X., et al. (2025). MS25: Materials Science-Focused Benchmark Data Set for MLIPs. *J. Chem. Inf. Model.* [DOI](https://doi.org/10.1021/acs.jcim.5c01262)

[30] Sun, M., Jin, B., Yang, X., & Xu, S. (2025). Probing nuclear quantum effects in electrocatalysis via a machine-learning enhanced grand canonical constant potential approach. *Nature Communications*. [DOI](https://doi.org/10.1038/s41467-025-58871-7)

[31] Tran, R., Lan, J., Shuaibi, M., et al. (2023). The Open Catalyst 2022 (OC22) Dataset and Challenges for Oxide Electrocatalysts. *Nature Scientific Data*, 10, 157. [DOI](https://doi.org/10.1038/s41597-023-02665-1)

[32] Wu, Q., Dai, C., Meng, F., et al. (2024). Potential and electric double-layer effect in electrocatalytic urea synthesis. *Nature Communications*, 15, 1055. [DOI](https://doi.org/10.1038/s41467-024-45522-6)

[33] Poltavsky, I., Charkin-Gorbulin, A., Puleva, M., et al. (2025). Crash testing machine learning force fields for molecules, materials, and interfaces: model analysis in the TEA Challenge 2023. *Chemical Science*. [DOI](https://doi.org/10.1039/d4sc06529h)

[34] Yuan, C., Kreiman, T., Zhang, C., et al. (2025). MLIP Arena: Advancing Fairness and Transparency in MLIPs via an Open Benchmark Platform. *arXiv:2509.20630*. [DOI](https://arxiv.org/abs/2509.20630)

[35] Zhong, P., Kim, D., King, D. S., & Cheng, B. (2025). Machine learning interatomic potential can infer electrical response. *npj Computational Materials*. [DOI](https://doi.org/10.1038/s41524-025-01911-z)

[36] Liu, Y. & Mo, Y. (2024). Learning from models: high-dimensional analyses on the performance of machine learning interatomic potentials. *npj Computational Materials*. [DOI](https://doi.org/10.1038/s41524-024-01333-3)

[37] Miret, S., Lee, K., Gonzales, C., et al. (2025). Energy & Force Regression on DFT Trajectories is Not Enough for Universal Machine Learning Interatomic Potentials. *arXiv:2502.03660*. [DOI](https://arxiv.org/abs/2502.03660)

[38] Xie, W., Han, Y., Wu, C., & Hu, P. (2026). Smarter Data: Rethinking Data Generation for MLPs in Heterogeneous Catalysis. *JACS Au*. [DOI](https://doi.org/10.1021/jacsau.6c00100)

[39] Nandi, A., Pandey, P., Houston, P. L., et al. (2024). Δ-Machine Learning to Elevate DFT-Based Potentials to the CCSD(T) Level. *J. Chem. Theory Comput.* [DOI](https://doi.org/10.1021/acs.jctc.4c00977)

[40] Li, J., Knijff, L., Zhang, Z.-Y., et al. (2025). PiNN: Equivariant Neural Network Suite for Modeling Electrochemical Systems. *J. Chem. Theory Comput.* [DOI](https://doi.org/10.1021/acs.jctc.4c01570)
