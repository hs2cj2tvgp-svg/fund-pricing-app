import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from scipy.optimize import minimize

FACE_VALUE = 100


# =====================
# NSS MODEL
# =====================
def nss_spot_rate(t, beta0, beta1, beta2, beta3, tau1, tau2):
    if t <= 0:
        return beta0 + beta1

    term1 = beta0
    term2 = beta1 * ((1 - np.exp(-t / tau1)) / (t / tau1))
    term3 = beta2 * (((1 - np.exp(-t / tau1)) / (t / tau1)) - np.exp(-t / tau1))
    term4 = beta3 * (((1 - np.exp(-t / tau2)) / (t / tau2)) - np.exp(-t / tau2))

    return term1 + term2 + term3 + term4


# =====================
# PRICE
# =====================
def calculate_model_price(bond, params, today, liquidity_spread=0.0):
    beta0, beta1, beta2, beta3, tau1, tau2 = params

    coupon_rate = bond["coupon_rate"] / 100
    freq_months = bond["coupon_frequency"]
    coupon_dates = bond["coupon_payment_dates"]

    coupon_cf = FACE_VALUE * coupon_rate * (freq_months / 12)
    price = 0.0

    for i, d in enumerate(coupon_dates):
        payment_date = datetime.strptime(d, "%Y-%m-%d")
        days_diff = (payment_date - today).days

        if days_diff <= 0:
            continue

        t_years = days_diff / 365.0
        r = nss_spot_rate(t_years, beta0, beta1, beta2, beta3, tau1, tau2)

        if not bond["is_liquid"]:
            r += liquidity_spread

        cf = coupon_cf
        if i == len(coupon_dates) - 1:
            cf += FACE_VALUE

        price += cf / ((1 + r / 365.0) ** days_diff)

    return price


def calculate_duration(bond, params, today):
    beta0, beta1, beta2, beta3, tau1, tau2 = params

    coupon_rate = bond["coupon_rate"] / 100
    freq_months = bond["coupon_frequency"]
    coupon_dates = bond["coupon_payment_dates"]

    coupon_cf = FACE_VALUE * coupon_rate * (freq_months / 12)
    price, wsum = 0.0, 0.0

    for i, d in enumerate(coupon_dates):
        payment_date = datetime.strptime(d, "%Y-%m-%d")
        days_diff = (payment_date - today).days

        if days_diff <= 0:
            continue

        t_years = days_diff / 365.0
        r = nss_spot_rate(t_years, beta0, beta1, beta2, beta3, tau1, tau2)

        cf = coupon_cf
        if i == len(coupon_dates) - 1:
            cf += FACE_VALUE

        pv = cf / ((1 + r / 365.0) ** days_diff)

        price += pv
        wsum += t_years * pv

    return wsum / price if price > 0 else 1.0


def objective_function(params, bonds, today):
    error = 0.0

    for bond in bonds.values():
        if not bond["is_liquid"]:
            continue

        model_price = calculate_model_price(bond, params, today)
        market_price = bond["purchase_price"]
        duration = calculate_duration(bond, params, today)

        error += (1 / duration) * (model_price - market_price) ** 2

    return error


# =====================
# MAIN ENTRY POINT
# =====================
def run_pricing(
    cashflow_df: pd.DataFrame,
    liquidity_days: int,
    liquidity_spread: float,
):
    today = datetime.today()
    bonds = {}

    for i, (_, row) in enumerate(cashflow_df.iterrows(), start=1):
        bonds[f"Bond {i}"] = {
            "bond_name": row.iloc[0],
            "purchase_price": row.iloc[1],
            "purchase_date": row.iloc[2],
            "maturity_date": row.iloc[3],
            "coupon_frequency": row.iloc[4],
            "coupon_rate": row.iloc[5],
        }

    for bond in bonds.values():
        maturity_date = bond["maturity_date"]
        freq_months = bond["coupon_frequency"]

        coupon_dates = []
        current_date = maturity_date

        while current_date >= today:
            coupon_dates.append(current_date)
            current_date -= relativedelta(months=freq_months)

        coupon_dates.reverse()
        bond["coupon_payment_dates"] = [
            d.strftime("%Y-%m-%d") for d in coupon_dates
        ]

        bond["is_liquid"] = (today - bond["purchase_date"]).days <= liquidity_days

    initial_guess = [0.10, -0.05, 0.02, 0.01, 1.5, 3.0]
    bounds = [
        (0.0, 0.30),
        (-0.30, 0.30),
        (-0.30, 0.30),
        (-0.30, 0.30),
        (0.1, 10.0),
        (0.1, 10.0),
]