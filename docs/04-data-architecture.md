# Raw data and ingestion contract

The authoritative nine-table schema is [raw_schema.sql](../data_platform/raw_schema.sql). It preserves original source column names, including source misspellings. IDs are text, postal prefixes are text (leading zeros matter), money is numeric(18,2), coordinates numeric, and source dates are timestamp without time zone.

Source timestamps have no time-zone offset. Preserve naive source business time; do not manufacture UTC. Group into calendar days/months using those values. System/audit timestamps use UTC. Historical demos use explicit dates; live freshness rules cannot compare a 2018 archive to today's clock.

## Grains and source keys

| Table | Source grain | Candidate key / concern |
| --- | --- | --- |
| customers | Order-specific customer record | customer_id; customer_unique_id identifies a person across orders |
| orders | Order | order_id |
| order_items | Item position in an order | order_id + order_item_id; each row is one item, no quantity column |
| products | Product | product_id |
| sellers | Seller | seller_id |
| payments | Payment component | order_id + payment_sequential; multiple per order |
| reviews | Review response | review_id is not assumed unique; multiple reviews/responses possible |
| geolocation | Postal observation | No unique zip key; repeated prefixes and coordinates are expected |
| product_category_translation | Category translation | product_category_name |

Raw landing tables intentionally have no business PK/FK/check constraints so anomalous source records remain inspectable. Loader must validate headers, parse types and record rejected rows with batch/line provenance; no silent lossy casts. Load a batch atomically, record source hashes, and publish only after required quality checks. Ingestion implementation belongs to Stage 1.

Stage keys are checked before downstream publication. For reviews select latest review_answer_timestamp then review_creation_date then review_id per order; exact duplicate rows may be collapsed, conflicting ties fail quality. Geolocation is aggregated to a unique prefix before joining, using median latitude/longitude; never join raw geolocation directly to facts.

Customer IDs and seller/product IDs are pseudonymous source identifiers, not proof that records are non-sensitive. Free-text review fields and fine geolocation stay in raw and are excluded from agent-visible marts and logs.

