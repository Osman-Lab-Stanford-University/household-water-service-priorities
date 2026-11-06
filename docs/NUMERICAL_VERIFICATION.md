# Numerical verification

The study reports numerical results in the manuscript and Supplementary Information. The 32 supplementary-table CSV transcriptions are indexed in [`results/supplementary_tables/INDEX.md`](../results/supplementary_tables/INDEX.md). They are supplementary-table references, not analysis input data.

## Reference comparison

The numerical contract at [`config/numerical_parity_contract.json`](../config/numerical_parity_contract.json) records 13 selected reported values, their source locations and comparison tolerances. Values reflect the precision displayed in the paper.

Supply an independently calculated JSON object following [`config/computed_results.schema.json`](../config/computed_results.schema.json), then run from the repository root:

```bash
python code/check_reported_results.py --computed original_computed_results.json --out outputs/parity_report.json
```

The utility validates result IDs and input-value structure, then reports `NUMERIC_AGREEMENT_ONLY`, `NUMERIC_MISMATCH` or `INCOMPLETE_OR_INVALID`.

## Manuscript materials

The manuscript and Supplementary Information are provided under [`manuscript/`](../manuscript/). The exported supplementary tables are under [`results/supplementary_tables/`](../results/supplementary_tables/).
