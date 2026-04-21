from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("machine_schedule_baseline"), ref("weather_carbon_forecast_predictions")],
    tests=[
        test("count_greater_than", count=0, severity="warn"),
        test("not_null", column="machine_id", severity="warn"),
    ],
)
def machine_reschedule_candidates(
    machine_schedule_baseline: ibis.Table,
    weather_carbon_forecast_predictions: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    baseline = machine_schedule_baseline.filter(machine_schedule_baseline.schedulable)
    forecast = weather_carbon_forecast_predictions.select(
        weather_carbon_forecast_predictions.facility_id.name("forecast_facility_id"),
        weather_carbon_forecast_predictions.day_of_week_index.cast("int64").name("forecast_day_of_week_index"),
        weather_carbon_forecast_predictions.hour_of_day.cast("int64").name("forecast_hour_of_day"),
        weather_carbon_forecast_predictions.tariff_bucket.name("forecast_tariff_bucket"),
        weather_carbon_forecast_predictions.tariff_rate_gbp_per_kwh.cast("float64").name("forecast_tariff_rate_gbp_per_kwh"),
        weather_carbon_forecast_predictions.predicted_carbon_intensity_gco2_per_kwh.cast("float64").name("forecast_predicted_carbon_intensity_gco2_per_kwh"),
        weather_carbon_forecast_predictions.carbon_cost_gbp_per_kwh.cast("float64").name("forecast_carbon_cost_gbp_per_kwh"),
    )

    candidates = baseline.join(
        forecast,
        [
            baseline.facility_id == forecast.forecast_facility_id,
            baseline.day_of_week_index == forecast.forecast_day_of_week_index,
        ],
        how="inner",
    ).filter(forecast.forecast_hour_of_day + baseline.runtime_hours <= 24)

    evaluated = candidates.mutate(
        candidate_start_hour=candidates.forecast_hour_of_day.cast("int64"),
        candidate_tariff_bucket=candidates.forecast_tariff_bucket,
        candidate_energy_cost_gbp=(candidates.energy_kwh * candidates.forecast_tariff_rate_gbp_per_kwh).cast("float64"),
        candidate_carbon_kg=((candidates.energy_kwh * candidates.forecast_predicted_carbon_intensity_gco2_per_kwh) / ibis.literal(1000.0)).cast("float64"),
        candidate_carbon_cost_gbp=(candidates.energy_kwh * candidates.forecast_carbon_cost_gbp_per_kwh).cast("float64"),
    )

    evaluated = evaluated.mutate(
        total_savings_gbp=(evaluated.baseline_total_cost_gbp - (evaluated.candidate_energy_cost_gbp + evaluated.candidate_carbon_cost_gbp)).cast("float64"),
        energy_cost_savings_gbp=(evaluated.baseline_energy_cost_gbp - evaluated.candidate_energy_cost_gbp).cast("float64"),
        carbon_savings_kg=(evaluated.baseline_carbon_kg - evaluated.candidate_carbon_kg).cast("float64"),
        carbon_cost_savings_gbp=(evaluated.baseline_carbon_cost_gbp - evaluated.candidate_carbon_cost_gbp).cast("float64"),
    )

    evaluated = evaluated.filter(
        (evaluated.total_savings_gbp > 0) & (evaluated.carbon_savings_kg > 0)
    )

    deduped = evaluated.group_by(
        "facility_id",
        "machine_facility_id",
        "machine_id",
        "machine_name",
        "machine_type",
        "day_of_week",
        "scheduled_hour",
        "candidate_start_hour",
        "tariff_bucket",
        "candidate_tariff_bucket",
    ).aggregate(
        energy_cost_savings_gbp=evaluated.energy_cost_savings_gbp.max(),
        carbon_savings_kg=evaluated.carbon_savings_kg.max(),
        carbon_cost_savings_gbp=evaluated.carbon_cost_savings_gbp.max(),
        total_savings_gbp=evaluated.total_savings_gbp.max(),
    )

    return deduped