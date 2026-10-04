import os
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("fixify_financial_forecaster")


def _validate_scenario(scenario: dict[str, Any]) -> tuple[str, int, list[dict[str, Any]]]:
    name = str(scenario.get("name", "Unnamed scenario"))
    forecast_months = int(scenario.get("forecast_months", 0))
    costs = scenario.get("costs", [])

    if forecast_months < 0:
        raise ValueError("forecast_months must be >= 0")

    if not isinstance(costs, list):
        raise ValueError("costs must be a list of {month, amount} objects")

    normalized = []
    for item in costs:
        if not isinstance(item, dict):
            raise ValueError("Each cost must be an object with month and amount")

        month = int(item.get("month", 0))
        amount = float(item.get("amount", 0))

        if month < 0 or month > forecast_months:
            raise ValueError(
                f"Cost month {month} must be between 0 and forecast_months ({forecast_months})"
            )

        if amount < 0:
            raise ValueError("Cost amount must be >= 0")

        normalized.append({"month": month, "amount": amount})

    return name, forecast_months, normalized


def _calculate(scenario: dict[str, Any]) -> dict[str, Any]:
    name, forecast_months, costs = _validate_scenario(scenario)

    monthly = [0.0] * (forecast_months + 1)

    for cost in costs:
        monthly[cost["month"]] += cost["amount"]

    total = sum(monthly)
    average_monthly = total / forecast_months if forecast_months > 0 else total

    return {
        "name": name,
        "forecast_months": forecast_months,
        "total_cost": round(total, 2),
        "average_monthly_cost": round(average_monthly, 2),
        "costs_by_month": [
            {"month": month, "cost": round(amount, 2)}
            for month, amount in enumerate(monthly)
            if amount != 0
        ],
    }


@mcp.tool()
def forecast_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministically forecast the total cost of one scenario over a defined
    number of months.

    Input example:
    {
      "name": "AMC",
      "forecast_months": 24,
      "costs": [
        {"month": 0, "amount": 4500},
        {"month": 12, "amount": 4500}
      ]
    }

    This tool performs calculations only. It does not recommend whether the
    scenario should be chosen.
    """
    return _calculate(scenario)


@mcp.tool()
def compare_scenarios(
    forecast_months: int,
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Deterministically calculate and compare multiple cost scenarios over the
    same forecast period.

    Example:
    {
      "forecast_months": 24,
      "scenarios": [
        {
          "name": "AMC",
          "costs": [
            {"month": 0, "amount": 4500},
            {"month": 12, "amount": 4500}
          ]
        },
        {
          "name": "No AMC",
          "costs": [
            {"month": 6, "amount": 2500},
            {"month": 15, "amount": 3500}
          ]
        }
      ]
    }

    This tool calculates the scenarios. It does not make a recommendation.
    """
    if forecast_months < 0:
        raise ValueError("forecast_months must be >= 0")

    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a non-empty list")

    results = []

    for scenario in scenarios:
        scenario_with_period = dict(scenario)
        scenario_with_period["forecast_months"] = forecast_months
        results.append(_calculate(scenario_with_period))

    return {
        "forecast_months": forecast_months,
        "scenarios": results,
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
    )
