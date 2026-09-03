CREATE VIEW vw_orders_trusted AS
SELECT
    o.order_id,
    o.customer_id,
    o.seller_id,
    o.order_date,
    o.status,
    o.payment_method,
    o.total_amount AS orders_total_amount_raw,
    COALESCE(SUM(oi.net_amount), 0) AS order_total_amount_trusted
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.customer_id, o.seller_id, o.order_date, o.status, o.payment_method, o.total_amount;