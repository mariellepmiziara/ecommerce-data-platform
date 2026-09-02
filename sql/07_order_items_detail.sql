-- database: ../data/database/ecommerce.db
SELECT 
    oi.order_item_id,
    oi.order_id,
    oi.product_id,
    p.product_name,
    p.category,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.discount_amount,
    oi.net_amount
FROM order_items oi
LEFT JOIN products p 
    ON oi.product_id = p.product_id
WHERE oi.order_id = 8481
ORDER BY oi.order_item_id;


SELECT
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount,
    gross_amount,
    discount_amount,
    net_amount
FROM order_items
WHERE order_id = 8481
ORDER BY order_item_id;

SELECT
    order_id,
    total_amount
FROM orders
WHERE order_id = 8481;

SELECT
    order_id,
    SUM(gross_amount) AS gross_total,
    SUM(discount_amount) AS discount_total,
    SUM(net_amount) AS items_total
FROM order_items
WHERE order_id = 8481
GROUP BY order_id;


SELECT
    COUNT(*) AS total_orders,
    SUM(
        CASE
            WHEN ABS(
                o.total_amount - oi.items_total
            ) > 0.01
            THEN 1
            ELSE 0
        END
    ) AS inconsistent_orders
FROM orders o
JOIN (
    SELECT
        order_id,
        SUM(net_amount) AS items_total
    FROM order_items
    GROUP BY order_id
) oi
    ON o.order_id = oi.order_id;


SELECT
    o.order_id,
    o.total_amount AS orders_total,
    COALESCE(SUM(oi.net_amount), 0) AS items_total,
    ROUND(o.total_amount - COALESCE(SUM(oi.net_amount), 0), 2) AS diff
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.total_amount
HAVING ABS(o.total_amount - COALESCE(SUM(oi.net_amount), 0)) > 0.01
ORDER BY ABS(diff) DESC;


WITH reconciliation AS (
    SELECT
        o.order_id,
        o.total_amount AS orders_total,
        COALESCE(SUM(oi.net_amount), 0) AS items_total
    FROM orders o
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY o.order_id, o.total_amount
)
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN ABS(orders_total - items_total) > 0.01 THEN 1 ELSE 0 END) AS orders_inconsistentes,
    ROUND(100.0 * SUM(CASE WHEN ABS(orders_total - items_total) > 0.01 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_inconsistente
FROM reconciliation;

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