---
name: sqlite
description: SQLite database commands, queries, and embedded database patterns. Use when user mentions "sqlite", "sqlite3", "embedded database", "local database", "lightweight db", "sqlite schema", "sqlite backup", "mobile database", or working with .db/.sqlite files.
---

# SQLite

## sqlite3 CLI Basics

```bash
sqlite3 myapp.db                    # open or create a database
sqlite3 :memory:                    # in-memory database
sqlite3 myapp.db ".tables"          # one-shot command
sqlite3 myapp.db < schema.sql       # run SQL from file
```

Common dot-commands inside the shell:

```sql
.tables                 -- list all tables
.schema                 -- show CREATE statements for all tables
.schema users           -- show CREATE for specific table
.headers on             -- show column headers in output
.mode column            -- aligned columns (also: csv, json, table, line, tabs)
.width 20 30 10         -- set column widths for column mode
.databases              -- list attached databases
.indexes users          -- list indexes for a table
.quit                   -- exit
```

## Create Tables, Insert, Update, Delete

```sql
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,  -- alias for rowid, auto-increments
  name TEXT NOT NULL,
  email TEXT UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  total REAL NOT NULL,
  status TEXT DEFAULT 'pending',
  created_at TEXT DEFAULT (datetime('now'))
);

INSERT INTO users (name, email) VALUES ('Alice', 'alice@example.com');

INSERT INTO orders (user_id, total, status)
VALUES (1, 49.99, 'completed'), (1, 25.00, 'pending'), (2, 120.00, 'completed');

UPDATE users SET email = 'newalice@example.com' WHERE id = 1;

DELETE FROM orders WHERE status = 'pending' AND created_at < datetime('now', '-30 days');
```

RETURNING clause available in 3.35.0+. Check with `sqlite3 --version`.

## Queries

### Joins, Subqueries, GROUP BY

```sql
SELECT o.id, u.name, o.total
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.status = 'completed';

SELECT u.name, COALESCE(SUM(o.total), 0) AS lifetime_value
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.name;

SELECT * FROM users
WHERE id IN (
  SELECT user_id FROM orders GROUP BY user_id HAVING SUM(total) > 100
);

SELECT status, COUNT(*) AS cnt, ROUND(AVG(total), 2) AS avg_total
FROM orders GROUP BY status HAVING cnt > 1 ORDER BY avg_total DESC;
```

### CTEs and Window Functions

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', created_at) AS month, SUM(total) AS revenue
  FROM orders WHERE status = 'completed' GROUP BY 1
)
SELECT month, revenue,
       revenue - LAG(revenue) OVER (ORDER BY month) AS change
FROM monthly;

SELECT user_id, total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY total DESC) AS rn,
  SUM(total) OVER (PARTITION BY user_id) AS user_total
FROM orders;
```

## Output Modes

```bash
sqlite3 -header -csv myapp.db "SELECT * FROM users;" > users.csv
sqlite3 -json myapp.db "SELECT * FROM users;"
sqlite3 -header -column myapp.db "SELECT * FROM users;"
```

Inside the shell:

```sql
.mode csv               -- comma-separated
.mode json              -- JSON array of objects
.mode column            -- aligned columns
.mode table             -- ASCII table borders (3.36+)
.mode line              -- one value per line
.separator "\t"         -- custom separator for list mode
```

## Import and Export CSV

```bash
# Export
sqlite3 -header -csv myapp.db "SELECT * FROM users;" > users.csv

# Import into existing table
sqlite3 myapp.db <<'EOF'
.mode csv
.import users.csv users
EOF
```

For large imports, wrap in a transaction for speed:

```sql
BEGIN;
.mode csv
.import large_file.csv target_table
COMMIT;
```

## Indexes and EXPLAIN QUERY PLAN

```sql
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status_date ON orders(status, created_at);
CREATE UNIQUE INDEX idx_users_email ON users(email);

EXPLAIN QUERY PLAN SELECT * FROM orders WHERE user_id = 1;
```

Key things in the output:
- **SCAN TABLE** -- no usable index, reads every row
- **SEARCH TABLE ... USING INDEX** -- index is being used
- **USING COVERING INDEX** -- query answered entirely from index
- **USE TEMP B-TREE** -- sort or GROUP BY without index

## WAL Mode and Concurrency

```sql
PRAGMA journal_mode=WAL;   -- returns "wal" on success
PRAGMA busy_timeout=5000;  -- wait up to 5s instead of failing immediately
```

- One writer at a time, but readers are not blocked
- Creates `-wal` and `-shm` files alongside the database
- Force checkpoint: `PRAGMA wal_checkpoint(TRUNCATE);`
- Set once; persists across connections

## Backup

```sql
.backup main backup.db          -- online backup (safe during use)
.dump                           -- full SQL text dump
.dump users                     -- dump a single table
```

```bash
sqlite3 myapp.db .dump > full_dump.sql    # dump to file
sqlite3 restored.db < full_dump.sql       # restore from dump
```

VACUUM rebuilds the database file, reclaiming space:

```sql
VACUUM;                    -- rebuild in place
VACUUM INTO 'compact.db';  -- compacted copy (3.27+)
```

## JSON Support

Available in SQLite 3.38+ (built-in) or via the JSON1 extension:

```sql
CREATE TABLE events (id INTEGER PRIMARY KEY, data TEXT NOT NULL);

INSERT INTO events (data)
VALUES ('{"type":"click","page":"/home","tags":["mobile","v2"]}');

-- Extract values
SELECT json_extract(data, '$.type') AS event_type FROM events;
SELECT data->>'$.page' AS page FROM events;  -- ->> operator (3.38+)

-- Iterate over arrays
SELECT e.id, j.value AS tag
FROM events e, json_each(json_extract(e.data, '$.tags')) j;

-- Modify JSON
UPDATE events SET data = json_set(data, '$.processed', true) WHERE id = 1;

-- Build JSON in queries
SELECT json_object('id', id, 'name', name) FROM users;
SELECT json_group_array(json_object('id', id, 'name', name)) FROM users;
```

## Full-Text Search (FTS5)

```sql
CREATE VIRTUAL TABLE articles_fts USING fts5(title, body, content=articles, content_rowid=id);

-- Populate from existing table
INSERT INTO articles_fts(rowid, title, body) SELECT id, title, body FROM articles;

-- Search with boolean operators
SELECT *, rank FROM articles_fts WHERE articles_fts MATCH 'database AND performance' ORDER BY rank;

-- Highlight matches
SELECT highlight(articles_fts, 1, '<b>', '</b>') FROM articles_fts WHERE articles_fts MATCH 'sqlite';

-- Keep in sync with triggers
CREATE TRIGGER articles_ai AFTER INSERT ON articles BEGIN
  INSERT INTO articles_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
CREATE TRIGGER articles_ad AFTER DELETE ON articles BEGIN
  INSERT INTO articles_fts(articles_fts, rowid, title, body)
  VALUES ('delete', old.id, old.title, old.body);
END;
```

## Date and Time Functions

SQLite stores dates as TEXT, REAL, or INTEGER. Built-in functions handle ISO-8601 strings:

```sql
SELECT datetime('now');                              -- 2025-01-15 08:30:00
SELECT date('now', '-7 days');                       -- 7 days ago
SELECT strftime('%Y-%m', 'now');                     -- current year-month
SELECT strftime('%s', 'now');                        -- unix timestamp
SELECT datetime('2025-01-15', '+3 months', '-1 day'); -- date arithmetic
SELECT julianday('now') - julianday(created_at) AS days_old FROM users;
```

## Attach Multiple Databases

```sql
ATTACH DATABASE 'archive.db' AS archive;

SELECT * FROM main.users u JOIN archive.orders o ON o.user_id = u.id;

INSERT INTO archive.orders SELECT * FROM main.orders WHERE created_at < '2024-01-01';
DELETE FROM main.orders WHERE created_at < '2024-01-01';

DETACH DATABASE archive;
```

## Pragmas

```sql
-- Performance
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;       -- faster writes (safe with WAL)
PRAGMA cache_size=-64000;        -- 64MB page cache (negative = KB)
PRAGMA mmap_size=268435456;      -- memory-map up to 256MB
PRAGMA temp_store=MEMORY;        -- temp tables in memory

-- Integrity
PRAGMA foreign_keys=ON;          -- enforce foreign keys (off by default!)
PRAGMA integrity_check;          -- full database integrity scan

-- Info
PRAGMA table_info(users);        -- column details
PRAGMA index_list(users);        -- indexes on a table
PRAGMA compile_options;          -- build-time options (check for JSON, FTS5)
```

## Common Patterns

### Config Key-Value Store

```sql
CREATE TABLE config (
  key TEXT PRIMARY KEY, value TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);
INSERT OR REPLACE INTO config (key, value) VALUES ('theme', 'dark');
SELECT value FROM config WHERE key = 'theme';
```

### Local Cache with Expiry

```sql
CREATE TABLE cache (key TEXT PRIMARY KEY, value TEXT, expires_at TEXT);

INSERT OR REPLACE INTO cache (key, value, expires_at)
VALUES ('api:/users', '{"data":[...]}', datetime('now', '+1 hour'));

SELECT value FROM cache WHERE key = 'api:/users' AND expires_at > datetime('now');
DELETE FROM cache WHERE expires_at <= datetime('now');
```

### CLI Tool Storage

```sql
CREATE TABLE history (
  id INTEGER PRIMARY KEY, command TEXT NOT NULL,
  args TEXT, exit_code INTEGER,
  ran_at TEXT DEFAULT (datetime('now'))
);
SELECT command, args, ran_at FROM history ORDER BY ran_at DESC LIMIT 20;
SELECT command, COUNT(*) AS cnt FROM history GROUP BY command ORDER BY cnt DESC;
```

### Test Fixtures

```bash
sqlite3 test.db < schema.sql && sqlite3 test.db < seed.sql
# In-memory: Python sqlite3.connect(":memory:") / Node new Database(":memory:")
```

```sql
BEGIN;
INSERT INTO users (id, name, email) VALUES
  (1, 'Test User', 'test@example.com'),
  (2, 'Admin', 'admin@example.com');
INSERT INTO orders (user_id, total, status) VALUES
  (1, 99.99, 'completed'), (2, 50.00, 'pending');
COMMIT;
```
