# Household Water-Service Priorities

**Research code and reproducibility materials**

*Household water-service priorities are not simple reflections of experienced service deficits*

## Overview

Household assessments of water-service quality describe the conditions people experience, but they do not necessarily explain which aspects of service households consider most consequential.

This repository accompanies our study of how households evaluate the impact of different dimensions of water-service delivery on their overall service experience, and whether those evaluations correspond to the service conditions they report.

The research draws on a household survey conducted in September 2025, primarily in Tamil Nadu, India. We analyze responses from 2,874 households reporting Municipality/Corporation as their primary domestic water source.

The study investigates how households distinguish among service dimensions, whether worse experienced conditions correspond to higher relative impact ratings, and how broader service conditions and household characteristics relate to differences in those ratings.

This repository provides research code, measurement documentation, supplementary numerical tables and numerical comparison tools.

## What the study measures

The questionnaire examines household water-service experiences across eight domains.

| Service dimension | Scope of the questionnaire section |
|---|---|
| Affordability | Household water-related costs and affordability experiences |
| Access | Accessibility of household water services |
| Reliability | Reliability of water supply and related experiences |
| Efficiency | Water-supply characteristics and associated service experiences |
| Acceptability | Household experiences of water acceptability |
| Perceived water quality | Household perceptions and assessments of water quality |
| Quantity | Water availability and adequacy of quantity |
| Customer service | Service, maintenance and interactions with providers |

### Reported impact and household priority

Within each domain, respondents answered questions about their experienced service conditions and then rated the impact of that domain, or the matters covered in its questionnaire section, on their overall water-service quality and experience.

The eight impact items use an integer scale from 0 to 10, with higher values indicating greater reported impact.

We use these ratings as an operational measure of **household priority**. The term refers to the importance reflected in respondents' assessments of how much each domain affects their overall service experience.

These ratings describe reported impact, rather than preferences among specific service improvements.

### Relative priority within households

Households differ in how they use the rating scale. Some rate nearly every dimension highly, while others make greater distinctions among dimensions.

To examine these relative differences, the analysis subtracts each household's mean impact rating across all eight domains from its rating for each domain.

For example, a household with an average impact rating of 7 and a reliability rating of 9 has a relative reliability rating of +2. If the same household rates affordability at 5, its relative affordability rating is −2.

Positive values indicate domains rated above the household's own average, while negative values indicate domains rated below it.

The resulting eight centered ratings sum to zero for each household. They preserve differences among domains while removing the household's overall rating level.

We refer to these centered measurements as **relative-priority ratings**.

### Experienced service deficits

The study separately measures experienced service conditions using questionnaire responses from the same eight domains.

For each domain, we selected a corresponding deficit measure representing an aspect of experienced service. Five primary measures use individual ordered questionnaire items. Acceptability, quantity and customer service use composites constructed from related items.

The deficit measures are oriented so that higher values indicate worse experienced conditions. For cross-domain analyses, each measure is standardized separately.

These deficit measures are distinct from the reported impact ratings.

For example, the reliability impact question concerns reliability broadly. The primary reliability deficit instead uses the reported frequency of unexpected outages, with an alternative broad reliability measure examined in sensitivity analysis.

The exact administered questions, response options, coding decisions and alternative deficit definitions are documented in Supplementary Tables S3–S4.

## Research questions and methods

The study addresses three hypotheses.

### H1. Structure of relative household priorities

Do households exhibit recurring patterns in how they rate the relative impact of different service dimensions?

The analysis removes each household's overall rating level and represents the remaining variation using seven orthonormal coordinates. It evaluates Gaussian-mixture models through numerical diagnostics, held-out validation and comparisons with alternative statistical distributions.

Additional analyses distinguish how strongly households differentiate among domains from which domains they rate relatively higher or lower.

The two-component mixture primarily distinguished households by differentiation magnitude rather than distinct domain-priority configurations. A flexible continuous distribution provided better held-out fit.

### H2. Experienced deficits and relative priorities

Do worse experienced conditions in a given service dimension correspond to higher relative impact ratings for that same dimension?

The analysis pairs each domain's relative-priority rating with its corresponding experienced-service deficit.

Household- and domain-fixed-effects models estimate the pooled relationship. Supporting analyses examine domain-specific associations, cross-domain relationships, alternative deficit definitions and statistical equivalence.

The results do not support a consistent positive relationship between greater experienced deficits and higher relative impact ratings in the corresponding domains. Associations differ across dimensions, but the pooled relationship is close to zero.

### H3. Household context and service conditions

How are household characteristics and broader service conditions associated with differences in household priority ratings?

The analyses examine whether households differentiate among domains and whether household context or experienced-service conditions are associated with fitted mixture-component probabilities.

Additional analyses examine observed differentiation magnitude and the direction of relative-priority profiles independently of the fitted components.

Household and service characteristics show associations with fitted component probabilities, but provide little predictive information about observed differentiation magnitude or relative-priority direction. These findings distinguish associations with a statistical representation from the ability to predict households' relative ratings themselves.

## Repository contents

| Directory | Contents |
|---|---|
| `code/` | Analytical functions, synthetic demonstration and numerical comparison tools |
| `config/` | Measurement and numerical contracts, software dependencies and input schemas |
| `data/synthetic/` | Synthetic demonstration data |
| `results/supplementary_tables/` | All 32 Supplementary Information tables, with a searchable [table index](results/supplementary_tables/INDEX.md) |
| `manuscript/` | Study manuscript and Supplementary Information |
| `docs/` | [Measurement and methods](docs/MEASUREMENT_AND_METHODS.md), [reproduction guide](docs/REPRODUCTION_GUIDE.md) and [numerical verification](docs/NUMERICAL_VERIFICATION.md) |
| `tests/` | Automated tests of numerical operations and input validation |

Demonstration and verification outputs are generated locally in `outputs/`, which is excluded from version control.

## Installation and demonstration

Python 3.11 or later is recommended.

From the repository root, install the dependencies:

```bash
python -m pip install -r config/requirements.txt
```

Run the automated tests:

```bash
python -m pytest -q tests
```

### Synthetic demonstration

The repository includes a synthetic demonstration of selected mathematical methods.

Generate the demonstration dataset:

```bash
python code/generate_synthetic_demo.py
```

Run the demonstration:

```bash
python code/driver.py demo --out outputs/demo
```

The demonstration generates synthetic household observations using a fixed random seed.

## Numerical verification

The repository includes computational methods, analytical documentation and 13 numerical reference values corresponding to the manuscript and Supplementary Information.

To compare calculated results against these values, run:

```bash
python code/check_reported_results.py --computed original_computed_results.json --out outputs/parity_report.json
```

Provide a JSON file with calculated results using the format in `config/computed_results.schema.json`. Comparisons use the tolerances in the reference contract. Further instructions are in the [reproduction guide](docs/REPRODUCTION_GUIDE.md).

## Survey administration and data availability

The original household survey was administered in English and Tamil through Qualtrics (an online survey tool), with field coordination and support from local collaborators.

The survey used nonprobability convenience sampling. Eligible adult respondents reported on their household water-service experiences, and all participants provided electronic informed consent. The study was conducted under Stanford University Institutional Review Board Protocol No. 82168.

Household-level survey records and personal identifiers are not included in this repository. Requests for research-data access are subject to applicable consent, institutional review and data-sharing requirements.

## Citation

**Citation to be added upon publication.**

Mohanavelu, A. & Osman, K. K. *Household water-service priorities are not simple reflections of experienced service deficits.*

The final journal reference and DOI will be added when available. Machine-readable repository citation information is provided in `CITATION.cff`.

## License

Original repository software is provided under the MIT License (`LICENSE`) and original standalone documentation under CC BY 4.0 (`LICENSE-DOCUMENTATION.md`). The manuscripts, supplementary tables and third-party materials are subject to their separate rights, as explained in `LICENSE-SCOPE.md`.

## Contact

**Aadhityaa (Aadhi) Mohanavelu**  
Department of Civil and Environmental Engineering, Stanford University  
[Personal website](https://aadhi-mohanavelu.com/)

**Prof. Khalid K. Osman**  
Department of Civil and Environmental Engineering, Stanford University  
osmank@stanford.edu
