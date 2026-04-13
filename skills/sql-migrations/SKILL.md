---
name: sql-migrations
description: Database migration mastery with Prisma, Drizzle, Knex, TypeORM, Alembic, Flyway, and golang-migrate. Use when user asks to "create a migration", "update database schema", "add a column", "remove a column", "rename a table", "set up Prisma", "rollback migration", "write SQL migration", "set up Drizzle", "zero-downtime migration", "backfill data", "squash migrations", "seed database", "migrate production", or any database schema change tasks.
---

# SQL Migrations

## Migration Fundamentals

A migration is a versioned, incremental change to a database schema. Migrations run in order and track which have been applied via a metadata table (e.g., `schema_migrations`, `_prisma_migrations`).

**Up/Down**: The up migration applies the change. The down migration reverses it. Not all changes are reversible (dropping a column with data destroys it).

**Versioned vs Repeatable**: Versioned migrations run once in order (001, 002, ...). Repeatable migrations (Flyway `R__` prefix) re-run whenever their checksum changes -- useful for views, functions, and stored procedures.

**Idempotent migrations**: Use `IF NOT EXISTS` / `IF EXISTS` guards so a migration can be re-run safely without erroring on already-applied state:

```sql
CREATE TABLE IF NOT EXISTS users (...);
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT;
DROP INDEX IF EXISTS idx_users_email;
```

## Tool-Specific Patterns

### Prisma

```bash
npm install prisma @prisma/client
npx prisma init
```

Commands:

```bash
npx prisma migrate dev --name add_users_table   # create + apply migration (dev)
npx prisma migrate deploy                       # apply pending migrations (production)
npx prisma migrate reset                        # drop + recreate + seed (destructive)
npx prisma migrate status                       # check migration status
npx prisma generate                             # regenerate client
npx prisma db push                              # push schema without migration file (prototyping)
npx prisma db seed                              # run seed script
npx prisma studio                               # open database GUI
```

### Drizzle

```bash
npm install drizzle-orm drizzle-kit
```

Commands:

```bash
npx drizzle-kit generate    # generate migration from schema diff
npx drizzle-kit migrate     # apply migrations
npx drizzle-kit push        # push schema directly (prototyping)
npx drizzle-kit studio      # open Drizzle Studio
npx drizzle-kit drop        # drop a migration
```

### Knex

```bash
npm install knex pg
npx knex init                              # create knexfile.js
npx knex migrate:make add_users_table      # create migration
npx knex migrate:latest                    # run pending
npx knex migrate:rollback                  # undo last batch
npx knex migrate:rollback --all            # undo everything
npx knex seed:make seed_users              # create seed file
npx knex seed:run                          # run seeds
```

### TypeORM

```bash
npx typeorm migration:create src/migrations/AddUsersTable
npx typeorm migration:generate -d src/data-source.ts src/migrations/AddUsersTable
npx typeorm migration:run -d src/data-source.ts
npx typeorm migration:revert -d src/data-source.ts
```

### Alembic (Python / SQLAlchemy)

```bash
alembic init alembic                       # initialize
alembic revision --autogenerate -m "add users table"
alembic upgrade head                       # apply all
alembic downgrade -1                       # undo last
alembic history                            # list migrations
alembic current                            # show current revision
```

### Flyway (Java / JVM)

```bash
flyway migrate                             # apply pending
flyway info                                # show status
flyway validate                            # verify applied match local
flyway repair                              # fix metadata table
flyway clean                               # drop all objects (destructive)
# Naming: V1__Create_users.sql, V2__Add_email_index.sql
# Repeatable: R__Create_views.sql (re-runs when checksum changes)
```

### golang-migrate

```bash
migrate create -ext sql -dir db/migrations -seq add_users_table
migrate -path db/migrations -database "$DB_URL" up
migrate -path db/migrations -database "$DB_URL" down 1
migrate -path db/migrations -database "$DB_URL" force 3   # fix dirty state
```

## Writing Safe Migrations (Zero-Downtime)

### Adding a Column

Never add a NOT NULL column without a default to a table that has existing rows. The safe sequence:

1. Add column as nullable: `ALTER TABLE users ADD COLUMN role TEXT;`
2. Deploy code that writes the new column.
3. Backfill existing rows: `UPDATE users SET role = 'user' WHERE role IS NULL;`
4. Add the constraint: `ALTER TABLE users ALTER COLUMN role SET NOT NULL;`

### Removing a Column

Never drop a column that code still reads. The safe sequence:

1. Stop reading the column in application code. Deploy.
2. Stop writing the column. Deploy.
3. Drop the column: `ALTER TABLE users DROP COLUMN legacy_field;`

### Renaming a Column or Table

Renaming breaks existing queries instantly. The safe sequence:

1. Add the new column. Deploy code that writes to both old and new.
2. Backfill new column from old column.
3. Switch reads to new column. Deploy.
4. Stop writing old column. Deploy.
5. Drop old column.

For tables, the same expand-migrate-contract pattern applies. Alternatively, create a view with the old name during transition.

### Index Creation

On Postgres, `CREATE INDEX` locks the table for writes. Use `CONCURRENTLY`:

```sql
-- Safe: does not block writes (Postgres only, cannot run inside a transaction)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Drop safely too
DROP INDEX CONCURRENTLY IF EXISTS idx_users_email;
```

In migration tools that wrap each file in a transaction, you must disable the transaction for that specific migration or run the index creation separately.

### Adding Constraints

```sql
-- Add foreign key without locking (Postgres)
ALTER TABLE posts ADD CONSTRAINT fk_posts_author
  FOREIGN KEY (author_id) REFERENCES users(id) NOT VALID;
ALTER TABLE posts VALIDATE CONSTRAINT fk_posts_author;

-- Add check constraint without locking (Postgres 12+)
ALTER TABLE users ADD CONSTRAINT chk_role
  CHECK (role IN ('admin', 'user', 'moderator')) NOT VALID;
ALTER TABLE users VALIDATE CONSTRAINT chk_role;
```

## Data Migrations vs Schema Migrations

Keep them separate. Schema migrations change structure (DDL). Data migrations change content (DML). Mixing them causes problems:

- Schema migrations should be fast and reversible. Data migrations on large tables are slow.
- Schema rollbacks cannot un-delete data.
- Data migrations may need batching; schema migrations do not.

```sql
-- Schema migration: 005_add_status_column.sql
ALTER TABLE orders ADD COLUMN status TEXT;

-- Data migration: 006_backfill_status.sql (separate file)
UPDATE orders SET status = 'completed' WHERE completed_at IS NOT NULL;
UPDATE orders SET status = 'pending' WHERE completed_at IS NULL;
```

## Large Table Migrations

For tables with millions of rows, a single `ALTER TABLE` or `UPDATE` can lock the table or run for hours.

**Batched updates**: Process rows in chunks to avoid long locks and transaction log bloat:

```sql
-- Backfill in batches of 10,000
DO $$
DECLARE batch_size INT := 10000;
BEGIN
  LOOP
    UPDATE orders SET status = 'pending'
    WHERE id IN (SELECT id FROM orders WHERE status IS NULL LIMIT batch_size);
    EXIT WHEN NOT FOUND;
    COMMIT;
  END LOOP;
END $$;
```

**Online schema change tools** (MySQL): `pt-online-schema-change` (Percona) and `gh-ost` (GitHub) create a shadow table, copy data, replay binlog changes, then swap. Use these for any DDL on large MySQL tables in production.

```bash
# pt-online-schema-change
pt-online-schema-change --alter "ADD COLUMN status VARCHAR(50)" \
  --execute D=mydb,t=orders

# gh-ost
gh-ost --alter "ADD COLUMN status VARCHAR(50)" \
  --database=mydb --table=orders --execute
```

## Squashing / Consolidating Migrations

When migration count grows unwieldy (100+ files), squash them:

1. Dump the current schema: `pg_dump --schema-only > baseline.sql`
2. Delete all existing migration files.
3. Create a single baseline migration from the dump.
4. Mark it as applied in the migrations table without running it.
5. All future migrations build from this baseline.

Prisma: `npx prisma migrate diff` can generate a diff between two states. Drizzle and Knex do not have built-in squash -- do it manually.

## Rollback Strategies and Limitations

**Always write down migrations** but understand their limits:

- Dropping a column is irreversible (data is gone). The down migration can recreate the column but not the data.
- Data migrations cannot be meaningfully reversed if the old value was overwritten.
- Rollbacks in production are risky. Prefer forward-fixing: deploy a new migration that undoes the change.

```sql
-- Down migration: 003_add_role.down.sql
ALTER TABLE users DROP COLUMN IF EXISTS role;
```

## Migration Locking and Concurrent Deploys

Most migration tools use advisory locks to prevent two processes from running migrations simultaneously. If your deployment runs multiple instances:

- Prisma and Flyway acquire locks automatically.
- Knex, golang-migrate: only one instance should run migrations (use a deploy step, not application startup).
- If a migration crashes mid-run and leaves a lock, you may need to manually clear the lock or use `migrate force` (golang-migrate) / `flyway repair`.

Run migrations in a dedicated CI/CD step, not at application boot.

## Testing Migrations

- Test against a production-like dataset, not an empty database. Schema changes that work on empty tables may lock or fail on tables with millions of rows.
- Run `up` then `down` then `up` again to verify reversibility.
- Use a copy of production data (anonymized) in staging.
- Check migration speed: if a migration takes > 1 second on staging, it will take longer in production. Plan accordingly.

## Seeding Data

Seeds populate the database with initial or test data. Keep seeds idempotent.

```sql
-- Idempotent seed
INSERT INTO roles (name) VALUES ('admin'), ('user'), ('moderator')
ON CONFLICT (name) DO NOTHING;
```

```typescript
// Prisma seed (prisma/seed.ts, configured in package.json "prisma.seed")
import { PrismaClient } from "@prisma/client";
const prisma = new PrismaClient();
async function main() {
  await prisma.role.upsert({
    where: { name: "admin" },
    update: {},
    create: { name: "admin" },
  });
}
main().finally(() => prisma.$disconnect());
```

## Environment-Specific Migrations

- **Dev**: Use `migrate reset` / `db push` freely. Speed matters more than safety.
- **Staging**: Mirror production. Run the exact same migration files. Test with realistic data volumes.
- **Production**: Never use `reset`, `push`, or `clean`. Only `migrate deploy` / `migrate up`. Always back up before migrating.

Use environment variables to control connection strings. Never hardcode credentials in migration files.

## Migration CI/CD Integration

```yaml
# GitHub Actions example
- name: Run migrations
  run: npx prisma migrate deploy
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}

# Validate migrations in PR checks
- name: Check migration status
  run: |
    npx prisma migrate status
    npx prisma migrate diff --from-migrations ./prisma/migrations --to-schema-datamodel ./prisma/schema.prisma --exit-code
```

CI pipeline checklist:

1. Run migrations against a test database before merging.
2. Verify no pending migrations exist after running.
3. Run the application test suite after migrations.
4. In production deploys, run migrations before deploying new application code (if the migration is backward-compatible) or after (if old code must stop using removed columns first).

## Raw SQL Migration Structure

```
migrations/
├── 001_create_users.up.sql
├── 001_create_users.down.sql
├── 002_create_posts.up.sql
├── 002_create_posts.down.sql
└── 003_add_email_index.up.sql
```

```sql
-- Example up migration
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Example down migration
DROP TABLE IF EXISTS users;
```

## Quick Reference

```
1. One change per migration -- easier to review, rollback, and debug
2. Always write down migrations for reversibility
3. Never edit an applied migration -- create a new one
4. Test migrations against production-like data
5. Wrap multi-statement migrations in transactions (except CONCURRENTLY)
6. Separate schema migrations from data migrations
7. Backfill data in a separate migration from the schema change
8. Run migrations in CI/CD, not at application boot
9. Back up the database before running production migrations
```
