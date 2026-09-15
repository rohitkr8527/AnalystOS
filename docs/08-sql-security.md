# SQL policy contract

This is the required implementation policy for Stage 2; no production SQL validator exists yet.

1. Parse exactly one PostgreSQL statement with SQLGlot; parsing errors fail closed. Allow SELECT and non-recursive WITH that resolve entirely to read-only SELECTs. Inspect the entire AST including nested CTEs.
2. Resolve names/aliases against vetted catalog metadata. Permit only approved marts tables/columns for the actor. Reject raw/staging/intermediate, system catalogs, cross-database references, unknown names and unqualified ambiguous relations.
3. Reject DML/DDL anywhere, SELECT INTO, locking clauses, COPY, SET, CALL, DO, transaction control, recursive CTEs and multi-statements. Reject arbitrary/user-defined functions and file/network/dblink/large-object/sleep functions. Maintain a small allowlist of safe aggregate/date/math functions.
4. Bind user values; never interpolate them. Identifiers come from resolved metadata, not raw user input. Reject unbounded cross joins; cap joins/subquery depth from config. Inspect EXPLAIN (without ANALYZE) under the reader identity; reject costs above configured threshold.
5. Execute in a read-only transaction with a database-side 30-second timeout. Enforce an outer result cap of 10,000 rows, bounded fetching and explicit truncation evidence; an LLM's LIMIT is insufficient. Count failed/retried attempts against budgets.
6. Record actor, parsed query hash, bindings with sensitive values redacted, resolved models, policy decision and query ID. Only bounded evidence is shared with agents.

Database privileges are independent protection, not a replacement for parsing. Reader has no warehouse ownership, DDL, schema CREATE, write grants or application DB access. Only loader-created marts receive future SELECT grants. Defaults such as read-only transactions can be changed by a session, so grants and AST restrictions remain mandatory.

Required negative tests include writable CTEs, comments/multi-statements, quoted identifiers, nested forbidden calls, SELECT INTO, alias spoofing, catalog reads, sleep functions, giant joins, invalid columns, timeouts and row truncation. Required positive tests include valid aggregates, window functions and non-recursive CTEs.

Reference: [PostgreSQL privileges](https://www.postgresql.org/docs/current/ddl-priv.html).

