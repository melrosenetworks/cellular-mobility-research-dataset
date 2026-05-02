![Edinburgh Dataset](DataSet_Edinburgh.png)

# Cellular Mobility & Positioning Research Dataset

An anonymised cellular drive-test dataset for research into GNSS-independent
positioning and mobility reconstruction using cell ID history.

This repository contains a curated public release of LTE drive-test observations
collected around Edinburgh, Scotland.

## Context

Positioning, navigation, and movement intelligence are increasingly affected by
the limitations and vulnerabilities of GNSS. At the same time, cellular networks
provide a globally pervasive signal layer that can be observed and analysed to
infer location and movement.

This dataset has been released to support research into how cellular network
observations can be used as an alternative or complementary source of positioning
and mobility intelligence. It reflects ongoing work in telecom-native and
RF-based situational awareness.

## Purpose

The dataset is intended to enable research into two closely related areas:
positioning without reliance on GNSS, and the reconstruction of movement from
cell ID history. In both cases, the focus is on understanding what can be
inferred from the cellular environment alone, using real-world observations
rather than simulated data.

More broadly, it supports work in signal-driven localisation, mobility
modelling, and the evaluation of inference techniques under realistic conditions.

## Dataset Description

The data consists of time-sequenced cellular observations collected during drive
testing in terrestrial environments. It includes serving and neighbouring cell
information, along with signal-related measurements representative of real-world
network conditions.

The dataset has been anonymised and reduced in scope to remove identifiers and
sensitive attributes, while retaining sufficient structure and fidelity to
support meaningful analysis.

The current release is `edinburgh_drive_test_observations_gps25_20260427_v1`.
It contains 52,134 curated observations from 42 source CSV files, covering 521
observed serving-cell identifiers between 2025-11-23 and 2026-04-27. The release
also includes 494 estimated LTE cell-site locations derived from the observations.

Coordinates are WGS 84 latitude/longitude decimal degrees (`EPSG:4326`). The
published dataset is filtered to this bounding box:

```text
min latitude:   55.890
max latitude:   56.000
min longitude:  -3.430
max longitude:  -3.150
```

## Intended Use

This dataset is made available for academic research, non-commercial
development, and evaluation activities, particularly where the objective is to
improve understanding of positioning, navigation, or mobility using cellular
signals.

It is suitable for experimentation, algorithm development, and comparative
analysis, but is not intended for direct operational deployment without further
validation and augmentation.

## Published Files

The release files are in `data/`:

- `data/edinburgh_drive_test_observations_gps25_20260427_v1.csv`: curated LTE
  observation records.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_schema.md`: schema
  for the observation CSV.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_parse_log.csv`:
  per-source parse and curation summary.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_parse_log_schema.md`:
  schema for the parse log.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_manifest.json`:
  release metadata, filters, coordinate reference system, and file list.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_viewer.html`:
  standalone interactive observation viewer.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_cell_sites/cell_site_estimates.csv`:
  estimated LTE cell-site locations.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_cell_sites/cell_site_estimates_schema.md`:
  schema for the cell-site estimates.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_cell_sites/cell_site_estimates.geojson`:
  cell-site estimates as GeoJSON points.
- `data/edinburgh_drive_test_observations_gps25_20260427_v1_cell_sites/cell_site_estimates_map.html`:
  standalone interactive map of estimated cell-site locations.

## What Is In Each Observation

Each observation is one timestamped LTE serving-cell measurement with GPS
location and derived movement context. The main CSV includes:

- Source provenance: `source_file`, `pass_id`, and `timestamp`.
- GPS fields: `latitude`, `longitude`, `altitude`, and `gps_accuracy_m`.
- Serving-cell fields: `mcc`, `mnc`, `tac`, `cid`, `cgi`, `pci`, `arfcn`,
  `rsrp`, `rsrq`, `ta`, and `tech`.
- Neighbour-cell fields for up to four neighbours.
- Derived sequence features such as `prev_cgi`, `time_since_handoff`,
  `speed_ms`, `heading_deg`, `delta_ta`, `heading_sin`, and `heading_cos`.

See the schema files in `data/` for column-level descriptions.

## Viewing The Data

Open the HTML files in a browser:

```text
data/edinburgh_drive_test_observations_gps25_20260427_v1_viewer.html
data/edinburgh_drive_test_observations_gps25_20260427_v1_cell_sites/cell_site_estimates_map.html
```

If your browser blocks local resources, serve the directory locally:

```bash
python3 -m http.server 8767
```

Then open `http://localhost:8767/data/`.

## Notes On Cell-Site Estimates

The cell-site files contain inferred locations from handset observations. They
are not authoritative operator site coordinates. Use the quality metrics in
`cell_site_estimates.csv`, such as observation counts and radius/residual
statistics, when deciding whether an estimate is suitable for analysis.

## Limitations

As a curated subset of a larger body of work, the dataset is necessarily
incomplete. It may contain noise, inconsistencies, or environment-specific
characteristics that reflect the conditions under which it was collected. Ground
truth positioning, where present, may be approximate and should not be assumed
to be authoritative.

Users should treat the dataset as a research artefact rather than a
production-grade input.

## Responsible Use

This dataset is released to support research and defensive applications. It must
not be used to re-identify individuals, devices, or sensitive locations, nor to
support harmful, unlawful, or adversarial activity. The development or deployment
of systems for offensive or targeting purposes using this dataset is not
permitted.

Users are expected to act responsibly and in accordance with applicable laws and
regulations.

## Licence

This dataset is released under the Melrose Networks Responsible Use Licence
(MNRUL v1.1). Use is permitted for research, evaluation, and defensive purposes.
Commercial use, and any harmful or offensive use, is prohibited without prior
written permission.

Please refer to the `LICENSE` file for full terms.

## Attribution

Use of this dataset must include the following attribution:

```text
Dataset provided by Melrose Networks (Melrose Labs Ltd)
```

## Collaboration

Melrose Networks welcomes engagement with academic institutions, industry
partners, and public sector organisations working in areas related to resilient
positioning, mobility intelligence, and telecom-native analysis.

For collaboration, access to extended datasets, or commercial enquiries:

```text
contact@melrosenetworks.com
```

## About

Melrose Networks is a business unit of Melrose Labs Ltd, focused on
telecom-native and RF-based technologies for detection, tracking, and analysis
of complex mobility and emerging threats.

## Disclaimer

This dataset is provided "as is", without warranty of any kind. See the
`LICENSE` file for full terms.

--