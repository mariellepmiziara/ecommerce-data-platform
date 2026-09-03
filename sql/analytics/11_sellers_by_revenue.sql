SELECT 
    s.seller_id,
    s.seller_name,
    s.state,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(t.order_total_amount_trusted), 2) AS revenue
FROM orders o   
JOIN sellers s ON s.seller_id = o.seller_id 
JOIN vw_orders_trusted t ON t.order_id = o.order_id
GROUP BY s.seller_id, s.seller_name, s.state
ORDER BY revenue DESC
LIMIT 10;