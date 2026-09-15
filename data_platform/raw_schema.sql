-- Source-aligned landing tables. Quality constraints belong to staging tests.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE raw.customers (
    customer_id text, customer_unique_id text, customer_zip_code_prefix text,
    customer_city text, customer_state text
);
CREATE TABLE raw.orders (
    order_id text, customer_id text, order_status text,
    order_purchase_timestamp timestamp, order_approved_at timestamp,
    order_delivered_carrier_date timestamp, order_delivered_customer_date timestamp,
    order_estimated_delivery_date timestamp
);
CREATE TABLE raw.order_items (
    order_id text, order_item_id integer, product_id text, seller_id text,
    shipping_limit_date timestamp, price numeric(18,2), freight_value numeric(18,2)
);
CREATE TABLE raw.products (
    product_id text, product_category_name text, product_name_lenght integer,
    product_description_lenght integer, product_photos_qty integer,
    product_weight_g integer, product_length_cm integer, product_height_cm integer,
    product_width_cm integer
);
CREATE TABLE raw.sellers (
    seller_id text, seller_zip_code_prefix text, seller_city text, seller_state text
);
CREATE TABLE raw.payments (
    order_id text, payment_sequential integer, payment_type text,
    payment_installments integer, payment_value numeric(18,2)
);
CREATE TABLE raw.reviews (
    review_id text, order_id text, review_score integer, review_comment_title text,
    review_comment_message text, review_creation_date timestamp, review_answer_timestamp timestamp
);
CREATE TABLE raw.geolocation (
    geolocation_zip_code_prefix text, geolocation_lat numeric(12,8),
    geolocation_lng numeric(12,8), geolocation_city text, geolocation_state text
);
CREATE TABLE raw.product_category_translation (
    product_category_name text, product_category_name_english text
);

