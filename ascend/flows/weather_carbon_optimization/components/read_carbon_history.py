from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd
import requests
from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import read, test


CARBON_URL_TEMPLATE = "https://uk-carbon-intensity.ascend.dev/intensity/{start}/{end}"
HISTORY_WINDOW_DAYS = 30


def _request_json(url: str, max_attempts: int = 5) -> dict[str, Any]:
    backoff_seconds = 1.0
    timeout = 60

    for attempt in range(1, max_attempts + 1):
        response = requests.get(url, timeout=timeout)
        if response.status_code == 429 and attempt < max_attempts:
            log(f"Rate limited by carbon API, retrying attempt {attempt + 1}")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError("Unable to retrieve carbon history after retries")


def _normalize_half_hour_intervals(interval_rows: list[dict[str, Any]]) -> pd.DataFrame:
    normalized_rows: list[dict[str, Any]] = []
    for item in interval_rows:
        start_ts = datetime.fromisoformat(item["from"].replace("Z", "+00:00")).astimezone(UTC)
        end_ts = datetime.fromisoformat(item["to"].replace("Z", "+00:00")).astimezone(UTC)
        intensity = item.get("intensity") or {}
        normalized_rows.append(
            {
                "interval_start": start_ts,
                "interval_end": end_ts,
                "timestamp_hour": start_ts.replace(minute=0, second=0, microsecond=0),
                "carbon_intensity_forecast_gco2_per_kwh": intensity.get("forecast"),
                "carbon_intensity_actual_gco2_per_kwh": intensity.get("actual"),
                "carbon_intensity_index": intensity.get("index"),
            }
        )

    intervals = pd.DataFrame(normalized_rows)
    if intervals.empty:
        return intervals

    intervals["carbon_intensity_used_gco2_per_kwh"] = intervals[
        "carbon_intensity_actual_gco2_per_kwh"
    ].fillna(intervals["carbon_intensity_forecast_gco2_per_kwh"])

    hourly = (
        intervals.groupby("timestamp_hour", dropna=False)
        .agg(
            carbon_intensity_forecast_gco2_per_kwh=("carbon_intensity_forecast_gco2_per_kwh", "mean"),
            carbon_intensity_actual_gco2_per_kwh=("carbon_intensity_actual_gco2_per_kwh", "mean"),
            carbon_intensity_used_gco2_per_kwh=("carbon_intensity_used_gco2_per_kwh", "mean"),
            carbon_intensity_index=("carbon_intensity_index", "max"),
            half_hour_intervals=("interval_start", "count"),
        )
        .reset_index()
    )
    return hourly


@read(
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="timestamp_hour"),
        test("not_null", column="carbon_intensity_used_gco2_per_kwh"),
    ],
    on_schema_change="sync_all_columns",
)
def read_carbon_history(context: ComponentExecutionContext) -> pd.DataFrame:
    end_time = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=HISTORY_WINDOW_DAYS)
    start_text = start_time.strftime("%Y-%m-%dT%H:%MZ")
    end_text = end_time.strftime("%Y-%m-%dT%H:%MZ")
    url = CARBON_URL_TEMPLATE.format(start=start_text, end=end_text)

    payload = _request_json(url)
    carbon_history = _normalize_half_hour_intervals(payload.get("data") or [])
    carbon_history = carbon_history[
        (carbon_history["timestamp_hour"] >= start_time) & (carbon_history["timestamp_hour"] < end_time)
    ].reset_index(drop=True)
    log(
        f"Returning {len(carbon_history)} hourly carbon rows for trailing {HISTORY_WINDOW_DAYS} days "
        f"from {start_time.isoformat()} to {end_time.isoformat()} using {url}"
    )
    return carbon_history