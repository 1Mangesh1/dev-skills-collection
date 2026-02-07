# Index Design Patterns

## Choose Right Data Type

```sql
-- Bad: VARCHAR for IDs
CREATE TABLE users (id VARCHAR(50) PRIMARY KEY);

-- Good: INT or UUID for IDs
CREATE TABLE users (id INT PRIMARY KEY, id UUID PRIMARY KEY);
-- Impact: 8 bytes vs 50 bytes = 6x space savings
```

## Column Order Matters

For composite indexes, column order affects performance:

```sql
-- If you query both these conditions often:
-- 1. WHERE status = 'active' AND created_at > date
-- 2. WHERE created_at > date AND status = 'active'

-- Use leftmost prefix rule
CREATE INDEX idx_status_date ON users(status, created_at);
-- ✓ WHERE status = 'active' AND created_at > date   (uses full index)
-- ✓ WHERE status = 'active'                         (uses partial index)
-- ✗ WHERE created_at > date                         (doesn't use index)

-- Better if you query only the second pattern:
CREATE INDEX idx_date_status ON users(created_at, status);
```

## Covering Indexes

Include all needed columns so database doesn't fetch from main table:

```sql
-- Bad: Index doesn't cover query
SELECT email, name FROM users WHERE id = 123;
-- Must read index, then fetch from table

-- Good: Covering index includes email and name
CREATE INDEX idx_id_cover ON users(id) INCLUDE (email, name);
-- Reads index only, doesn't fetch table
```

## Partial Indexes

Only index rows that matter:

```sql
-- Bad: Index all rows including inactive
CREATE INDEX idx_users_email ON users(email);

-- Good: Only active users
CREATE INDEX idx_active_email ON users(email) WHERE status = 'active';
-- Much smaller index, faster searches
```

## Expression Indexes

Index computed values:

```sql
-- Bad: WHERE LOWER(email) = 'test@example.com' (full table scan)
-- Good: Create expression index
CREATE INDEX idx_email_lower ON users(LOWER(email));
```

## Index Maintenance

```sql
-- Check for unused indexes
SELECT schemaname, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan < 50  -- rarely used
ORDER BY idx_scan ASC;

-- Drop unused
DROP INDEX idx_rarely_used;

-- Rebuild fragmented index
REINDEX INDEX idx_my_index;
```
