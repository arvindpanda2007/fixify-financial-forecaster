from fastmcp import FastMCP
from typing import Any

mcp = FastMCP("fixify_financial_forecaster")

def validate_amount(value: float):
    if value < 0:
        raise ValueError("amount cannot be negative")

@mcp.tool()
def forecast_scenario(
    name: str,
    forecast_months: int,
    costs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Calculate deterministic future cost for one scenario."""
    if forecast_months <= 0:
        raise ValueError("forecast_months must be greater than 0")

    monthly = [0.0] * (forecast_months + 1)

    for item in costs:
        month = int(item["month"])
        amount = float(item["amount"])
        if month < 0 or month > forecast_months:
            raise ValueError("cost month is outside the forecast period")
        validate_amount(amount)
        monthly[month] += amount

    total = sum(monthly)

    return {
        "scenario": name,
        "forecast_months": forecast_months,
        "total_cost": round(total, 2),
        "average_monthly_cost": round(total / forecast_months, 2),
        "cumulative_monthly_cost": [
            {
                "month": month,
                "cost_in_month": round(monthly[month], 2),
                "cumulative_cost": round(sum(monthly[:month + 1]), 2),
            }
            for month in range(forecast_months + 1)
        ],
    }

@mcp.tool()
def compare_scenarios(
    forecast_months: int,
    scenarios: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare future costs. Returns calculations only, never a recommendation."""
    if not scenarios:
        raise ValueError("At least one scenario is required")

    results = []
    for scenario in scenarios:
        result = forecast_scenario(
            str(scenario["name"]),
            forecast_months,
            scenario["costs"],
        )
        results.append({
            "name": result["scenario"],
            "total_cost": result["total_cost"],
            "average_monthly_cost": result["average_monthly_cost"],
        })

    lowest = min(x["total_cost"] for x in results)

    for result in results:
        result["difference_from_lowest_total"] = round(
            result["total_cost"] - lowest, 2
        )

    return {
        "forecast_months": forecast_months,
        "scenarios": results,
        "note": "Mathematical comparison only; no recommendation is made.",
    }

@mcp.tool()
def calculate_emi(
    appliance_price: float,
    down_payment: float,
    monthly_emi: float,
    tenure_months: int,
    fees: float = 0.0,
) -> dict[str, Any]:
    """Calculate totals from a supplied EMI offer."""
    for value in (appliance_price, down_payment, monthly_emi, fees):
        validate_amount(float(value))

    if tenure_months <= 0:
        raise ValueError("tenure_months must be greater than 0")
    if down_payment > appliance_price:
        raise ValueError("down_payment cannot exceed appliance_price")

    financed_amount = appliance_price - down_payment
    total_emi_payment = monthly_emi * tenure_months
    total_amount_paid = down_payment + total_emi_payment + fees

    return {
        "appliance_price": round(appliance_price, 2),
        "down_payment": round(down_payment, 2),
        "financed_amount": round(financed_amount, 2),
        "monthly_emi": round(monthly_emi, 2),
        "tenure_months": tenure_months,
        "total_emi_payment": round(total_emi_payment, 2),
        "fees": round(fees, 2),
        "total_amount_paid": round(total_amount_paid, 2),
        "finance_cost": round(total_amount_paid - appliance_price, 2),
        "average_monthly_outflow": round(
            total_amount_paid / tenure_months, 2
        ),
    }

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
