-- database: ../data/database/ecommerce.db
SELECT
    status,
    COUNT(*) AS total_orders,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_order_value
FROM orders
GROUP BY status
ORDER BY total_revenue DESC;