def run_pricing(cashflow_df, liquidity_level):
    prices = cashflow_df.copy()
    prices["price"] = 100

    curve = {
        "tenor": [1, 2, 3, 5, 10],
        "rate": [0.20, 0.22, 0.25, 0.27, 0.30]
    }

    return prices, curve
