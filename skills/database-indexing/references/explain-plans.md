# EXPLAIN Plans Deep Dive

## What is EXPLAIN?

EXPLAIN shows how database executes your query without actually running it.
EXPLAIN ANALYZE runs it and shows actual vs. estimated costs.

## EXPLAIN Output

```
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';

                            QUERY PLAN
─────────────────────────────────────────────────────────────────
 Seq Scan on users  (cost=0.00..35.50 rows=1 width=500)
   Filter: (email = 'test@example.com'::text)
   Actual rows=1, Actual time=0.024..0.025 ms
```

## Key Metrics

| Metric | Meaning |
|--------|---------|
| cost=0.00..35.50 | Estimated cost range |
| rows=1 | Estimated rows returned |
| Actual rows=1 | Actual rows returned |
| Actual time=0.024..0.025 | Time in milliseconds |

## Common Scan Types

### Seq Scan (Sequential Scan)
- Reads entire table
- Slowest for large tables
- Cost: High (0.00..1000.00+)
- Fix: Create index

### Index Scan
- Uses index to find rows
- Much faster with selective WHERE
- Cost: Lower (0.00..20.00)
- Good performance

### Index Only Scan
- Returns data from index alone
- Doesn't need to access main table  
- Cost: Very low (0.00..5.00)
- Best performance

## Reading Costs

Cost is arbitrary units approximating disk page reads.
- Cost 1000 = ~1000 page reads needed
- Lower is better

## How to Optimize

When you see slow Seq Scan:

```sql
-- Before: Seq Scan (slow)
SELECT * FROM users WHERE email = 'test@example.com';

-- After: Add index  
CREATE INDEX idx_email ON users(email);

-- Now: Index Scan (fast)
SELECT * FROM users WHERE email = 'test@example.com';
```

## Filtering vs Indexing

```
-- Can use index (good)
WHERE user_id = 5

-- Cannot use index effectively (needs index on email)
WHERE status = 'active' AND created_at > '2024-01-01'

-- Needs multi-column index
CREATE INDEX idx_status_date ON users(status, created_at)
```
