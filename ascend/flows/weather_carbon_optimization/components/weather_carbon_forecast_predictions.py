from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("weather_carbon_forecast_features"), ref("weather_carbon_hourly_model")],
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="predicted_carbon_intensity_gco2_per_kwh"),
        test("not_null", column="effective_cost_gbp_per_kwh"),
    ],
)
def weather_carbon_forecast_predictions(
    weather_carbon_forecast_features: ibis.Table,
    weather_carbon_hourly_model: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    historical_profile = (
        weather_carbon_hourly_model.group_by(
            "facility_id",
            "hour_of_day",
            "day_of_week_index",
            "is_weekend",
        )
        .aggregate(
            predicted_carbon_intensity_gco2_per_kwh=weather_carbon_hourly_model.carbon_intensity_gco2_per_kwh.mean(),
            baseline_carbon_cost_gbp_per_kwh=weather_carbon_hourly_model.carbon_cost_gbp_per_kwh.mean(),
        )
    )

    forecast = weather_carbon_forecast_features
    scored = forecast.join(
        historical_profile,
        [
            forecast.facility_id == historical_profile.facility_id,
            forecast.hour_of_day == historical_profile.hour_of_day,
            forecast.day_of_week_index == historical_profile.day_of_week_index,
            forecast.is_weekend == historical_profile.is_weekend,
        ],
        how="left",
    )

    tariff_bucket = ibis.cases(
        (forecast.hour_of_day < 7, "off_peak"),
        (forecast.hour_of_day < 16, "mid_peak"),
        (forecast.hour_of_day < 22, "on_peak"),
        else_="off_peak",
    )
    tariff_rate = ibis.cases(
        (forecast.hour_of_day < 7, 0.135),
        (forecast.hour_of_day < 16, 0.145),
        (forecast.hour_of_day < 22, 0.155),
        else_=0.135,
    )

    return scored.mutate(
        predicted_carbon_intensity_gco2_per_kwh=scored.predicted_carbon_intensity_gco2_per_kwh.coalesce(80.0),
        carbon_cost_gbp_per_kwh=(scored.predicted_carbon_intensity_gco2_per_kwh.coalesce(80.0) / ibis.literal(1000000.0)) * 85.0,
        tariff_bucket=tariff_bucket,
        tariff_rate_gbp_per_kwh=tariff_rate,
        effective_cost_gbp_per_kwh=tariff_rate + ((scored.predicted_carbon_intensity_gco2_per_kwh.coalesce(80.0) / ibis.literal(1000000.0)) * 85.0),
    )