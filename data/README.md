# Olist data

Source: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), owner `olistbr`, dataset version 2. Source attribution must remain in reports/demo documentation. The source lists CC BY-NC-SA 4.0: retain attribution, use non-commercially and observe share-alike terms when distributing adaptations. Review the source terms before a different use.

The dataset covers Brazilian marketplace orders from 2016–2018. It has orders, items, order-specific customers, products, sellers, payment components, review responses, postal observations and category translations. It does not contain margin, acquisition spend, inventory history or reliable refund transactions.

## Acquisition

```powershell
python scripts/download_olist.py
uv run python scripts/verify_foundation.py --with-raw
```

The script downloads the pinned public Kaggle ZIP over HTTPS, extracts only the nine expected filenames, checks CSV shape and writes `olist-manifest.json` with source/version, UTC acquisition time, headers, row counts and SHA-256 hashes. Hashes provide local reproducibility, not a publisher-signed authenticity claim. Archive and raw files are ignored by Git. Do not commit them.

If Kaggle requires authentication, sign in and download version 2 from the source page, save it as `data/downloads/olist-v2.zip`, then rerun the script. Keep account credentials out of the repository. Existing raw files are never overwritten; verification reports mismatches for investigation.

## Interpretation limits

Source timestamps are naive business timestamps; preserve that meaning. Currency is BRL. customer_id is order-specific; customer_unique_id supports repeat behavior. Payment rows and item rows are both one-to-many with orders. Review IDs and postal prefixes must not be assumed globally unique. Missing translations become `unknown`; missing dates, malformed types and unexpected status values require visible quality handling.

Historical data has uneven and partial endpoint periods. Freshness uses declared batch completeness and requested period, not today's wall clock. Establish complete periods during ingestion before drawing trend conclusions.

`fixtures/` contains original synthetic data, committed for deterministic tests. Its values are not Olist facts. See [testing strategy](../docs/12-testing-strategy.md) and [raw schema](../data_platform/raw_schema.sql).
