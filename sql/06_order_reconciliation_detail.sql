SELECT 
    o.order_id,
    ROUND(o.total_amount, 2) AS order_total,
    ROUND(SUM(oi.net_amount), 2) AS items_total,
    ROUND(
        SUM(oi.net_amount) - o.total_amount,
        2
    ) AS difference
FROM orders o 
JOIN order_items oi  
    ON o.order_id = oi.order_id
GROUP BY
    o.order_id,
    o.total_amount
ORDER BY ABS(difference) DESC
LIMIT 20;