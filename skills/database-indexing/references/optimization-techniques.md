# Query Optimization Techniques

## EXPLAIN Plans

### PostgreSQL
```sql
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM users WHERE email = 'test@example.com';

Result:
- Seq Scan vs Index Scan (shows if index was used)
- Rows=1 (estimated vs actual)
- Planning time, Execution time
```

### MySQL
```sql
EXPLAIN FORMAT=JSON
SELECT * FROM users WHERE email = 'test@example.com';

Shows:
- table: which table
- type: access method (ref, range, index, seq scan)
- key: which index used
- rows: estimated rows examined
```

## Common Optimization Patterns

### 1. Add Missing Index
```sql
-- Slow without index
SELECT * FROM orders WHERE customer_id = 123;

-- Solution
CREATE INDEX idx_customer ON orders(customer_id);
```

### 2. Fix Join Order
```sql
-- Wrong: Join big table first
SELECT * FROM big_table 
JOIN small_filtered_table ON ...

-- Better: Filter small table first
SELECT * FROM small_filtered_table
JOIN big_table ON ...
```

### 3. Avoid SELECT *
```sql
-- Slower - reads all columns
SELECT * FROM users WHERE id = 1;

-- Faster - only needed columns
SELECT id, name, email FROM users WHERE id = 1;
```

### 4. Use Covering Index
```sql
CREATE INDEX idx_user_name_email ON users(id, name, email);
-- Now query doesn't need to look up main table
SELECT name, email FROM users WHERE id = 1;
```
