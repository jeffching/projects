from __future__ import annotations

import ibis
from ascend.application.context import ComponentExecutionContext
from ascend.resources import ref, test, transform


@transform(
    inputs=[ref("machine_reschedule_candidates")],
    tests=[
        test("count_greater_than", count=0, severity="warn"),
    ],
)
def machine_reschedule_recommendations(
    machine_reschedule_candidates: ibis.Table,
    context: ComponentExecutionContext,
) -> ibis.Table:
    evaluated = machine_reschedule_candidates.filter(
        (machine_reschedule_candidates.total_savings_gbp > 0)
        & (machine_reschedule_candidates.carbon_savings_kg > 0)
    )

    best_savings = evaluated.group_by("machine_id", "day_of_week").aggregate(
        best_total_savings_gbp=evaluated.total_savings_gbp.max()
    )

    recommendations = evaluated.join(
        best_savings,
        [
            evaluated.machine_id == best_savings.machine_id,
            evaluated.day_of_week == best_savings.day_of_week,
            evaluated.total_savings_gbp == best_savings.best_total_savings_gbp,
        ],
        how="inner",
    )

    return recommendations.distinct().select(
        "facility_id",
        "machine_facility_id",
        "machine_id",
        "machine_name",
        "machine_type",
        "day_of_week",
        recommendations.scheduled_hour.name("baseline_start_hour"),
        "candidate_start_hour",
        recommendations.tariff_bucket.name("baseline_tariff_bucket"),
        "candidate_tariff_bucket",
        "energy_cost_savings_gbp",
        "carbon_savings_kg",
        "carbon_cost_savings_gbp",
        "total_savings_gbp",
    )