from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("read_production_schedule"), ref("read_machines"), ref("weather_carbon_forecast_predictions")],
    tests=[
        test("count_greater_than", count=10),
        test("not_null", column="machine_id"),
        test("not_null", column="effective_cost_gbp_per_kwh"),
    ],
)
def machine_schedule_baseline(
    read_production_schedule: ibis.Table,
    read_machines: ibis.Table,
    weather_carbon_forecast_predictions: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    schedule = read_production_schedule.mutate(
        day_of_week_index=ibis.cases(
            (read_production_schedule.day_of_week == "Monday", 0),
            (read_production_schedule.day_of_week == "Tuesday", 1),
            (read_production_schedule.day_of_week == "Wednesday", 2),
            (read_production_schedule.day_of_week == "Thursday", 3),
            (read_production_schedule.day_of_week == "Friday", 4),
            (read_production_schedule.day_of_week == "Saturday", 5),
            else_=6,
        ).cast("int64"),
        scheduled_hour=read_production_schedule.scheduled_hour.cast("int64"),
        runtime_hours=read_production_schedule.runtime_hours.cast("int64"),
        energy_kwh=read_production_schedule.energy_kwh.cast("float64"),
    )
    machines = read_machines.select(
        "machine_id",
        read_machines.facility_id.name("machine_facility_id"),
        "machine_name",
        "machine_type",
        read_machines.kwh_per_hour.cast("float64").name("kwh_per_hour"),
        read_machines.max_daily_runtime_hours.cast("int64").name("max_daily_runtime_hours"),
        read_machines.min_runtime_hours.cast("int64").name("min_runtime_hours"),
        read_machines.schedulable.cast("int64").name("schedulable_flag"),
    )
    schedule = schedule.join(machines, [schedule.machine_id == machines.machine_id], how="left")

    forecast = weather_carbon_forecast_predictions.select(
        "timestamp_hour",
        weather_carbon_forecast_predictions.facility_id.name("forecast_facility_id"),
        weather_carbon_forecast_predictions.day_of_week_index.cast("int64").name("forecast_day_of_week_index"),
        weather_carbon_forecast_predictions.hour_of_day.cast("int64").name("forecast_hour_of_day"),
        "tariff_bucket",
        weather_carbon_forecast_predictions.tariff_rate_gbp_per_kwh.cast("float64").name("tariff_rate_gbp_per_kwh"),
        weather_carbon_forecast_predictions.predicted_carbon_intensity_gco2_per_kwh.cast("float64").name("predicted_carbon_intensity_gco2_per_kwh"),
        weather_carbon_forecast_predictions.carbon_cost_gbp_per_kwh.cast("float64").name("carbon_cost_gbp_per_kwh"),
        weather_carbon_forecast_predictions.effective_cost_gbp_per_kwh.cast("float64").name("effective_cost_gbp_per_kwh"),
    )

    baseline = schedule.join(
        forecast,
        [
            schedule.facility_id == forecast.forecast_facility_id,
            schedule.day_of_week_index == forecast.forecast_day_of_week_index,
            schedule.scheduled_hour == forecast.forecast_hour_of_day,
        ],
        how="left",
    )

    return baseline.mutate(
        schedulable=baseline.schedulable_flag == 1,
        baseline_energy_cost_gbp=(baseline.energy_kwh * baseline.tariff_rate_gbp_per_kwh).cast("float64"),
        baseline_carbon_kg=((baseline.energy_kwh * baseline.predicted_carbon_intensity_gco2_per_kwh) / ibis.literal(1000.0)).cast("float64"),
        baseline_carbon_cost_gbp=(baseline.energy_kwh * baseline.carbon_cost_gbp_per_kwh).cast("float64"),
        baseline_total_cost_gbp=(baseline.energy_kwh * baseline.effective_cost_gbp_per_kwh).cast("float64"),
        day_of_week_index=baseline.day_of_week_index.cast("int64"),
        scheduled_hour=baseline.scheduled_hour.cast("int64"),
        runtime_hours=baseline.runtime_hours.cast("int64"),
        schedulable_flag=baseline.schedulable_flag.cast("int64"),
    )