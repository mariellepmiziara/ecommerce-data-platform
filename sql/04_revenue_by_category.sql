-- database: ../data/database/ecommerce.db
SELECT  
    p.category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS total_items,
    ROUND(SUM(oi.net_amount), 2) AS total_revenue,
    ROUND(AVG(oi.net_amount), 2) AS average_item_value
FROM order_items AS oi
JOIN products AS p 
    ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;