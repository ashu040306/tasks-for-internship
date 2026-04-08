import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path


# -----------------------------
# FILE PATHS
# -----------------------------
BASE_PATH = Path(__file__).parent

DB_FILE = BASE_PATH / "sales.db"
ORDER_FILE = BASE_PATH / "order_detail.csv"


# -----------------------------
# CONNECT DATABASE
# -----------------------------
conn = sqlite3.connect(DB_FILE)

print("Database connected successfully")


# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv(ORDER_FILE)

df.columns = [
    "order_id",
    "customer_id",
    "order_date",
    "sku_id",
    "price",
    "qty_ordered",
    "before_discount",
    "discount",
    "after_discount",
    "is_gross",
    "is_valid",
    "is_net",
    "payment_id"
]

print("Data loaded successfully")


# -----------------------------
# DATE PROCESSING
# -----------------------------
df["order_date"] = pd.to_datetime(df["order_date"])

df["year"] = df["order_date"].dt.year
df["month"] = df["order_date"].dt.month


# -----------------------------
# FILTER 2022 DATA
# -----------------------------
df_2022 = df[df["year"] == 2022]


# -----------------------------
# MONTHLY SALES
# -----------------------------
monthly_sales = (
    df_2022.groupby("month")["qty_ordered"]
    .sum()
    .reset_index()
)

print("\nMonthly Sales 2022:")
print(monthly_sales)


# -----------------------------
# NUMPY LINEAR REGRESSION
# -----------------------------
x = monthly_sales["month"].values
y = monthly_sales["qty_ordered"].values


# Calculate slope and intercept
slope, intercept = np.polyfit(x, y, 1)

print("\nModel created using NumPy")


# -----------------------------
# PREDICT TRAIN DATA
# -----------------------------
y_pred = slope * x + intercept


# -----------------------------
# EVALUATE MODEL
# -----------------------------
mae = np.mean(np.abs(y - y_pred))

rmse = np.sqrt(np.mean((y - y_pred) ** 2))

print("\nModel Evaluation:")
print("MAE:", round(mae, 2))
print("RMSE:", round(rmse, 2))


# -----------------------------
# PREDICT Q2 2023
# -----------------------------
future_months = np.array([4, 5, 6])

future_predictions = slope * future_months + intercept


forecast_df = pd.DataFrame({
    "month": ["April", "May", "June"],
    "predicted_sales": future_predictions
})

print("\nPredicted Sales for Q2 2023:")
print(forecast_df)


# -----------------------------
# TREND IDENTIFICATION
# -----------------------------
if future_predictions[-1] > future_predictions[0]:
    trend = "Increasing"
else:
    trend = "Decreasing"

print("\nSales Trend:", trend)


# -----------------------------
# SAVE TO SQLITE
# -----------------------------
monthly_sales.to_sql(
    "monthly_sales_2022",
    conn,
    if_exists="replace",
    index=False
)

forecast_df.to_sql(
    "sales_forecast_Q2_2023",
    conn,
    if_exists="replace",
    index=False
)


# -----------------------------
# SAVE CSV FILES
# -----------------------------
monthly_sales.to_csv(
    BASE_PATH / "monthly_sales_2022.csv",
    index=False
)

forecast_df.to_csv(
    BASE_PATH / "sales_forecast_Q2_2023.csv",
    index=False
)

print("\nCSV files saved successfully")

conn.close()

print("Database connection closed")