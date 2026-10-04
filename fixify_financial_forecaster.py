
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
