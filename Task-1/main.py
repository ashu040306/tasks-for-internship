import sqlite3
import pandas as pd
from pathlib import Path


# ==============================
# FILE PATHS
# ==============================
BASE_PATH = Path(__file__).parent

DB_FILE = BASE_PATH / "sales.db"
ORDER_FILE = BASE_PATH / "order_detail.csv"


# ==============================
# CONNECT DATABASE
# ==============================
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("Database connected successfully")


# ==============================
# CREATE TABLE
# ==============================
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
    payment_id TEXT
)
""")

conn.commit()
print("Table created successfully")


# ==============================
# LOAD CSV
# ==============================
df = pd.read_csv(ORDER_FILE)

# Remove unwanted index column if exists
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# Rename CSV columns correctly
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

df.to_sql(
    "order_detail",
    conn,
    if_exists="append",
    index=False
)

print("Data loaded successfully")


# ==============================
# OVERALL WEEKEND VS WEEKDAY
# ==============================
query_overall = """
WITH daily_sales AS (
    SELECT 
        DATE(order_date) AS order_day,

        CASE 
            WHEN strftime('%w', DATE(order_date)) IN ('0','6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,

        SUM(before_discount) AS daily_total

    FROM order_detail

    WHERE order_date LIKE '2022-10%'
       OR order_date LIKE '2022-11%'
       OR order_date LIKE '2022-12%'

    GROUP BY order_day, day_type
)

SELECT 
    day_type,
    ROUND(AVG(daily_total), 2) AS avg_sales
FROM daily_sales
GROUP BY day_type;
"""

df_overall = pd.read_sql_query(query_overall, conn)

print("\nOverall Weekend vs Weekday:")
print(df_overall)


# ==============================
# MONTH-WISE ANALYSIS
# ==============================
query_month = """
WITH daily_sales AS (
    SELECT 
        DATE(order_date) AS order_day,

        CASE 
            WHEN order_date LIKE '2022-10%' THEN 'October'
            WHEN order_date LIKE '2022-11%' THEN 'November'
            WHEN order_date LIKE '2022-12%' THEN 'December'
        END AS month_name,

        CASE 
            WHEN strftime('%w', DATE(order_date)) IN ('0','6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type,

        SUM(before_discount) AS daily_total

    FROM order_detail

    WHERE order_date LIKE '2022-10%'
       OR order_date LIKE '2022-11%'
       OR order_date LIKE '2022-12%'

    GROUP BY order_day, month_name, day_type
)

SELECT 
    month_name,
    day_type,
    ROUND(AVG(daily_total), 2) AS avg_sales
FROM daily_sales
GROUP BY month_name, day_type
ORDER BY 
    CASE month_name
        WHEN 'October' THEN 1
        WHEN 'November' THEN 2
        WHEN 'December' THEN 3
    END,
    day_type;
"""

df_month = pd.read_sql_query(query_month, conn)

print("\nMonth-wise Weekend vs Weekday Analysis:")
print(df_month)


# ==============================
# CALCULATE DIFFERENCE
# ==============================
pivot_df = df_month.pivot(
    index="month_name",
    columns="day_type",
    values="avg_sales"
)

pivot_df["Difference (Weekend - Weekday)"] = (
    pivot_df["Weekend"] - pivot_df["Weekday"]
)

print("\nDifference:")
print(pivot_df)


# ==============================
# INSIGHT
# ==============================
weekend_avg = df_overall.loc[
    df_overall["day_type"] == "Weekend",
    "avg_sales"
].values[0]

weekday_avg = df_overall.loc[
    df_overall["day_type"] == "Weekday",
    "avg_sales"
].values[0]

print("\nInsight:")

if weekend_avg > weekday_avg:
    print("Weekend sales are higher than weekday sales. The weekend campaign looks effective.")
else:
    print("Weekend sales are lower than weekday sales. The weekend campaign does not show strong improvement.")


# ==============================
# SAVE CSV FILES
# ==============================
df_month.to_csv(
    BASE_PATH / "monthly_weekend_vs_weekday_sales.csv",
    index=False
)

df_overall.to_csv(
    BASE_PATH / "overall_weekend_vs_weekday_sales.csv",
    index=False
)

pivot_df.to_csv(
    BASE_PATH / "weekend_weekday_difference.csv"
)

print("\nCSV files saved successfully")

conn.close()
print("Database connection closed")