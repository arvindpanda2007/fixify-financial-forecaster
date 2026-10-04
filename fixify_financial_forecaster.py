    {
        "month": 0,
        "amount": 4500
    }

    Recurring monthly cost:
    {
        "month": 1,
        "amount": 1500,
        "recurring": true,
        "frequency": "monthly"
    }

    Supported recurring frequencies:
    - monthly
    - quarterly
    - yearly

    The tool performs deterministic calculations only.
    It does not recommend an option.
    """

    return _calculate_scenario(scenario)


@mcp.tool()
def compare_scenarios(
    forecast_months: int,
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compare multiple scenarios over the same period.

    Example:
    {
        "forecast_months": 24,
        "scenarios": [
            {
                "name": "AMC",
                "costs": [
                    {
                        "month": 0,
                        "amount": 4500
                    },
                    {
                        "month": 12,
                        "amount": 4500
                    }
                ]
            },
            {
                "name": "No AMC",
                "costs": [
                    {
                        "month": 1,
                        "amount": 1500,
                        "recurring": true,
                        "frequency": "monthly"
                    }
                ]
            }
        ]
    }

    The tool calculates each scenario.
    It does not recommend a winner.
    """

    if forecast_months < 0:
        raise ValueError(
            "forecast_months must be >= 0"
        )

    if (
        not isinstance(scenarios, list)
        or not scenarios
    ):
        raise ValueError(
            "scenarios must be a non-empty list"
        )

    results = []

    for scenario in scenarios:
        scenario_with_period = dict(scenario)
        scenario_with_period[
            "forecast_months"
        ] = forecast_months

        results.append(
            _calculate_scenario(
                scenario_with_period
            )
        )

    return {
        "forecast_months": forecast_months,
        "scenarios": results,
    }


if __name__ == "__main__":
    port = int(
        os.getenv("PORT", "8000")
    )

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )
