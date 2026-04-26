import sqlite3
import pandas as pd
from pathlib import Path


BASE_PATH = Path(__file__).parent

DB_FILE = BASE_PATH / "sales.db"
ORDER_FILE = BASE_PATH / "order_detail.csv"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("Database connected successfully")


cursor.execute("DROP TABLE IF EXISTS order_detail")

cursor.execute("""
CREATE TABLE order_detail (
    order_id TEXT,
    customer_id TEXT,
    order_date TEXT,
    sku_id TEXT,
    price REAL,
    qty_ordered INTEGER,
    before_discount REAL,
    discount REAL,
    after_discount REAL,
    is_gross INTEGER,
    is_valid INTEGER,
    is_net INTEGER,
    payment_id TEXT,
    payment_method TEXT,
    cogs REAL
)
""")

conn.commit()
print("Table created successfully")


df_order = pd.read_csv(ORDER_FILE)

df_order.columns = [
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


# -----------------------------
# CREATE PAYMENT METHOD
# -----------------------------
payment_map = {
    1: "Credit Card",
    2: "Debit Card",
    3: "JazzCash",
    4: "EasyPaisa",
    5: "Cash on Delivery"
}

df_order["payment_method"] = df_order["payment_id"].map(payment_map)


# -----------------------------
# CREATE COGS
# -----------------------------
# Estimated COGS because cogs column is not available in current dataset
df_order["cogs"] = df_order["before_discount"] * 0.70


df_order.to_sql("order_detail", conn, if_exists="append", index=False)

print("Data inserted successfully")


# -----------------------------
# PAYMENT METHOD PERFORMANCE
# -----------------------------
query_payment = """
SELECT
    payment_method,

    ROUND(SUM(before_discount), 2) AS total_sales,

    SUM(qty_ordered) AS total_quantity_sold,

    ROUND(SUM(after_discount - cogs), 2) AS total_net_profit

FROM order_detail

GROUP BY payment_method

ORDER BY total_sales DESC;
"""

df_payment = pd.read_sql_query(query_payment, conn)

print("\nPayment Method Performance:")
print(df_payment)


# -----------------------------
# MONTH-WISE PAYMENT METHOD PERFORMANCE
# -----------------------------
query_month = """
SELECT
    strftime('%Y-%m', order_date) AS month,
    payment_method,

    ROUND(SUM(before_discount), 2) AS total_sales,

    SUM(qty_ordered) AS total_quantity_sold,

    ROUND(SUM(after_discount - cogs), 2) AS total_net_profit

FROM order_detail

GROUP BY month, payment_method

ORDER BY month, total_sales DESC;
"""

df_month = pd.read_sql_query(query_month, conn)

print("\nMonth-wise Payment Method Performance:")
print(df_month.head(20))


# -----------------------------
# QUARTER-WISE PAYMENT METHOD PERFORMANCE
# -----------------------------
query_quarter = """
SELECT
    CASE
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        WHEN CAST(strftime('%m', order_date) AS INTEGER) BETWEEN 10 AND 12 THEN 'Q4'
    END AS quarter,

    payment_method,

    ROUND(SUM(before_discount), 2) AS total_sales,

    SUM(qty_ordered) AS total_quantity_sold,

    ROUND(SUM(after_discount - cogs), 2) AS total_net_profit

FROM order_detail

GROUP BY quarter, payment_method

ORDER BY quarter, total_sales DESC;
"""

df_quarter = pd.read_sql_query(query_quarter, conn)

print("\nQuarter-wise Payment Method Performance:")
print(df_quarter)


# -----------------------------
# SAVE CSV FILES
# -----------------------------
df_payment.to_csv(BASE_PATH / "payment_method_performance.csv", index=False)
df_month.to_csv(BASE_PATH / "payment_method_monthly_performance.csv", index=False)
df_quarter.to_csv(BASE_PATH / "payment_method_quarterly_performance.csv", index=False)

print("\nCSV files saved successfully")

conn.close()
print("Database connection closed")