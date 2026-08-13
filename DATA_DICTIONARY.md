# OPV-DB Data Dictionary

This dictionary describes the files included in the Scientific Data release
package.

## Data Files

- `data/opv_devices.csv`: single consolidated device table holding the
  publication-facing single-junction OPV device-record archive after excluding
  physically non-single-cell records and nonstandard module, tandem/subcell,
  silicon-hybrid, perovskite/lead-halide hybrid,
  theoretical/computational/device-simulation, photodiode, Schottky, and
  Voc >2.0 V and PCE-recomputation error >50% rows. The two strict benchmark
  layers are nested subsets of this table with identical field values and are
  marked by the `in_strict_performance_benchmark` and
  `in_strict_molecular_benchmark` columns; earlier releases shipped them as the
  separate files `opv_devices_full.csv`,
  `opv_devices_strict_performance_benchmark.csv`, and
  `opv_devices_strict_molecular_benchmark.csv`.
- `data/materials_reference.csv`: supporting material-reference table used for
  material labels, SMILES, aliases, material classes, and available reference
  annotations. It is not a unique authoritative namespace; some labels retain
  multiple literature/reference entries, and common aliases may appear in the
  `aliases` field rather than as separate `name` rows.

## Device Table Fields

- `id`: unique device-record identifier.
- `doi`, `doi_norm`: normalized source DOI fields used for public release
  provenance.
- `donor`, `acceptor`: extracted donor and acceptor labels.
- `donor_canonical`, `acceptor_canonical`: normalized material labels.
- `donor_smiles`, `acceptor_smiles`: mapped molecular strings when available.
- `voc`: open-circuit voltage in V.
- `jsc`: short-circuit current density in mA cm^-2.
- `ff`: fill factor in percent.
- `pce`: reported power conversion efficiency in percent.
- `pce_recomputed`: deterministic value calculated as `voc * jsc * ff / 100`;
  blank when unavailable or when the derived value is removed during public
  high-PCE cleanup.
- `pce_relative_error_percent`: relative deviation between reported and
  recomputed PCE where all four metrics are available.
- `pce_avg`, `pce_best`: extracted average and best PCE values when available.
- `d_a_ratio`: donor:acceptor blend ratio when reported.
- `additive`, `additive_canonical`, `additive_ratio`: additive labels and
  reported additive loading.
- `device_structure`, `device_type`: device stack and architecture labels.
- `etl`, `etl_canonical`, `htl`, `htl_canonical`: electron- and hole-transport
  layer labels.
- `active_layer_thickness`: active-layer thickness, typically in nm when
  reported.
- `solvent`, `solvent_canonical`: processing solvent labels.
- `annealing_temp`: annealing temperature, typically in degrees Celsius when
  reported.
- `homo_d`, `lumo_d`, `eg_d`, `homo_a`, `lumo_a`, `eg_a`: material-reference
  energy-level annotations. These fields should not be interpreted as
  article-specific device measurements unless independently verified.
- `in_strict_performance_benchmark`: `true` when the record belongs to the
  strict benchmark layer requiring normalized DOI, donor, acceptor, PCE, Voc,
  Jsc, FF, internal source-scope checks, physical-range checks, duplicate
  removal, and PCE recomputation relative error <= 2%.
- `in_strict_molecular_benchmark`: `true` when the record is a strict
  performance benchmark record that also has both donor and acceptor SMILES
  present. Implies `in_strict_performance_benchmark == true`.

The public device exports intentionally omit unstable internal provenance
helper columns such as source-table labels, source-type labels, verification
flags, and baseline-reference flags. The stable public provenance identifier is
the source DOI.

## Material-Reference Fields

- `name`: material label.
- `smiles`: mapped molecular string.
- `material_type`: donor, acceptor, transport layer, additive, or other role
  category when available.
- `chemical_class`: broad chemical class annotation when available.
- `aliases`: known aliases or alternate labels.
- `homo`, `lumo`: reference energy-level annotations.

The public material-reference export intentionally omits unstable internal
source labels. It should be treated as a supporting material-identity table, not
as a fully auditable source namespace.

## Validation Files

- `validation/opv_quality_tier_rules.json`: public tier definitions.
- `validation/opv_quality_tier_summary.csv`: record and coverage summaries for
  the three public layers: full archive, strict performance benchmark, and
  strict molecular benchmark. `all_four_metrics_records` is the raw count of
  rows where PCE, Voc, Jsc, and FF are all non-empty.
  `pce_consistency_checkable_records` is the count of rows where those four
  reported metrics plus retained public PCE-recomputation diagnostics are
  available.
- `validation/opv_quality_tier_field_coverage.csv`: field-level filled-record
  coverage for the three public layers.
- `validation/opv_pce_consistency_records.csv`: record-level PCE recomputation
  diagnostics for rows where PCE, Voc, Jsc, FF, `pce_recomputed`, and
  `pce_relative_error_percent` are all retained in the public export.

Missing values are represented as empty cells.
