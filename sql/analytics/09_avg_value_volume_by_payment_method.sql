SELECT  
    o.payment_method,
    COUNT(*) AS total_orders,
    ROUND(AVG(t.order_total_amount_trusted), 2) AS avg_order_value,
    ROUND(SUM(t.order_total_amount_trusted), 2) AS total_revenue
FROM orders o            
JOIN vw_orders_trusted t ON t.order_id = o.order_id
GROUP BY o.payment_method
ORDER BY total_revenue DESC;