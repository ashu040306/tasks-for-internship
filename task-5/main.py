import sqlite3
import pandas as pd
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
cursor = conn.cursor()

print("Database connected successfully")


# -----------------------------
# DROP TABLE IF EXISTS
# -----------------------------
cursor.execute("DROP TABLE IF EXISTS order_detail")


# -----------------------------
# CREATE TABLE
# -----------------------------
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
    payment_id TEXT
)
""")

conn.commit()
print("Table created successfully")


# -----------------------------
# LOAD DATA
# -----------------------------
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

df_order.to_sql("order_detail", conn, if_exists="append", index=False)

print("Data loaded successfully")


# -----------------------------
# MONTHLY AOV QUERY
# -----------------------------
query_aov = """
SELECT
    CAST(strftime('%m', order_date) AS INTEGER) AS month,

    ROUND(SUM(after_discount), 2) AS total_revenue,

    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(
        SUM(after_discount) /
        COUNT(DISTINCT order_id),
        2
    ) AS AOV

FROM order_detail

WHERE strftime('%Y', order_date) = '2022'

GROUP BY month

ORDER BY month;
"""


df_aov = pd.read_sql_query(query_aov, conn)

print("\nMonthly AOV 2022:")
print(df_aov)


# -----------------------------
# TREND INSIGHT
# -----------------------------
if df_aov["AOV"].iloc[-1] > df_aov["AOV"].iloc[0]:

    print("\nTrend: Increasing AOV")

else:

    print("\nTrend: Decreasing AOV")


# -----------------------------
# SAVE CSV
# -----------------------------
output_file = BASE_PATH / "monthly_aov_2022.csv"

df_aov.to_csv(output_file, index=False)

print("\nCSV file saved successfully")


# -----------------------------
# CLOSE CONNECTION
# -----------------------------
conn.close()

print("Database connection closed")