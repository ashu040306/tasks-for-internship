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
# LOAD order_detail DATA
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
print("order_detail data inserted successfully")


# -----------------------------
# LOAD sku_detail DATA
# -----------------------------
df_sku = pd.read_csv(SKU_FILE)
df_sku.to_sql("sku_detail", conn, if_exists="append", index=False)
print("sku_detail data inserted successfully")


# -----------------------------
# CATEGORY-WISE REVENUE ANALYSIS
# -----------------------------
query_category_revenue = """
SELECT
    s.category,
    ROUND(SUM(o.before_discount), 2) AS total_before_discount,
    ROUND(SUM(o.after_discount), 2) AS total_after_discount,
    ROUND(SUM(o.before_discount) - SUM(o.after_discount), 2) AS discount_impact
FROM order_detail o
LEFT JOIN sku_detail s
    ON o.sku_id = s.product_id
GROUP BY s.category
ORDER BY total_before_discount DESC;
"""

df_category = pd.read_sql_query(query_category_revenue, conn)

print("\n🔹 Category-wise Revenue Analysis:")
print(df_category)


# -----------------------------
# INSIGHT
# -----------------------------
if not df_category.empty:
    highest_discount = df_category.sort_values("discount_impact", ascending=False).iloc[0]

    print("\n🔹 Insight:")
    print(
        f"The category with the highest discount impact is '{highest_discount['category']}', "
        f"where revenue before discount was {highest_discount['total_before_discount']} "
        f"and revenue after discount was {highest_discount['total_after_discount']}. "
        f"The total discount impact is {highest_discount['discount_impact']}."
    )
else:
    print("\n🔹 Insight: No category data found.")


# -----------------------------
# SAVE OUTPUT
# -----------------------------
df_category.to_csv(BASE_PATH / "category_revenue_discount_impact.csv", index=False)

print("\nCSV file saved successfully")


# -----------------------------
# CLOSE CONNECTION
# -----------------------------
conn.close()
print("Database connection closed")