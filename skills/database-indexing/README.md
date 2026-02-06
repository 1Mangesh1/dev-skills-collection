# Database Indexing Quick Start

Optimize database queries through strategic indexing and analysis.

## Quick Rules

1. **Index WHERE clause columns first**
2. **Consider JOIN conditions**
3. **Index columns in ORDER BY/GROUP BY**
4. **Column order matters** (leftmost prefix rule)
5. **Don't over-index** - costs writes

## How to Find Slow Queries

### PostgreSQL
```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### MySQL
```sql
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE email = 'test@example.com';
```

## Creating Indexes

### Single Column
```sql
CREATE INDEX idx_email ON users(email);
```

### Composite (Multi-column)
```sql
CREATE INDEX idx_user_status ON users(status, created_at);
```

### Full-Text Search
```sql
CREATE FULLTEXT INDEX idx_content ON articles(title, body);
```

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Query still slow | Bad WHERE clause | Analyze conditions |
| Index not used | Wrong column order | Review composite keys |
| Slow writes | Too many indexes | Remove unused ones |
| Out of memory | Large indexes | Archive/partition data |

## Performance Metrics

- Look at query time before/after indexing
- Monitor index usage with `pg_stat` or SHOW STATUS
- Analyze cardinality (uniqueness) of columns
- Keep indexes up-to-date with ANALYZE/VACUUM

## Tools

- EXPLAIN ANALYZE (PostgreSQL)
- Query Profiler (MySQL Workbench)
- Use the Index, Luke (free book)
- Database monitoring tools (Datadog, New Relic)

## Resources

- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [MySQL Performance](https://dev.mysql.com/doc/refman/8.0/en/optimization.html)
- [Use the Index, Luke!](https://use-the-index-luke.com/)

## See Also

- SKILL.md - Comprehensive indexing strategies
- metadata.json - Database documentation
