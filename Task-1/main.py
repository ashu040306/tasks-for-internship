import sqlite3
import pandas as pd


conn = sqlite3.connect(r"C:\Users\ashub\OneDrive\Desktop\sales pro\sales_pro\sales.db")
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
    payment_id TEXT
)
""")

conn.commit()
print("Table created")


with open(r"C:\Users\ashub\OneDrive\Desktop\sales pro\sales_pro\order_detail.txt", "r") as file:
    sql_script = file.read()

sql_script = sql_script.replace("INSERT IGNORE", "INSERT")

cursor.executescript(sql_script)
conn.commit()

print("Data inserted successfully")


#  OVERALL WEEKEND vs WEEKDAY

query_overall = """
WITH daily_sales AS (
    SELECT 
        DATE(order_date) AS order_day,

        CASE 
            WHEN strftime('%w', DATE(order_date)) IN ('0','6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS type,

        SUM(before_discount) AS daily_total

    FROM order_detail

    WHERE order_date LIKE '2021-10%'
       OR order_date LIKE '2021-11%'
       OR order_date LIKE '2021-12%'

    GROUP BY order_day, type
)

SELECT 
    type,
    ROUND(AVG(daily_total),2) AS avg_sales
FROM daily_sales
GROUP BY type;
"""

df_overall = pd.read_sql_query(query_overall, conn)
print("\n🔹 Overall Weekend vs Weekday:")
print(df_overall)


#  MONTH-WISE ANALYSIS

query_month = """
WITH daily_sales AS (
    SELECT 
        DATE(order_date) AS order_day,

        CASE 
            WHEN order_date LIKE '2021-10%' THEN 'October'
            WHEN order_date LIKE '2021-11%' THEN 'November'
            WHEN order_date LIKE '2021-12%' THEN 'December'
        END AS month_name,

        CASE 
            WHEN strftime('%w', DATE(order_date)) IN ('0','6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS type,

        SUM(before_discount) AS daily_total

    FROM order_detail

    WHERE order_date LIKE '2021-10%'
       OR order_date LIKE '2021-11%'
       OR order_date LIKE '2021-12%'

    GROUP BY order_day, month_name, type
)

SELECT 
    month_name,
    type,
    ROUND(AVG(daily_total),2) AS avg_sales
FROM daily_sales
GROUP BY month_name, type
ORDER BY month_name;
"""

df_month = pd.read_sql_query(query_month, conn)
print("\n🔹 Month-wise Analysis:")
print(df_month)


# CALCULATE DIFFERENCE


pivot_df = df_month.pivot(index="month_name", columns="type", values="avg_sales")

# Calculate difference
pivot_df["Difference (Weekend - Weekday)"] = pivot_df["Weekend"] - pivot_df["Weekday"]

print("\n🔹 Difference (Weekend vs Weekday):")
print(pivot_df)


if df_overall.loc[df_overall['type']=='Weekend','avg_sales'].values[0] > \
   df_overall.loc[df_overall['type']=='Weekday','avg_sales'].values[0]:

    print("\n Insight: Weekend sales are HIGHER → Campaign is effective")
else:
    print("\n Insight: No significant increase in weekend sales")


conn.close()
df_month.to_csv("month_analysis_new.csv", index=False)
df_overall.to_csv("overall_analysis_new.csv", index=False)
