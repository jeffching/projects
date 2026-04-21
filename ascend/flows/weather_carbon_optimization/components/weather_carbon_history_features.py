from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[
        ref("read_weather_history"),
        ref("read_carbon_history"),
        ref("read_facilities"),
    ],
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="facility_id"),
        test("not_null", column="timestamp_hour"),
        test("not_null", column="carbon_intensity_gco2_per_kwh"),
    ],
)
def weather_carbon_history_features(
    read_weather_history: ibis.Table,
    read_carbon_history: ibis.Table,
    read_facilities: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    weather = read_weather_history.mutate(
        timestamp_hour=read_weather_history.timestamp_hour.cast("timestamp"),
    )
    carbon = read_carbon_history.mutate(
        timestamp_hour=read_carbon_history.timestamp_hour.cast("timestamp"),
    )

    features = (
        weather.join(read_facilities, [weather.city == read_facilities.city], how="left")
        .join(carbon, [weather.timestamp_hour == carbon.timestamp_hour], how="left")
        .mutate(
            carbon_intensity_gco2_per_kwh=carbon.carbon_intensity_used_gco2_per_kwh,
            carbon_intensity_forecast_gco2_per_kwh=carbon.carbon_intensity_forecast_gco2_per_kwh,
            carbon_intensity_actual_gco2_per_kwh=carbon.carbon_intensity_actual_gco2_per_kwh,
            carbon_intensity_index=carbon.carbon_intensity_index,
            carbon_cost_gbp_per_kwh=(carbon.carbon_intensity_used_gco2_per_kwh / ibis.literal(1000000.0)) * 85.0,
            hour_of_day=weather.timestamp_hour.hour(),
            day_of_week_index=weather.timestamp_hour.day_of_week.index(),
            is_weekend=weather.timestamp_hour.day_of_week.index().isin([5, 6]),
        )
    )

    return features.select(
        "facility_id",
        "facility_name",
        "region",
        "city",
        weather.latitude.name("weather_latitude"),
        weather.longitude.name("weather_longitude"),
        "timestamp_hour",
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation",
        "cloud_cover",
        "wind_speed_10m",
        "carbon_intensity_gco2_per_kwh",
        "carbon_intensity_forecast_gco2_per_kwh",
        "carbon_intensity_actual_gco2_per_kwh",
        "carbon_intensity_index",
        "carbon_cost_gbp_per_kwh",
        "hour_of_day",
        "day_of_week_index",
        "is_weekend",
    )