#!/usr/bin/env python3
"""Check drive-test LTE timing advance values against known cell-site locations.

For each observation with a known serving eNodeB, the script verifies that the
distance from the observation GPS point to the known cell site lies in the
reported TA bin:

    TA * 78.125 m <= distance <= (TA + 1) * 78.125 m

The feasible range is expanded by the observation GPS accuracy, when available,
plus any extra tolerance supplied on the command line.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_TA_METRES = 78.125
DEFAULT_CID_SHIFT_BITS = 8
JAVA_INT_MAX = 2_147_483_647
LIST_ROW_CATEGORIES = {
    "invalid-locations": "invalid_location",
    "empty-cids": "empty_cid",
    "missing-ta": "missing_ta",
    "unavailable-ta": "unavailable_ta",
    "unmatched-enodeb": "unmatched_enodeb",
}


def normalize_column_name(column: object) -> str:
    """Normalize CSV headers for tolerant first-line column matching."""
    text = str(column).replace("\ufeff", "").strip().casefold()
    return "".join(char for char in text if char.isalnum())


def haversine_m(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> np.ndarray:
    """Return great-circle distance in metres for scalar or array-like inputs."""
    radius_m = 6_371_000.0
    lat1_arr = np.asarray(lat1, dtype=float)
    lon1_arr = np.asarray(lon1, dtype=float)
    lat2_arr = np.asarray(lat2, dtype=float)
    lon2_arr = np.asarray(lon2, dtype=float)

    dlat = np.radians(lat2_arr - lat1_arr)
    dlon = np.radians(lon2_arr - lon1_arr)
    a = (
        np.sin(dlat / 2.0) ** 2
        + np.cos(np.radians(lat1_arr))
        * np.cos(np.radians(lat2_arr))
        * np.sin(dlon / 2.0) ** 2
    )
    return radius_m * 2.0 * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def load_known_cells(path: Path) -> pd.DataFrame:
    known = pd.read_csv(path)
    columns = resolve_columns(
        known,
        {
            "enodebid": ("enodebid", "enodeb_id"),
            "lat": ("lat", "latitude"),
            "lon": ("lon", "longitude", "lng"),
        },
    )
    missing = {"enodebid", "lat", "lon"}.difference(columns)
    if missing:
        raise ValueError(
            f"{path} is missing required columns: {', '.join(sorted(missing))}; "
            f"available columns: {', '.join(map(str, known.columns))}"
        )

    out = known.copy()
    out["enodebid"] = pd.to_numeric(out[columns["enodebid"]], errors="coerce").astype("Int64")
    out["known_latitude"] = pd.to_numeric(out[columns["lat"]], errors="coerce")
    out["known_longitude"] = pd.to_numeric(out[columns["lon"]], errors="coerce")
    out = out.dropna(subset=["enodebid", "known_latitude", "known_longitude"])
    return out[["enodebid", "known_latitude", "known_longitude"]].drop_duplicates("enodebid")


def resolve_columns(df: pd.DataFrame, aliases: dict[str, tuple[str, ...]]) -> dict[str, str]:
    """Resolve canonical column names using normalized, case-insensitive aliases."""
    by_normalized: dict[str, str] = {}
    for column in df.columns:
        by_normalized.setdefault(normalize_column_name(column), column)

    resolved: dict[str, str] = {}
    for canonical, candidates in aliases.items():
        for candidate in candidates:
            if candidate in df.columns:
                resolved[canonical] = candidate
                break
            match = by_normalized.get(normalize_column_name(candidate))
            if match is not None:
                resolved[canonical] = match
                break
    return resolved


def derive_enodeb_ids(cid_series: pd.Series, shift_bits: int) -> pd.Series:
    cids = pd.to_numeric(cid_series, errors="coerce")

    def shift_cid(cid: float) -> int | None:
        if not np.isfinite(cid) or cid < 0 or not float(cid).is_integer():
            return None
        return int(cid) >> shift_bits

    return cids.map(shift_cid).astype("Int64")


def build_checked_rows(args: argparse.Namespace) -> tuple[pd.DataFrame, dict[str, int]]:
    observations = pd.read_csv(args.input_csv)
    columns = resolve_columns(
        observations,
        {
            "latitude": ("latitude", "lat"),
            "longitude": ("longitude", "lon", "lng"),
            "cid": ("cid",),
            "ta": ("ta",),
        },
    )
    missing = {"latitude", "longitude", "cid", "ta"}.difference(columns)
    if missing:
        raise ValueError(
            f"{args.input_csv} is missing required columns: {', '.join(sorted(missing))}; "
            f"available columns: {', '.join(map(str, observations.columns))}"
        )

    obs = observations.copy()
    obs["row_number"] = obs.index + 2
    obs["latitude"] = pd.to_numeric(obs[columns["latitude"]], errors="coerce")
    obs["longitude"] = pd.to_numeric(obs[columns["longitude"]], errors="coerce")
    obs["ta"] = pd.to_numeric(obs[columns["ta"]], errors="coerce")
    obs["cid"] = obs[columns["cid"]]
    obs["cid_numeric"] = pd.to_numeric(obs[columns["cid"]], errors="coerce")
    obs["enodebid"] = derive_enodeb_ids(obs[columns["cid"]], args.cid_shift_bits)
    obs["sector_id"] = (obs["cid_numeric"] % (1 << args.cid_shift_bits)).where(
        obs["cid_numeric"].notna()
    )

    gps_accuracy_columns = resolve_columns(
        obs,
        {"gps_accuracy": (args.gps_accuracy_column, "gps_accuracy_m", "accuracy_m", "accuracy")},
    )
    if "gps_accuracy" in gps_accuracy_columns:
        gps_accuracy = pd.to_numeric(obs[gps_accuracy_columns["gps_accuracy"]], errors="coerce")
    else:
        gps_accuracy = pd.Series(args.default_gps_accuracy_m, index=obs.index)
    obs["gps_accuracy_m"] = gps_accuracy.fillna(args.default_gps_accuracy_m).clip(lower=0.0)

    valid_location = obs["latitude"].notna() & obs["longitude"].notna()
    empty_cid = obs[columns["cid"]].isna() | obs[columns["cid"]].astype(str).str.strip().eq("")
    missing_ta = obs[columns["ta"]].isna() | obs[columns["ta"]].astype(str).str.strip().eq("")
    unavailable_ta = obs["ta"].eq(JAVA_INT_MAX)
    valid_ta = obs["ta"].notna() & (obs["ta"] >= 0) & ~unavailable_ta
    valid_cid = obs["enodebid"].notna()

    known = load_known_cells(args.known_cells_csv)
    checked = obs.merge(known, on="enodebid", how="left")
    known_match = checked["known_latitude"].notna() & checked["known_longitude"].notna()
    range_checked = valid_location & valid_ta & valid_cid & known_match & ~empty_cid
    unmatched_enodeb = valid_cid & ~known_match & ~empty_cid

    checked["invalid_location"] = ~valid_location
    checked["empty_cid"] = empty_cid
    checked["missing_ta"] = missing_ta
    checked["unavailable_ta"] = unavailable_ta
    checked["unmatched_enodeb"] = unmatched_enodeb

    checked["distance_to_site_m"] = np.nan
    checked.loc[range_checked, "distance_to_site_m"] = haversine_m(
        checked.loc[range_checked, "latitude"],
        checked.loc[range_checked, "longitude"],
        checked.loc[range_checked, "known_latitude"],
        checked.loc[range_checked, "known_longitude"],
    )

    checked["ta_min_distance_m"] = checked["ta"] * args.ta_metres
    checked["ta_max_distance_m"] = (checked["ta"] + 1.0) * args.ta_metres
    checked["feasible_min_m"] = (
        checked["ta_min_distance_m"] - checked["gps_accuracy_m"] - args.tolerance_m
    ).clip(lower=0.0)
    checked["feasible_max_m"] = checked["ta_max_distance_m"] + checked["gps_accuracy_m"] + args.tolerance_m
    checked["expected_ta_floor"] = np.floor(checked["distance_to_site_m"] / args.ta_metres)

    checked["range_checked"] = range_checked
    checked["ta_in_expected_range"] = False
    checked.loc[range_checked, "ta_in_expected_range"] = (
        (checked.loc[range_checked, "distance_to_site_m"] >= checked.loc[range_checked, "feasible_min_m"])
        & (checked.loc[range_checked, "distance_to_site_m"] <= checked.loc[range_checked, "feasible_max_m"])
    )
    checked["distance_below_min_m"] = (
        checked["feasible_min_m"] - checked["distance_to_site_m"]
    ).clip(lower=0.0)
    checked["distance_above_max_m"] = (
        checked["distance_to_site_m"] - checked["feasible_max_m"]
    ).clip(lower=0.0)
    checked["ta_error_direction"] = ""
    checked.loc[range_checked & (checked["distance_below_min_m"] > 0), "ta_error_direction"] = "reported_ta_too_high"
    checked.loc[range_checked & (checked["distance_above_max_m"] > 0), "ta_error_direction"] = "reported_ta_too_low"

    stats = {
        "total_rows": int(len(checked)),
        "invalid_location_rows": int((~valid_location).sum()),
        "ignored_empty_cid_rows": int(empty_cid.sum()),
        "invalid_cid_rows": int((~valid_cid & ~empty_cid).sum()),
        "missing_ta_rows": int(missing_ta.sum()),
        "ignored_unavailable_ta_rows": int(unavailable_ta.sum()),
        "invalid_ta_rows": int((~valid_ta & ~missing_ta & ~unavailable_ta).sum()),
        "unmatched_enodeb_rows": int(unmatched_enodeb.sum()),
        "unmatched_enodeb_count": int(checked.loc[unmatched_enodeb, "enodebid"].nunique()),
        "checked_rows": int(range_checked.sum()),
        "within_range_rows": int((range_checked & checked["ta_in_expected_range"]).sum()),
        "out_of_range_rows": int((range_checked & ~checked["ta_in_expected_range"]).sum()),
        "known_cell_sites": int(len(known)),
    }
    return checked, stats


def output_columns(df: pd.DataFrame) -> list[str]:
    preferred = [
        "row_number",
        "source_file",
        "pass_id",
        "timestamp",
        "cid",
        "enodebid",
        "sector_id",
        "ta",
        "latitude",
        "longitude",
        "gps_accuracy_m",
        "known_latitude",
        "known_longitude",
        "distance_to_site_m",
        "ta_min_distance_m",
        "ta_max_distance_m",
        "feasible_min_m",
        "feasible_max_m",
        "expected_ta_floor",
        "distance_below_min_m",
        "distance_above_max_m",
        "ta_error_direction",
    ]
    return [col for col in preferred if col in df.columns]


def skipped_row_columns(df: pd.DataFrame) -> list[str]:
    preferred = [
        "row_number",
        "source_file",
        "pass_id",
        "timestamp",
        "cid",
        "enodebid",
        "sector_id",
        "ta",
        "latitude",
        "longitude",
        "gps_accuracy_m",
        "known_latitude",
        "known_longitude",
    ]
    return [col for col in preferred if col in df.columns]


def parse_list_row_categories(raw_categories: list[str] | None) -> list[str]:
    if not raw_categories:
        return []

    categories: list[str] = []
    for raw in raw_categories:
        for value in raw.split(","):
            category = value.strip().casefold()
            if not category:
                continue
            if category == "all":
                for known_category in LIST_ROW_CATEGORIES:
                    if known_category not in categories:
                        categories.append(known_category)
                continue
            if category not in LIST_ROW_CATEGORIES:
                valid = ", ".join([*LIST_ROW_CATEGORIES, "all"])
                raise ValueError(f"unknown --list-rows category '{value}'; valid values: {valid}")
            if category not in categories:
                categories.append(category)
    return categories


def print_selected_rows(df: pd.DataFrame, categories: list[str], limit: int) -> None:
    columns = skipped_row_columns(df)
    for category in categories:
        mask_column = LIST_ROW_CATEGORIES[category]
        rows = df[df[mask_column]].copy()
        total = len(rows)
        if limit > 0:
            rows = rows.head(limit)
            suffix = f"showing {len(rows)} of {total}"
        else:
            suffix = f"showing all {total}"

        print(f"{category} rows: {total} total, {suffix}.")
        if rows.empty:
            continue
        print(rows.to_string(columns=columns, index=False))


def unknown_enodeb_summary(df: pd.DataFrame) -> pd.DataFrame:
    unknown = df[df["enodebid"].notna() & df["known_latitude"].isna()].copy()
    if unknown.empty:
        return pd.DataFrame()

    unknown["has_valid_ta"] = unknown["ta"].notna() & (unknown["ta"] >= 0) & ~unknown["ta"].eq(JAVA_INT_MAX)
    unknown["has_valid_location"] = unknown["latitude"].notna() & unknown["longitude"].notna()
    aggregations = {
        "observations": ("enodebid", "size"),
        "unique_cids": ("cid", "nunique"),
        "unique_sector_ids": ("sector_id", "nunique"),
        "valid_ta_rows": ("has_valid_ta", "sum"),
        "valid_location_rows": ("has_valid_location", "sum"),
    }
    if "source_file" in unknown.columns:
        aggregations["source_files"] = ("source_file", "nunique")
    if "timestamp" in unknown.columns:
        aggregations["first_timestamp"] = ("timestamp", "min")
        aggregations["last_timestamp"] = ("timestamp", "max")

    summary = unknown.groupby("enodebid", dropna=False).agg(**aggregations).reset_index()
    summary["enodebid"] = summary["enodebid"].astype("Int64")
    return summary.sort_values(["observations", "enodebid"], ascending=[False, True])


def print_unknown_enodebs(df: pd.DataFrame, limit: int) -> None:
    summary = unknown_enodeb_summary(df)
    if summary.empty:
        print("Unknown eNodeB summary: no derived eNodeB IDs missing from the known-cell catalogue.")
        return

    total_unknown_ids = len(summary)
    total_unknown_rows = int(summary["observations"].sum())
    if limit > 0:
        display = summary.head(limit)
        suffix = f" showing top {len(display)} by observation count"
    else:
        display = summary
        suffix = " showing all"

    print(
        "Unknown eNodeB summary: "
        f"{total_unknown_ids} derived eNodeB IDs across {total_unknown_rows} rows,"
        f"{suffix}."
    )
    print(display.to_string(index=False))


def print_summary(stats: dict[str, int]) -> None:
    checked_rows = stats["checked_rows"]
    out_of_range = stats["out_of_range_rows"]
    rate = (out_of_range / checked_rows * 100.0) if checked_rows else 0.0
    print(
        "TA quality check: "
        f"{out_of_range}/{checked_rows} checked rows out of range ({rate:.2f}%)."
    )
    print(
        "Skipped rows: "
        f"{stats['invalid_location_rows']} invalid location, "
        f"{stats['ignored_empty_cid_rows']} empty CID ignored, "
        f"{stats['invalid_cid_rows']} invalid CID, "
        f"{stats['missing_ta_rows']} missing TA, "
        f"{stats['ignored_unavailable_ta_rows']} unavailable TA ignored, "
        f"{stats['invalid_ta_rows']} invalid TA, "
        f"{stats['unmatched_enodeb_rows']} unmatched eNodeB "
        f"({stats['unmatched_enodeb_count']} unique)."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="Drive-test observation/CDR CSV to check")
    parser.add_argument("known_cells_csv", type=Path, help="Known cell-site CSV with enodebid,lat,lon")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write out-of-range observations to this CSV",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=None,
        help="Write summary counts to this JSON file",
    )
    parser.add_argument(
        "--cid-shift-bits",
        type=int,
        default=DEFAULT_CID_SHIFT_BITS,
        help="Right shift applied to CID to derive eNodeB ID (default: 8)",
    )
    parser.add_argument(
        "--ta-metres",
        type=float,
        default=DEFAULT_TA_METRES,
        help="Distance represented by one LTE TA step in metres (default: 78.125)",
    )
    parser.add_argument(
        "--gps-accuracy-column",
        default="gps_accuracy_m",
        help="Observation column containing horizontal GPS accuracy in metres (default: gps_accuracy_m)",
    )
    parser.add_argument(
        "--default-gps-accuracy-m",
        type=float,
        default=0.0,
        help="GPS accuracy used when the column is missing or blank (default: 0)",
    )
    parser.add_argument(
        "--tolerance-m",
        type=float,
        default=0.0,
        help="Extra tolerance added to both sides of each TA range in metres (default: 0)",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with status 1 when any checked row is out of range",
    )
    parser.add_argument(
        "--list-unknown-enodebs",
        action="store_true",
        help="Print a grouped summary of derived eNodeB IDs not found in the known-cell CSV",
    )
    parser.add_argument(
        "--unknown-enodeb-limit",
        type=int,
        default=25,
        help="Maximum unknown eNodeB rows to print; use 0 for all (default: 25)",
    )
    parser.add_argument(
        "--list-rows",
        action="append",
        default=None,
        metavar="CATEGORY",
        help=(
            "Print rows for skipped categories. Use one or more of: "
            "invalid-locations, empty-cids, missing-ta, unavailable-ta, "
            "unmatched-enodeb, all. May be repeated or comma-separated."
        ),
    )
    parser.add_argument(
        "--list-row-limit",
        type=int,
        default=25,
        help="Maximum rows to print per --list-rows category; use 0 for all (default: 25)",
    )
    args = parser.parse_args()

    if not args.input_csv.is_file():
        parser.error(f"Input CSV does not exist: {args.input_csv}")
    if not args.known_cells_csv.is_file():
        parser.error(f"Known-cells CSV does not exist: {args.known_cells_csv}")
    if args.cid_shift_bits < 0:
        parser.error("--cid-shift-bits must be zero or greater")
    if args.ta_metres <= 0:
        parser.error("--ta-metres must be greater than zero")
    if args.default_gps_accuracy_m < 0:
        parser.error("--default-gps-accuracy-m must be zero or greater")
    if args.tolerance_m < 0:
        parser.error("--tolerance-m must be zero or greater")
    if args.unknown_enodeb_limit < 0:
        parser.error("--unknown-enodeb-limit must be zero or greater")
    if args.list_row_limit < 0:
        parser.error("--list-row-limit must be zero or greater")
    try:
        args.list_rows = parse_list_row_categories(args.list_rows)
    except ValueError as exc:
        parser.error(str(exc))
    return args


def main() -> None:
    args = parse_args()
    try:
        checked, stats = build_checked_rows(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)

    failures = checked[
        checked["range_checked"] & ~checked["ta_in_expected_range"]
    ].copy()
    columns = output_columns(failures)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        failures.to_csv(args.output, columns=columns, index=False)
        print(f"Wrote {len(failures)} out-of-range rows to {args.output}")

    if args.summary_output is not None:
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote summary to {args.summary_output}")

    print_summary(stats)
    if args.list_unknown_enodebs:
        print_unknown_enodebs(checked, args.unknown_enodeb_limit)
    if args.list_rows:
        print_selected_rows(checked, args.list_rows, args.list_row_limit)
    if args.fail_on_violations and stats["out_of_range_rows"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
