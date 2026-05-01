# Edinburgh Drive-Test Parse Log CSV Schema

File: `7681cc66ecb0_parse_log.csv`

One row summarises parsing and curation results for one source CSV file.

## Columns

| Column | Type | Description |
| --- | --- | --- |
| `file` | string | Relative source CSV path. |
| `status` | string | Parse/curation status for the file, such as `ok`, `empty`, or `no_bbox_match`. |
| `raw_obs` | integer | Number of observations parsed before curation filters. |
| `clean_obs` | integer | Number of observations after optional cleaning. |
| `gps_accuracy_obs` | integer | Number of observations after the GPS accuracy filter. |
| `curated_obs` | integer | Number of observations inside the dataset bounding box before overlap exclusion. |
| `lat_min` | float | Minimum curated latitude for the source file. |
| `lat_max` | float | Maximum curated latitude for the source file. |
| `lon_min` | float | Minimum curated longitude for the source file. |
| `lon_max` | float | Maximum curated longitude for the source file. |
| `n_cgis` | integer | Number of distinct serving-cell global identifiers in curated observations. |
| `overlap_excluded_obs` | integer | Observations removed by overlap exclusion. |
| `curated_after_overlap_obs` | integer | Curated observations remaining after overlap exclusion. |

## Notes

Counts are useful for audit and reproducibility. Some count or range fields may
be blank for files that did not produce curated observations.
