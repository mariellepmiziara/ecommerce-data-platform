SELECT
    ROUND(SUM(o.total_amount), 2) AS orders_total,
    ROUND(SUM(oi.net_amount), 2) AS order_items_total,
    ROUND(
        SUM(oi.net_amount) - SUM(o.total_amount),
        2
    ) AS difference
FROM orders o 
JOIN (
    SELECT
        order_id,
        SUM(net_amount) AS net_amount
    FROM order_items
    GROUP BY order_id
) oi
    ON o.order_id = oi.order_id;
