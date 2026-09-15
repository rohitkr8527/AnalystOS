-- Test-only contract views over source-shaped synthetic CSVs.
-- Portable SQL subset used for offline numeric checks; production runs PostgreSQL/dbt.
CREATE VIEW dim_customer AS
SELECT customer_unique_id, MIN(customer_state) AS customer_state
FROM customers GROUP BY customer_unique_id;
CREATE VIEW dim_product AS
SELECT p.product_id, COALESCE(t.product_category_name_english, 'unknown') AS category
FROM products p LEFT JOIN product_category_translation t USING (product_category_name);
CREATE VIEW dim_seller AS SELECT seller_id, seller_state FROM sellers;
CREATE VIEW fct_order_items AS
SELECT i.order_id, CAST(i.order_item_id AS INTEGER) AS order_item_id,
       i.product_id, i.seller_id, p.category,
       SUBSTR(o.order_purchase_timestamp, 1, 10) AS purchase_date,
       SUBSTR(o.order_purchase_timestamp, 1, 7) AS purchase_month,
       o.order_status IN ('delivered','shipped','processing','invoiced','approved') AS is_valid,
       CAST(i.price AS REAL) AS item_price, CAST(i.freight_value AS REAL) AS freight_value
FROM order_items i JOIN orders o USING (order_id) JOIN dim_product p USING (product_id);
CREATE VIEW fct_orders AS
SELECT o.order_id, c.customer_unique_id, c.customer_state,
       SUBSTR(o.order_purchase_timestamp, 1, 10) AS purchase_date,
       SUBSTR(o.order_purchase_timestamp, 1, 7) AS purchase_month,
       o.order_status, o.order_status IN ('delivered','shipped','processing','invoiced','approved') AS is_valid,
       o.order_status = 'delivered' AS is_delivered,
       NULLIF(o.order_delivered_customer_date, '') AS delivered_at,
       NULLIF(o.order_estimated_delivery_date, '') AS estimated_at,
       o.order_status = 'delivered' AND o.order_delivered_customer_date > o.order_estimated_delivery_date AS is_late,
       i.revenue, i.freight, CAST(r.review_score AS INTEGER) AS review_score
FROM orders o JOIN customers c USING (customer_id)
JOIN (SELECT order_id, SUM(CAST(price AS REAL)) AS revenue,
             SUM(CAST(freight_value AS REAL)) AS freight FROM order_items GROUP BY order_id) i USING (order_id)
LEFT JOIN (SELECT *, ROW_NUMBER() OVER (
    PARTITION BY order_id ORDER BY review_answer_timestamp DESC, review_creation_date DESC, review_id DESC
) AS position FROM reviews) r ON o.order_id = r.order_id AND r.position = 1;
CREATE VIEW fct_payments AS
SELECT p.order_id, CAST(p.payment_sequential AS INTEGER) AS payment_sequential,
       p.payment_type, CAST(p.payment_value AS REAL) AS payment_value,
       o.purchase_date, o.purchase_month, o.is_valid
FROM payments p JOIN fct_orders o USING (order_id);
CREATE VIEW mart_monthly_sales AS
SELECT purchase_month, SUM(revenue) AS revenue, COUNT(*) AS orders,
       SUM(revenue)/COUNT(*) AS average_order_value
FROM fct_orders WHERE is_valid GROUP BY purchase_month;
CREATE VIEW mart_category_performance AS
SELECT category, purchase_month, SUM(item_price) AS revenue, COUNT(*) AS items,
       COUNT(DISTINCT order_id) AS orders
FROM fct_order_items WHERE is_valid GROUP BY category, purchase_month;
