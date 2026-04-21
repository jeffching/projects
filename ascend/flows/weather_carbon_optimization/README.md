# Weather Carbon Optimization

Flow: #flow:weather_carbon_optimization

## Components

- local reads: @flows/weather_carbon_optimization/components/read_facilities.yaml, @flows/weather_carbon_optimization/components/read_machines.yaml, @flows/weather_carbon_optimization/components/read_production_schedule.yaml
- live weather and carbon reads: @flows/weather_carbon_optimization/components/read_weather_history.py, @flows/weather_carbon_optimization/components/read_carbon_history.py, @flows/weather_carbon_optimization/components/read_weather_forecast.py
- modeling: @flows/weather_carbon_optimization/components/weather_carbon_history_features.py, @flows/weather_carbon_optimization/components/weather_carbon_hourly_model.py, @flows/weather_carbon_optimization/components/weather_carbon_forecast_features.py, @flows/weather_carbon_optimization/components/weather_carbon_forecast_predictions.py
- optimization: @flows/weather_carbon_optimization/components/machine_schedule_baseline.py, @flows/weather_carbon_optimization/components/machine_reschedule_candidates.py, @flows/weather_carbon_optimization/components/machine_reschedule_recommendations.py

## Live data windows

- #component:read_weather_history pulls a rolling 30-day hourly weather history ending at the current UTC hour.
- #component:read_carbon_history pulls a rolling 30-day hourly carbon history ending at the current UTC hour.
- #component:read_weather_forecast pulls a 7-day hourly forecast and stamps all rows with a single run-level `forecast_generated_at` timestamp.

## Dashboard

- application: @applications/weather-carbon-optimization-dashboard-v1/weather-carbon-optimization-dashboard.tsx

## Output

The flow produces machine rescheduling recommendations with estimated energy savings, carbon savings, and total gross savings by facility, day, and machine.