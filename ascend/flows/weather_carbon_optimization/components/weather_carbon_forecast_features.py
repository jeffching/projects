from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("read_weather_forecast"), ref("read_facilities")],
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="facility_id"),
        test("not_null", column="timestamp_hour"),
    ],
)
def weather_carbon_forecast_features(
    read_weather_forecast: ibis.Table,
    read_facilities: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    forecast = read_weather_forecast.mutate(
        timestamp_hour=read_weather_forecast.timestamp_hour.cast("timestamp"),
    )

    joined = forecast.join(read_facilities, [forecast.city == read_facilities.city], how="left")

    return joined.mutate(
        hour_of_day=joined.timestamp_hour.hour(),
        day_of_week_index=joined.timestamp_hour.day_of_week.index(),
        is_weekend=joined.timestamp_hour.day_of_week.index().isin([5, 6]),
    ).select(
        "facility_id",
        "facility_name",
        "region",
        "city",
        forecast.latitude.name("weather_latitude"),
        forecast.longitude.name("weather_longitude"),
        "timestamp_hour",
        "forecast_generated_at",
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "cloud_cover",
        "wind_speed_10m",
        "hour_of_day",
        "day_of_week_index",
        "is_weekend",
    )