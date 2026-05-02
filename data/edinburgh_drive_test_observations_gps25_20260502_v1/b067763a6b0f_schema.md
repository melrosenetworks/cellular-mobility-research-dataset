# Edinburgh Drive-Test Observations CSV Schema

File: `b067763a6b0f.csv`

One row represents one curated LTE observation from a drive-test pass. Coordinates
use WGS 84 decimal degrees; west longitudes are negative.

## Columns

| Column | Type | Description |
| --- | --- | --- |
| `source_file` | string | Relative source CSV path used to produce the observation. |
| `pass_id` | integer | Numeric pass identifier assigned during curation. |
| `timestamp` | datetime | Observation timestamp in UTC. |
| `latitude` | float | GPS latitude in decimal degrees north. |
| `longitude` | float | GPS longitude in decimal degrees east; west is negative. |
| `altitude` | float | GPS altitude, where provided by the source device. |
| `gps_accuracy_m` | float | Reported GPS horizontal accuracy in metres. |
| `mcc` | integer | Mobile Country Code. |
| `mnc` | integer | Mobile Network Code. |
| `tac` | integer | LTE Tracking Area Code. |
| `cid` | integer | LTE cell identifier. |
| `rsrp` | float | Serving-cell Reference Signal Received Power in dBm. |
| `rsrq` | float | Serving-cell Reference Signal Received Quality in dB. |
| `ta` | integer | LTE timing advance value reported by the device. |
| `arfcn` | integer | Serving-cell LTE EARFCN. |
| `pci` | integer | Serving-cell Physical Cell ID. |
| `tech` | string | Radio access technology, typically `LTE`. |
| `n_neighbours` | integer | Number of neighbour cells parsed for the observation. |
| `nb0_pci` to `nb3_pci` | float | Neighbour-cell Physical Cell IDs, ordered as reported. |
| `nb0_arfcn` to `nb3_arfcn` | float | Neighbour-cell EARFCNs, ordered as reported. |
| `nb0_rsrp` to `nb3_rsrp` | float | Neighbour-cell RSRP values in dBm, ordered as reported. |
| `nb0_rsrq` to `nb3_rsrq` | float | Neighbour-cell RSRQ values in dB, ordered as reported. |
| `cgi` | string | Serving-cell global identifier in `mcc-mnc-tac-cid` form. |
| `prev_cgi` | string | Previous serving-cell global identifier after timestamp ordering. |
| `time_since_handoff` | float | Seconds since the previous observed serving-cell change. |
| `speed_ms` | float | Estimated movement speed in metres per second. |
| `heading_deg` | float | Estimated movement heading in degrees. |
| `delta_ta` | integer | Difference between current and previous timing advance. |
| `heading_sin` | float | Sine transform of `heading_deg`. |
| `heading_cos` | float | Cosine transform of `heading_deg`. |

## Notes

Blank fields indicate unavailable or unparsed source values. Android telephony
`Integer.MAX_VALUE` sentinels (`2147483647`) are normalized to blank before
analysis and export. Rows sharing a timestamp are treated as one Android
`TelephonyManager.allCellInfo` batch; the LTE observation is selected from the
batch by cell identity, RAT and available signal fields, not by source row order.
The public dataset uses the filters recorded in the manifest.
