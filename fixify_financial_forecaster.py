import os
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("fixify_financial_forecaster")


def _validate_scenario(
    scenario: dict[str, Any],
) -> tuple[str, int, list[dict[str, Any]]]:
    """Validate and normalize one financial scenario."""

    name = str(scenario.get("name", "Unnamed scenario"))
    forecast_months = int(scenario.get("forecast_months", 0))
    costs = scenario.get("costs", [])

    if forecast_months < 0:
        raise ValueError("forecast_months must be >= 0")

    if not isinstance(costs, list):
        raise ValueError(
            "costs must be a list of cost objects"
        )

    normalized = []

    for item in costs:
        if not isinstance(item, dict):
            raise ValueError(
                "Each cost must be an object"
            )

        month = int(item.get("month", 0))
        amount = float(item.get("amount", 0))
        recurring = bool(item.get("recurring", False))
        frequency = str(
            item.get("frequency", "monthly")
        ).lower()

        if month < 0 or month > forecast_months:
            raise ValueError(
                f"Cost month {month} must be between "
                f"0 and forecast_months ({forecast_months})"
            )

        if amount < 0:
            raise ValueError(
                "Cost amount must be >= 0"
            )

        if recurring and frequency not in {
            "monthly",
            "quarterly",
            "yearly",
        }:
            raise ValueError(
                "Recurring frequency must be "
                "monthly, quarterly, or yearly"
            )

        if not recurring:
            frequency = None

        normalized.append(
            {
                "month": month,
                "amount": amount,
                "recurring": recurring,
                "frequency": frequency,
            }
        )

    return name, forecast_months, normalized


def _frequency_interval(frequency: str) -> int:
    """Return recurrence interval in months."""

    intervals = {
        "monthly": 1,
        "quarterly": 3,
        "yearly": 12,
    }

    return intervals[frequency]


def _calculate_scenario(
    scenario: dict[str, Any],
) -> dict[str, Any]:
    """Perform deterministic cost calculations."""

    (
        name,
        forecast_months,
        costs,
    ) = _validate_scenario(scenario)

    monthly_costs = [
        0.0
        for _ in range(forecast_months + 1)
    ]

    for cost in costs:
        start_month = cost["month"]
        amount = cost["amount"]

        if not cost["recurring"]:
            monthly_costs[start_month] += amount
            continue

        interval = _frequency_interval(
            cost["frequency"]
        )

        month = start_month

        while month <= forecast_months:
            monthly_costs[month] += amount
            month += interval

    total_cost = sum(monthly_costs)

    if forecast_months > 0:
        average_monthly_cost = (
            total_cost / forecast_months
        )
    else:
        average_monthly_cost = total_cost

    return {
        "name": name,
        "forecast_months": forecast_months,
        "total_cost": round(total_cost, 2),
        "average_monthly_cost": round(
            average_monthly_cost,
            2,
        ),
        "costs_by_month": [
            {
                "month": month,
                "cost": round(amount, 2),
            }
            for month, amount in enumerate(
                monthly_costs
            )
            if amount != 0
        ],
    }


@mcp.tool()
def forecast_scenario(
    scenario: dict[str, Any],
) -> dict[str, Any]:
    """
    Forecast one scenario over a defined period.

    One-time cost:
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
