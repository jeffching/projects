from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd
import requests
from ascend.application.context import ComponentExecutionContext
from ascend.common.events import log
from ascend.resources import read, test


OPEN_METEO_URL = "https://open-meteo.ascend.dev/v1/forecast"
HISTORY_WINDOW_DAYS = 30
WEATHER_FIELDS = [
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "cloud_cover",
    "wind_speed_10m",
]
CITY_COORDINATES = [
    {"city": "Manchester", "latitude": 53.4808, "longitude": -2.2426},
    {"city": "Birmingham", "latitude": 52.4862, "longitude": -1.8904},
    {"city": "Leeds", "latitude": 53.8008, "longitude": -1.5491},
    {"city": "Bristol", "latitude": 51.4545, "longitude": -2.5879},
    {"city": "London", "latitude": 51.5074, "longitude": -0.1278},
]


def _request_json(url: str, params: dict[str, Any], max_attempts: int = 5) -> dict[str, Any]:
    backoff_seconds = 1.0
    timeout = 60

    for attempt in range(1, max_attempts + 1):
        response = requests.get(url, params=params, timeout=timeout)
        if response.status_code == 429 and attempt < max_attempts:
            log(f"Rate limited by weather API, retrying attempt {attempt + 1}")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
            continue

        response.raise_for_status()
        return response.json()

    raise RuntimeError("Unable to retrieve weather history after retries")


def _rows_from_payload(payload: dict[str, Any], city: str, latitude: float, longitude: float) -> list[dict[str, Any]]:
    hourly = payload.get("hourly") or {}
    hourly_units = payload.get("hourly_units") or {}
    times = hourly.get("time") or []
    series_lengths = {field: len(hourly.get(field) or []) for field in WEATHER_FIELDS}

    for field, length in series_lengths.items():
        if length not in {0, len(times)}:
            raise ValueError(f"Hourly weather field {field} length {length} does not match time length {len(times)}")

    rows: list[dict[str, Any]] = []
    for index, timestamp_text in enumerate(times):
        timestamp_hour = datetime.fromisoformat(timestamp_text).replace(tzinfo=UTC)
        row = {
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp_hour": timestamp_hour,
            "weather_timezone": payload.get("timezone"),
            "weather_timezone_abbreviation": payload.get("timezone_abbreviation"),
            "weather_elevation": payload.get("elevation"),
        }
        for field in WEATHER_FIELDS:
            values = hourly.get(field) or []
            row[field] = values[index] if index < len(values) else None
            row[f"{field}_unit"] = hourly_units.get(field)
        rows.append(row)

    return rows


@read(
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="city"),
        test("not_null", column="timestamp_hour"),
    ],
    on_schema_change="sync_all_columns",
)
def read_weather_history(context: ComponentExecutionContext) -> pd.DataFrame:
    end_time = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(days=HISTORY_WINDOW_DAYS)
    rows: list[dict[str, Any]] = []

    for city_config in CITY_COORDINATES:
        params = {
            "latitude": city_config["latitude"],
            "longitude": city_config["longitude"],
            "start_date": start_time.date().isoformat(),
            "end_date": end_time.date().isoformat(),
            "hourly": ",".join(WEATHER_FIELDS),
            "timezone": "GMT",
        }
        payload = _request_json(OPEN_METEO_URL, params=params)
        city_rows = _rows_from_payload(
            payload,
            city=city_config["city"],
            latitude=city_config["latitude"],
            longitude=city_config["longitude"],
        )
        log(f"Retrieved {len(city_rows)} hourly weather rows for {city_config['city']}")
        rows.extend(city_rows)

    weather_history = pd.DataFrame(rows)
    weather_history = weather_history[
        (weather_history["timestamp_hour"] >= start_time) & (weather_history["timestamp_hour"] < end_time)
    ].reset_index(drop=True)
    log(
        f"Returning {len(weather_history)} historical weather rows for trailing {HISTORY_WINDOW_DAYS} days "
        f"from {start_time.isoformat()} to {end_time.isoformat()}"
    )
    return weather_history