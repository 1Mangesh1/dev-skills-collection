# SQL Database Migrations

## Migration Files

Structure:
```
migrations/
├── 20240101120000_create_users_table.sql
├── 20240102150000_add_email_column.sql
└── 20240103100000_create_orders_table.sql
```

Naming: `YYYYMMDDHHMMSS_description.sql`

## Creating Migrations

```sql
-- Migration: Create users table
-- Created: 2024-01-20

BEGIN;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

COMMIT;
```

## Running Migrations

```bash
# Run all pending migrations
./migrate.sh apply

# Rollback last migration
./migrate.sh rollback

# Show status
./migrate.sh status
```

## Tracking Migrations

Create table to track applied migrations:

```sql
CREATE TABLE schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

When migration runs, record in this table:

```sql
INSERT INTO schema_migrations (version) VALUES ('20240120120000');
```

## Migration Best Practices

1. **One change per migration** - Easier to rollback
2. **Make reversible** - Include rollback
3. **Use transactions** - Atomic changes
4. **Test locally** - Before deploying
5. **Version control** - Commit migrations
6. **No data loss** - Plan carefully
7. **Idempotent** - Safe to run multiple times

## Complex Migration Example

```sql
-- Add column with default, then remove after
BEGIN;

-- Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);

-- Populate from existing columns
UPDATE users SET full_name = CONCAT(first_name, ' ', last_name);

-- Make it NOT NULL after population
ALTER TABLE users MODIFY full_name VARCHAR(255) NOT NULL;

-- Drop old columns later (separate migration)

COMMIT;
```

## Rollback Strategy

Via down migration:

```sql
-- Migration: 20240120_add_phone_to_users_down.sql
BEGIN;

ALTER TABLE users DROP COLUMN phone_number;

COMMIT;
```

Or revert approach:

```sql
-- Revert: 20240120_add_phone_to_users.sql
BEGIN;

ALTER TABLE users DROP COLUMN phone_number;

DELETE FROM schema_migrations WHERE version = '20240120120000';

COMMIT;
```
