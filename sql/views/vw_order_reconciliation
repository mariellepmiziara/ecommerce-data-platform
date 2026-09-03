CREATE VIEW vw_order_reconciliation AS
SELECT
    o.order_id,
    o.total_amount AS orders_total,
    COALESCE(SUM(oi.net_amount), 0) AS items_total,
    ROUND(o.total_amount - COALESCE(SUM(oi.net_amount), 0), 2) AS diff,
    CASE
        WHEN ABS(o.total_amount - COALESCE(SUM(oi.net_amount), 0)) > 0.01
        THEN 'INCONSISTENT'
        ELSE 'OK'
    END AS reconciliation_status
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.total_amount;

SELECT * FROM vw_order_reconciliation WHERE reconciliation_status = 'INCONSISTENT';