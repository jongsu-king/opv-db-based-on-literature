# OPV-DB Scientific Data Release Package

This package is the publication-facing OPV-DB release intended for Scientific
Data review and Zenodo deposition. It is deliberately smaller than the internal
working release directory.

## Relationship to the original OPV-DB

This release is a **derivative work**. It builds on the original OPV-DB by
Qiu, Jiangjie (Zenodo, https://doi.org/10.5281/zenodo.20841543, CC BY 4.0) and
extends it by merging in an independently literature-mined device-record
collection, so the record counts and coverage here differ from the original
release. As required by CC BY 4.0, the original is credited above and the
changes are stated here.

Changes relative to the original OPV-DB:

- Merged an independently literature-mined OPV device-record collection into
  the device table.
- Consolidated the three previously separate device tiers into a single
  `data/opv_devices.csv` carrying `in_strict_performance_benchmark` and
  `in_strict_molecular_benchmark` tier columns (see below).

Cite both this release and the original OPV-DB when using these data. See
`CITATION.cff` for this release and `THIRD_PARTY_ATTRIBUTION.md` for other
external resources used during construction.

## Included data files

- `data/opv_devices.csv`: single consolidated device table. It contains the
  publication-facing single-junction OPV device-record archive after excluding
  physically non-single-cell records and nonstandard module, tandem/subcell,
  silicon-hybrid, perovskite/lead-halide hybrid,
  theoretical/computational/device-simulation, photodiode, Schottky, and
  Voc >2.0 V and PCE-recomputation error >50% rows. The two recommended
  modelling benchmarks are marked in-place by the boolean columns
  `in_strict_performance_benchmark` and `in_strict_molecular_benchmark` rather
  than shipped as separate files.
- `data/materials_reference.csv`: supporting material labels, SMILES, aliases,
  classes, and available reference annotations.

### Selecting a tier

The three published layers are nested subsets of the same records
(molecular ⊂ performance ⊂ full) with identical field values, so each is
recovered by filtering the consolidated table:

| Layer | Filter | Records |
| --- | --- | --- |
| Full archive | no filter | 38,849 |
| Strict performance benchmark | `in_strict_performance_benchmark == true` | 31,360 |
| Strict molecular benchmark | `in_strict_molecular_benchmark == true` | 21,720 |

```python
import pandas as pd

devices = pd.read_csv("data/opv_devices.csv")
performance = devices[devices["in_strict_performance_benchmark"]]
molecular = devices[devices["in_strict_molecular_benchmark"]]
```

## Included validation files

- `validation/opv_quality_tier_rules.json`
- `validation/opv_quality_tier_summary.csv`
- `validation/opv_quality_tier_field_coverage.csv`
- `validation/opv_pce_consistency_records.csv`

In `opv_quality_tier_summary.csv`, `all_four_metrics_records` is the raw count
of records where PCE, Voc, Jsc, and FF are all non-empty. The separate
`pce_consistency_checkable_records` column counts records with all four metrics
plus retained `pce_recomputed` and retained `pce_relative_error_percent`.

## Code availability

Custom code used for manuscript figure generation and release checks should be
archived separately through the manuscript Code Availability statement. This
data deposition package intentionally contains only data, validation summaries,
metadata, attribution, and checksums.

See `metadata/release_manifest.json` and `metadata/SHA256SUMS.txt` for the
exact file list and checksums.
