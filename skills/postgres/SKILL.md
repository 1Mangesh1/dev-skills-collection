---
name: postgres
description: PostgreSQL database commands, queries, administration, and troubleshooting. Use when user mentions "postgres", "psql", "postgresql", "database queries", "sql optimization", "pg_dump", "database backup", "postgres tuning", "connection pooling", "postgres roles", or any PostgreSQL task.
---

# PostgreSQL

## psql CLI Basics

Connect to a database:

```bash
psql -h localhost -p 5432 -U myuser -d mydb
psql "postgresql://myuser:mypass@localhost:5432/mydb?sslmode=require"
```

Common meta-commands inside psql:

```sql
\l                  -- list all databases
\c dbname           -- switch to database
\dt                 -- list tables in current schema
\dt schema_name.*   -- list tables in a specific schema
\d table_name       -- describe table (columns, indexes, constraints)
\di                 -- list indexes
\df                 -- list functions
\du                 -- list roles
\x                  -- toggle expanded output
\timing             -- toggle query timing
\e                  -- open last query in $EDITOR
\i file.sql         -- execute commands from file
\copy table TO '/tmp/out.csv' CSV HEADER  -- export to CSV
```

## Common Queries

### CRUD

```sql
INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com')
RETURNING id, created_at;

SELECT id, name, email FROM users WHERE active = true ORDER BY created_at DESC LIMIT 20;

UPDATE users SET email = 'new@example.com' WHERE id = 42 RETURNING *;

DELETE FROM orders WHERE created_at < now() - interval '2 years' RETURNING id;
```

### Joins

```sql
-- Inner join
SELECT o.id, u.name, o.total
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.status = 'completed';

-- Left join with coalesce for missing data
SELECT u.name, COALESCE(SUM(o.total), 0) AS lifetime_value
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.name;
```

### Subqueries

```sql
SELECT * FROM users
WHERE id IN (
  SELECT user_id FROM orders
  WHERE total > 500
  GROUP BY user_id
  HAVING COUNT(*) >= 3
);
```

### CTEs (Common Table Expressions)

```sql
WITH monthly_revenue AS (
  SELECT date_trunc('month', created_at) AS month,
         SUM(total) AS revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
)
SELECT month,
       revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly_revenue
ORDER BY month;
```

### Window Functions

```sql
SELECT
  user_id,
  created_at,
  total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn,
  SUM(total) OVER (PARTITION BY user_id) AS user_total,
  RANK() OVER (ORDER BY total DESC) AS overall_rank
FROM orders;
```

## Indexing

### B-tree (default, most common)

```sql
CREATE INDEX idx_users_email ON users (email);

-- Composite index (column order matters for query matching)
CREATE INDEX idx_orders_user_status ON orders (user_id, status);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users (lower(email));
```

### Partial Index

```sql
-- Only index active users; smaller index, faster lookups
CREATE INDEX idx_users_active ON users (email) WHERE active = true;
```

### GIN (for arrays, JSONB, full-text search)

```sql
CREATE INDEX idx_tags_gin ON articles USING gin (tags);
CREATE INDEX idx_data_gin ON events USING gin (payload jsonb_path_ops);
CREATE INDEX idx_fts ON articles USING gin (to_tsvector('english', body));
```

### GiST (for geometric, range, and proximity queries)

```sql
CREATE INDEX idx_location ON stores USING gist (location);
CREATE INDEX idx_daterange ON bookings USING gist (during);
```

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT * FROM orders WHERE user_id = 42;
```

Key things to look for: **Seq Scan** on large tables (missing index), **Nested Loop** with high row counts (needs Hash Join or index), high **Buffers: shared read** (data not cached), **Rows Removed by Filter** much larger than actual rows (index not selective enough).

## JSON/JSONB Operations

### Storing JSON

```sql
CREATE TABLE events (
  id bigserial PRIMARY KEY,
  payload jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

INSERT INTO events (payload)
VALUES ('{"type": "click", "page": "/home", "user": {"id": 1, "plan": "pro"}}');
```

### Querying JSON

```sql
-- Extract a text value
SELECT payload->>'type' AS event_type FROM events;

-- Nested access
SELECT payload->'user'->>'plan' AS plan FROM events;

-- Filter with containment operator
SELECT * FROM events WHERE payload @> '{"type": "click"}';

-- Check if key exists
SELECT * FROM events WHERE payload ? 'type';

-- Query array elements inside JSONB
SELECT * FROM events WHERE payload->'tags' @> '["urgent"]';

-- Aggregate JSONB values
SELECT payload->>'type' AS event_type, COUNT(*)
FROM events
GROUP BY 1
ORDER BY 2 DESC;
```

### Indexing JSON

```sql
-- GIN index for containment queries (@>, ?, ?|, ?&)
CREATE INDEX idx_events_payload ON events USING gin (payload jsonb_path_ops);

-- B-tree index on a specific extracted value
CREATE INDEX idx_events_type ON events ((payload->>'type'));
```

## Administration

### Roles and Permissions

```sql
-- Create a role
CREATE ROLE app_readonly LOGIN PASSWORD 'securepass';

-- Grant read access to all tables in a schema
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

-- Make it apply to future tables too
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- Create a readwrite role
CREATE ROLE app_readwrite LOGIN PASSWORD 'securepass';
GRANT USAGE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;

-- Revoke
REVOKE ALL ON DATABASE mydb FROM some_role;
```

### Backup and Restore

```bash
# Dump a single database (custom format, compressed)
pg_dump -Fc -h localhost -U myuser mydb > mydb.dump

# Dump specific tables
pg_dump -Fc -t users -t orders mydb > partial.dump

# Schema only / data only
pg_dump -s mydb > schema.sql
pg_dump -a -t users mydb > users_data.sql

# Restore from custom format dump
pg_restore -h localhost -U myuser -d mydb --no-owner mydb.dump

# Dump all databases
pg_dumpall -h localhost -U postgres > all_databases.sql
```

### Vacuuming

```sql
-- Manual vacuum (reclaim space, update planner stats)
VACUUM VERBOSE users;

VACUUM ANALYZE users;
VACUUM FULL users;  -- rewrites table, requires exclusive lock -- use sparingly

-- Check autovacuum stats
SELECT relname, last_vacuum, last_autovacuum, n_dead_tup, n_live_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

## Performance

### Identifying Slow Queries

Enable `pg_stat_statements` (add to `postgresql.conf` or `shared_preload_libraries`):

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 queries by total time
SELECT
  calls,
  round(total_exec_time::numeric, 2) AS total_ms,
  round(mean_exec_time::numeric, 2) AS mean_ms,
  round((100 * total_exec_time / SUM(total_exec_time) OVER ())::numeric, 2) AS pct,
  LEFT(query, 100) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### Active Queries and Locks

```sql
-- Currently running queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Kill a long-running query
SELECT pg_cancel_backend(pid);    -- graceful
SELECT pg_terminate_backend(pid); -- forceful

-- Check for lock contention
SELECT
  blocked.pid AS blocked_pid,
  blocked.query AS blocked_query,
  blocking.pid AS blocking_pid,
  blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
  AND blocked_locks.relation = blocking_locks.relation
  AND blocked_locks.pid != blocking_locks.pid
JOIN pg_stat_activity blocking ON blocking_locks.pid = blocking.pid
WHERE NOT blocked_locks.granted;
```

### Connection Pooling with PgBouncer

Minimal `pgbouncer.ini`:

```ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
```

Pool modes: **session** (held for entire client session, safest), **transaction** (returned after each transaction, best balance), **statement** (returned after each statement, breaks multi-statement transactions).

## Common Gotchas

### Idle Transactions

Idle-in-transaction connections hold locks and prevent vacuuming:

```sql
-- Find idle-in-transaction connections
SELECT pid, now() - state_change AS idle_duration, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY idle_duration DESC;

-- Set a timeout to auto-kill them
ALTER DATABASE mydb SET idle_in_transaction_session_timeout = '5min';
```

### Table Bloat

Dead tuples accumulate when autovacuum cannot keep up:

```sql
-- Estimate bloat ratio
SELECT
  relname,
  n_dead_tup,
  n_live_tup,
  round(n_dead_tup::numeric / GREATEST(n_live_tup, 1) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;
```

If autovacuum is constantly behind, tune it per-table:

```sql
ALTER TABLE hot_table SET (
  autovacuum_vacuum_scale_factor = 0.01,
  autovacuum_analyze_scale_factor = 0.005
);
```

### Lock Contention

Common causes: long-running `ALTER TABLE` on busy tables, missing indexes causing full-table scans during updates, `LOCK TABLE` held too long.

Safe DDL pattern for adding columns:

```sql
-- This is fast and does not lock reads/writes (no default value with volatile expression)
ALTER TABLE users ADD COLUMN preferences jsonb;

-- Backfill in batches to avoid long locks
UPDATE users SET preferences = '{}' WHERE id BETWEEN 1 AND 10000;
UPDATE users SET preferences = '{}' WHERE id BETWEEN 10001 AND 20000;

-- Then add the default for future rows
ALTER TABLE users ALTER COLUMN preferences SET DEFAULT '{}';
```

Safe index creation on production tables:

```sql
-- CONCURRENTLY avoids locking writes (takes longer but does not block)
CREATE INDEX CONCURRENTLY idx_orders_created ON orders (created_at);
```
