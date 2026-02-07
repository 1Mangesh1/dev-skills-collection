# Index Selection Strategy

## Golden Rule: Index WHERE and JOIN Columns

### Priority Order

1. **WHERE clause columns** - Highest priority
   - Narrow down result set
   - Most queries have WHERE conditions

2. **JOIN condition columns** - High priority
   - Speed up table joins
   - Critical for multi-table queries

3. **ORDER BY columns** - Medium priority
   - Avoid sorting in memory
   - Only indexes can avoid disk sorts

4. **GROUP BY columns** - Medium priority
   - Speed up aggregations
   - Avoid 'Using temporary' in EXPLAIN

5. **SELECT columns** - Low priority
   - Only for "covering indexes"
   - Include in index to avoid table lookups

## Index Types by Use Case

| Type | Use Case | Example |
|------|----------|---------|
| Single Column | Simple equality filters | `CREATE INDEX idx_email ON users(email)` |
| Composite | Multiple WHERE conditions | `CREATE INDEX idx_name_email ON users(last_name, email)` |
| Full-Text | Text search | `CREATE FULLTEXT INDEX idx_text ON articles(content)` |
| Hash | Equality only, fast | `CREATE INDEX idx_id ON … USING HASH` |

## Column Order Matters!

```sql
-- Query: WHERE status='active' AND created_at > '2024-01-01'
-- Index order 1 (GOOD)
CREATE INDEX idx_status_date ON orders(status, created_at);

-- Index order 2 (BAD - status filter works, date doesn't use index)
CREATE INDEX idx_date_status ON orders(created_at, status);

-- Leftmost prefix rule: first column must be used
```

## When NOT to Index

- ❌ Low cardinality columns (gender, status with few values)
- ❌ Columns rarely used in WHERE/JOIN
- ❌ Very small tables (< 10,000 rows)
- ❌ Columns with many NULL values
- ❌ Frequently updated columns (write performance)
