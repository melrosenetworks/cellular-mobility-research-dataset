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

The current release is `edinburgh_drive_test_observations_gps25_20260503_v2`.
It contains 87,656 curated observations from 57 source CSV files, covering 695
observed serving-cell identifiers between 2025-11-23 and 2026-05-03. The release
also includes 655 estimated LTE cell-site locations derived from the observations.

Coordinates are WGS 84 latitude/longitude decimal degrees (`EPSG:4326`). The
published dataset is filtered to this bounding box:

```text
min latitude:   55.890
max latitude:   56.000
min longitude:  -3.430
max longitude:  -3.150
```

The published observations are filtered to GPS accuracy of 25 metres or better.
The curation pipeline also removes overlapping pass sections and omits configured
exclusion areas recorded in the release manifest.

## Intended Use

This dataset is made available for academic research, non-commercial
development, and evaluation activities, particularly where the objective is to
improve understanding of positioning, navigation, or mobility using cellular
signals.

It is suitable for experimentation, algorithm development, and comparative
analysis, but is not intended for direct operational deployment without further
validation and augmentation.

## Published Files

The release files are in
`data/edinburgh_drive_test_observations_gps25_20260503_v2/`. File names use the
release content prefix `31e30acc43f2`:

Previous releases are retained in `data/`. Releases can be differentiated by
the date and version in the release directory name, and by the file prefix/stem
used for the generated artefacts.

- `31e30acc43f2.csv`: curated LTE observation records.
- `31e30acc43f2_schema.md`: schema for the observation CSV.
- `31e30acc43f2_parse_log.csv`: per-source parse and curation summary.
- `31e30acc43f2_parse_log_schema.md`: schema for the parse log.
- `31e30acc43f2_manifest.json`: release metadata, filters, coordinate reference
  system, road coverage summary, and file list.
- `31e30acc43f2_viewer.html`: standalone interactive observation viewer.
- `31e30acc43f2_cell_sites/cell_site_estimates.csv`: estimated LTE cell-site
  locations.
- `31e30acc43f2_cell_sites/cell_site_estimates_schema.md`: schema for the
  cell-site estimates.
- `31e30acc43f2_cell_sites/cell_site_estimates.geojson`: cell-site estimates as
  GeoJSON points.
- `31e30acc43f2_cell_sites/cell_site_estimates_map.html`: standalone
  interactive map of estimated cell-site locations.
- `31e30acc43f2_cell_sites/cell_site_ta_overlap_areas.geojson`: timing-advance
  feasible-area geometries for cell-site analysis.
- `31e30acc43f2_cell_sites/cell_site_ta_overlap_map.html`: standalone
  interactive map of timing-advance overlap areas.
- `31e30acc43f2_cell_sites/cell_site_comparison.csv`: comparison between
  estimated cell-site locations and supplied known eNodeB coordinates.
- `31e30acc43f2_road_coverage_by_class.csv`: road-length coverage summary by
  OpenStreetMap highway class.
- `31e30acc43f2_road_coverage_roads.geojson`: OpenStreetMap road geometries
  with estimated drive-test coverage metrics.
- `31e30acc43f2_road_coverage_uncovered_roads.geojson`: road segments remaining
  after covered spans are removed.
- `31e30acc43f2_road_coverage_uncovered_roads_tertiary_and_higher.geojson`:
  uncovered road segments for tertiary and higher highway classes.
- `31e30acc43f2_road_coverage_summary.json`: road coverage parameters and
  class-level summary.

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
data/edinburgh_drive_test_observations_gps25_20260503_v2/31e30acc43f2_viewer.html
data/edinburgh_drive_test_observations_gps25_20260503_v2/31e30acc43f2_cell_sites/cell_site_estimates_map.html
data/edinburgh_drive_test_observations_gps25_20260503_v2/31e30acc43f2_cell_sites/cell_site_ta_overlap_map.html
```

If your browser blocks local resources, serve the directory locally:

```bash
python3 -m http.server 8767 --directory data/edinburgh_drive_test_observations_gps25_20260503_v2
```

Then open `http://localhost:8767/`.

## Notes On Cell-Site Estimates

The cell-site files contain inferred locations from handset observations. They
are estimates only and may be inaccurate. They are not authoritative operator
site coordinates. Use the quality metrics in `cell_site_estimates.csv`, such as
observation counts and radius/residual statistics, when deciding whether an
estimate is suitable for analysis.

The release also includes timing-advance overlap outputs. These show feasible
areas implied by intersecting per-observation timing-advance disks and should be
treated as analytical aids, not ground-truth site boundaries.

Where known eNodeB coordinates are supplied to the pipeline,
`cell_site_comparison.csv` records matches and distance errors between inferred
locations and that reference catalogue.

## Road Coverage Outputs

Road coverage outputs estimate which OpenStreetMap road segments fall within
the drive-test coverage envelope. The current release uses a 25 metre coverage
buffer, 10 metre road sampling, 150 metre maximum observation segment length,
and 60 second maximum time gap when constructing covered spans.

The drive-test collection focuses primarily on motorway, trunk, primary,
secondary, and tertiary roads. Approximate coverage by OpenStreetMap road class,
including each class's `_link` roads, is:

- Motorway: 98.4%.
- Trunk: 83.1%.
- Primary: 93.4%.
- Secondary: 98.1%.
- Tertiary: 81.1%.

Further dataset updates should be expected until coverage exceeds 95% for each
of these priority road classes.

These files are useful for understanding geographic coverage of the released
observations. They are not a statement of network service availability.

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

## Data Credits And Attribution

Use of this dataset must include the following attribution:

```text
Dataset provided by Melrose Networks (Melrose Labs Ltd)
```

The curated drive-test observations and inferred LTE cell-site estimates are
derived from Melrose Networks drive-test collection and analysis.

Road-coverage outputs, where included, use road geometry from
[OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, retrieved
through the Overpass API. OpenStreetMap data is available under the
[Open Database Licence](https://opendatacommons.org/licenses/odbl/).

The interactive HTML viewers may load third-party map tiles depending on the
selected background layer. These include OpenStreetMap tiles, OpenStreetMap HOT
tiles, CARTO basemaps, and OpenTopoMap tiles using OpenStreetMap and SRTM data.
Please retain the attribution displayed in the viewers when publishing maps,
screenshots, or derivative visualisations.

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