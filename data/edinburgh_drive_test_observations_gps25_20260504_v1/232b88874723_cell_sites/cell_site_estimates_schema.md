# Cell-Site Estimates CSV Schema

File: `232b88874723_cell_sites/cell_site_estimates.csv`

One row represents one estimated LTE cell-site location derived from curated
drive-test observations. Coordinates use WGS 84 decimal degrees; west
longitudes are negative.

## Columns

| Column | Type | Description |
| --- | --- | --- |
| `cgi` | string | Cell global identifier in `mcc-mnc-tac-cid` form. |
| `mcc` | integer | Mobile Country Code. |
| `mnc` | integer | Mobile Network Code. |
| `tac` | integer | LTE Tracking Area Code. |
| `cid` | integer | LTE cell identifier. |
| `tech` | string | Radio access technology, typically `LTE`. |
| `estimate_method` | string | Estimation method used for the cell-site location. |
| `estimate_latitude` | float | Estimated cell-site latitude in decimal degrees north. |
| `estimate_longitude` | float | Estimated cell-site longitude in decimal degrees east; west is negative. |
| `centroid_latitude` | float | Observation centroid latitude used as an intermediate estimate. |
| `centroid_longitude` | float | Observation centroid longitude used as an intermediate estimate. |
| `n_observations` | integer | Number of observations available for this CGI. |
| `n_top_observations` | integer | Number of strongest observations used for strongest-signal centroiding. |
| `n_ta_observations` | integer | Number of observations with timing advance values. |
| `n_ta_values` | integer | Number of distinct timing advance values. |
| `n_files` | integer | Number of source files contributing observations for this CGI. |
| `max_rsrp` | float | Strongest observed RSRP in dBm. |
| `median_rsrp` | float | Median observed RSRP in dBm. |
| `strongest_observed_latitude` | float | Latitude of the strongest observed signal. |
| `strongest_observed_longitude` | float | Longitude of the strongest observed signal. |
| `strongest_observed_rsrp` | float | RSRP value for the strongest observed signal in dBm. |
| `median_ta` | float | Median LTE timing advance value. |
| `min_ta` | float | Minimum LTE timing advance value. |
| `approx_min_ta_distance_m` | float | Approximate minimum distance implied by timing advance, in metres. |
| `ta_range_span_m` | float | Timing-advance range span used by the fit, in metres. |
| `ta_fit_rmse_m` | float | Timing-advance fit root mean squared error in metres. |
| `ta_fit_p50_residual_m` | float | Median absolute timing-advance fit residual in metres. |
| `ta_fit_p90_residual_m` | float | 90th percentile absolute timing-advance fit residual in metres. |
| `ta_centroid_rmse_m` | float | RMSE for the timing-advance centroid reference, in metres. |
| `top_p50_radius_m` | float | Median radius of strongest observations around the estimate, in metres. |
| `top_p90_radius_m` | float | 90th percentile radius of strongest observations around the estimate, in metres. |
| `all_p90_radius_m` | float | 90th percentile radius of all observations around the estimate, in metres. |
| `source_files` | string | Semicolon-separated relative source CSV paths contributing observations. |

## Notes

Cell-site locations are estimates derived from handset observations, not
authoritative site coordinates. The quality metrics should be used when deciding
whether an estimate is suitable for a particular analysis.
