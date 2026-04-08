import sqlite3
import pandas as pd
from pathlib import Path


# -----------------------------
# FILE PATHS
# -----------------------------
BASE_PATH = Path(__file__).parent

DB_FILE = BASE_PATH / "sales.db"
ORDER_FILE = BASE_PATH / "order_detail.csv"
SKU_FILE = BASE_PATH / "sku_detail_clean.csv"


# -----------------------------
# CONNECT DATABASE
# -----------------------------
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print("Database connected successfully")


# -----------------------------
# DROP OLD TABLES
# -----------------------------
cursor.execute("DROP TABLE IF EXISTS order_detail")
cursor.execute("DROP TABLE IF EXISTS sku_detail")


# -----------------------------
# CREATE order_detail TABLE
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


# -----------------------------
# CREATE sku_detail TABLE
# -----------------------------
cursor.execute("""
CREATE TABLE sku_detail (
    product_id TEXT,
    sku_name TEXT,
    original_price REAL,
    discounted_price REAL,
    category TEXT
)
""")

conn.commit()
print("Tables created successfully")


# -----------------------------
# LOAD order_detail CSV
# -----------------------------
df_order = pd.read_csv(ORDER_FILE)

# Rename columns if needed
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
print("order_detail data inserted successfully")


# -----------------------------
# LOAD sku_detail CSV
# -----------------------------
df_sku = pd.read_csv(SKU_FILE)
df_sku.to_sql("sku_detail", conn, if_exists="append", index=False)
print("sku_detail data inserted successfully")


# -----------------------------
# 2021 SALES BY PRODUCT
# -----------------------------
query_2021 = """
SELECT 
    s.sku_name,
    SUM(o.qty_ordered) AS sales_2021
FROM order_detail o
LEFT JOIN sku_detail s
    ON o.sku_id = s.product_id
WHERE strftime('%Y', DATE(o.order_date)) = '2021'
GROUP BY s.sku_name
ORDER BY sales_2021 DESC;
"""

df_2021 = pd.read_sql_query(query_2021, conn)
print("\n🔹 2021 Sales by Product:")
print(df_2021.head(10))


# -----------------------------
# 2022 SALES BY PRODUCT
# -----------------------------
query_2022 = """
SELECT 
    s.sku_name,
    SUM(o.qty_ordered) AS sales_2022
FROM order_detail o
LEFT JOIN sku_detail s
    ON o.sku_id = s.product_id
WHERE strftime('%Y', DATE(o.order_date)) = '2022'
GROUP BY s.sku_name
ORDER BY sales_2022 DESC;
"""

df_2022 = pd.read_sql_query(query_2022, conn)
print("\n🔹 2022 Sales by Product:")
print(df_2022.head(10))


# -----------------------------
# SALES DIFFERENCE (2022 - 2021)
# -----------------------------
query_difference = """
WITH sales_2021 AS (
    SELECT 
        s.sku_name,
        SUM(o.qty_ordered) AS sales_2021
    FROM order_detail o
    LEFT JOIN sku_detail s
        ON o.sku_id = s.product_id
    WHERE strftime('%Y', DATE(o.order_date)) = '2021'
    GROUP BY s.sku_name
),

sales_2022 AS (
    SELECT 
        s.sku_name,
        SUM(o.qty_ordered) AS sales_2022
    FROM order_detail o
    LEFT JOIN sku_detail s
        ON o.sku_id = s.product_id
    WHERE strftime('%Y', DATE(o.order_date)) = '2022'
    GROUP BY s.sku_name
),

all_products AS (
    SELECT sku_name FROM sales_2021
    UNION
    SELECT sku_name FROM sales_2022
)

SELECT 
    a.sku_name,
    COALESCE(y21.sales_2021, 0) AS sales_2021,
    COALESCE(y22.sales_2022, 0) AS sales_2022,
    COALESCE(y22.sales_2022, 0) - COALESCE(y21.sales_2021, 0) AS sales_difference
FROM all_products a
LEFT JOIN sales_2021 y21
    ON a.sku_name = y21.sku_name
LEFT JOIN sales_2022 y22
    ON a.sku_name = y22.sku_name
ORDER BY sales_difference ASC;
"""

df_difference = pd.read_sql_query(query_difference, conn)

print("\n🔹 Sales Difference (2022 - 2021):")
print(df_difference.head(10))


# -----------------------------
# TOP 10 PRODUCTS WITH LARGEST DECREASE
# -----------------------------
df_top10 = df_difference.head(10)

print("\n🔹 Top 10 Products with Largest Decrease in Sales:")
print(df_top10)


# -----------------------------
# INSIGHT
# -----------------------------
if not df_top10.empty:
    largest_drop = df_top10.iloc[0]
    print("\n🔹 Insight:")
    print(
        f"The product with the highest decrease in sales is '{largest_drop['sku_name']}', "
        f"with sales dropping from {largest_drop['sales_2021']} in 2021 "
        f"to {largest_drop['sales_2022']} in 2022, "
        f"resulting in a difference of {largest_drop['sales_difference']}."
    )
else:
    print("\n🔹 Insight: No data found for the selected years.")


# -----------------------------
# SAVE OUTPUT FILES
# -----------------------------
df_2021.to_csv(BASE_PATH / "sales_2021_by_product.csv", index=False)
df_2022.to_csv(BASE_PATH / "sales_2022_by_product.csv", index=False)
df_difference.to_csv(BASE_PATH / "sales_difference_2021_2022.csv", index=False)
df_top10.to_csv(BASE_PATH / "top_10_products_largest_decrease.csv", index=False)

print("\nCSV files saved successfully")


# -----------------------------
# CLOSE CONNECTION
# -----------------------------
conn.close()
print("Database connection closed")