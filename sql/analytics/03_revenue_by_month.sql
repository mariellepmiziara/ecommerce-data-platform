SELECT
    strftime('%Y-%m', order_date) AS month,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_order_value,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;