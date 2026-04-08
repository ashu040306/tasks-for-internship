# Task 3: Sales Prediction for the Next Quarter Using Historical Data

## Objective

The objective of this task is to predict total sales for the upcoming quarter (Q2 2023) using historical sales data from Q1 2022 to Q4 2022.  
The prediction helps the sales team plan inventory, marketing, and operational strategies.

---

## Scenario

The Sales Team wants to forecast future sales based on past performance.  
Using historical monthly sales data from 2022, a prediction model is built to estimate total sales for the next quarter (April–June 2023).

---

## Tools and Technologies Used

- Python
- NumPy
- Pandas
- SQLite
- VS Code
- Google Looker Studio

---

## Dataset Features Used

The following fields were used from the dataset:

- order_date → Used to extract year and month
- qty_ordered → Used as the sales quantity

---

## Steps Performed

1. Loaded the sales dataset into Python.
2. Converted the order_date column into datetime format.
3. Extracted year and month from the order_date.
4. Filtered historical sales data for the year 2022.
5. Aggregated total monthly sales using group by.
6. Built a prediction model using NumPy Linear Regression.
7. Evaluated model accuracy using error metrics:
   - MAE (Mean Absolute Error)
   - RMSE (Root Mean Squared Error)
8. Predicted sales for the next quarter (Q2 2023):
   - April 2023
   - May 2023
   - June 2023
9. Identified the overall sales trend.
10. Exported prediction results to CSV files.
11. Visualized the predicted sales trend using Google Looker Studio.

---

## Model Used

A Linear Regression model was implemented using NumPy to forecast future sales based on historical monthly data.

Prediction Formula:

Sales = slope × month + intercept

---

## Model Evaluation Metrics

The model performance was evaluated using:

- MAE (Mean Absolute Error)  
  Measures the average difference between actual and predicted values.

- RMSE (Root Mean Squared Error)  
  Measures the square root of the average squared prediction errors.

These metrics help determine how accurate the prediction model is.

---

## Output Files Generated

The following files were created:

- monthly_sales_2022.csv  
  Contains total monthly sales for the year 2022

- sales_forecast_Q2_2023.csv  
  Contains predicted sales for April, May, and June 2023

- sales.db  
  SQLite database storing processed tables

---

## Visualization

A Line Chart was created in Google Looker Studio to visualize the predicted sales for Q2 2023.

Chart Details:

- Chart Type: Line Chart
- Dimension: month
- Metric: predicted_sales

---

## Trend Insight

Based on the prediction model, the sales trend for Q2 2023 shows:

- Increasing trend → Sales are expected to grow
OR
- Decreasing trend → Sales are expected to decline

(This depends on the actual model output.)

---

## Business Value

This prediction helps businesses:

- Plan inventory levels
- Forecast demand
- Optimize marketing strategies
- Improve financial planning
- Support data-driven decision making

---

## Repository Structure

Task-3

main.py  
README.md  
order_detail.csv  
monthly_sales_2022.csv  
sales_forecast_Q2_2023.csv  

---

## Author

Data Analysis / Data Science Internship Task