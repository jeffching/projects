from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("weather_carbon_history_features")],
    tests=[
        test("count_greater_than", count=100),
        test("not_null", column="tariff_bucket"),
        test("not_null", column="effective_cost_gbp_per_kwh"),
    ],
)
def weather_carbon_hourly_model(
    weather_carbon_history_features: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    features = weather_carbon_history_features

    tariff_bucket = ibis.cases(
        (features.hour_of_day < 7, "off_peak"),
        (features.hour_of_day < 16, "mid_peak"),
        (features.hour_of_day < 22, "on_peak"),
        else_="off_peak",
    )
    tariff_rate = ibis.cases(
        (features.hour_of_day < 7, 0.135),
        (features.hour_of_day < 16, 0.145),
        (features.hour_of_day < 22, 0.155),
        else_=0.135,
    )

    return features.mutate(
        tariff_bucket=tariff_bucket,
        tariff_rate_gbp_per_kwh=tariff_rate,
        effective_cost_gbp_per_kwh=tariff_rate + features.carbon_cost_gbp_per_kwh,
        combined_cost_signal=tariff_rate + features.carbon_cost_gbp_per_kwh,
    )