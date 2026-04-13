---
name: prisma-orm
description: Prisma ORM for database access, schema design, migrations, and queries in TypeScript/JavaScript. Use when user mentions "prisma", "prisma schema", "prisma migrate", "prisma client", "prisma studio", "database ORM", "type-safe database", "prisma seed", or any Prisma-related task.
---

# Prisma ORM

## Setup

```bash
npx prisma init          # creates prisma/schema.prisma and .env
npm install @prisma/client
```

Configure `prisma/schema.prisma`:

```prisma
datasource db {
  provider = "postgresql" // "mysql", "sqlite", "sqlserver", "mongodb", "cockroachdb"
  url      = env("DATABASE_URL")
}
generator client {
  provider = "prisma-client-js"
}
```

Set `DATABASE_URL` in `.env`: `postgresql://user:password@localhost:5432/mydb?schema=public`

## Schema Language

```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  role      Role     @default(USER)
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  @@map("users")
  @@index([email, name])
}

enum Role {
  USER
  ADMIN
  MODERATOR
}
```

Key attributes: `@id` (primary key), `@unique`, `@default(value)`, `@map("col")` (column rename), `@updatedAt`, `@relation`, `@@id([a, b])` (composite PK), `@@unique([a, b])`.

## Relations

One-to-one:

```prisma
model User {
  id      Int      @id @default(autoincrement())
  profile Profile?
}
model Profile {
  id     Int  @id @default(autoincrement())
  user   User @relation(fields: [userId], references: [id])
  userId Int  @unique
}
```

One-to-many:

```prisma
model User {
  id    Int    @id @default(autoincrement())
  posts Post[]
}
model Post {
  id       Int  @id @default(autoincrement())
  author   User @relation(fields: [authorId], references: [id])
  authorId Int
}
```

Many-to-many (implicit -- Prisma manages the join table):

```prisma
model Post {
  id         Int        @id @default(autoincrement())
  categories Category[]
}
model Category {
  id    Int    @id @default(autoincrement())
  posts Post[]
}
```

Explicit many-to-many (custom join table with extra fields):

```prisma
model CategoriesOnPosts {
  post       Post     @relation(fields: [postId], references: [id])
  postId     Int
  category   Category @relation(fields: [categoryId], references: [id])
  categoryId Int
  assignedAt DateTime @default(now())
  @@id([postId, categoryId])
}
```

Self-relations:

```prisma
model Employee {
  id        Int        @id @default(autoincrement())
  manager   Employee?  @relation("Mgmt", fields: [managerId], references: [id])
  managerId Int?
  reports   Employee[] @relation("Mgmt")
}
```

## Migrations

```bash
npx prisma migrate dev --name add_user_table  # create + apply migration (dev)
npx prisma migrate deploy                     # apply pending migrations (prod)
npx prisma migrate reset                      # drop DB, re-apply all migrations
npx prisma migrate resolve --applied "20240101000000_name"  # mark as resolved
npx prisma generate                           # regenerate client without migrating
npx prisma db push                            # push schema without migration file (prototyping)
```

## Prisma Client Queries

```typescript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// Create
const user = await prisma.user.create({ data: { email: 'a@b.com', name: 'Alice' } });
await prisma.user.createMany({
  data: [{ email: 'a@b.com', name: 'Alice' }, { email: 'b@b.com', name: 'Bob' }],
  skipDuplicates: true,
});

// Read
await prisma.user.findUnique({ where: { id: 1 } });
await prisma.user.findUniqueOrThrow({ where: { id: 1 } });
await prisma.user.findFirst({ where: { name: 'Alice' } });
await prisma.user.findMany();

// Update
await prisma.user.update({ where: { id: 1 }, data: { name: 'Updated' } });

// Upsert
await prisma.user.upsert({
  where: { email: 'a@b.com' },
  update: { name: 'Updated' },
  create: { email: 'a@b.com', name: 'Alice' },
});

// Delete
await prisma.user.delete({ where: { id: 1 } });
await prisma.user.deleteMany({ where: { role: 'USER' } });
```

## Filtering

```typescript
const users = await prisma.user.findMany({
  where: {
    email: { contains: 'example.com' },
    name: { startsWith: 'A' },
    role: { in: ['ADMIN', 'MODERATOR'] },
    id: { not: 5 },
    AND: [{ createdAt: { gte: new Date('2024-01-01') } }, { createdAt: { lte: new Date('2024-12-31') } }],
    OR: [{ name: { contains: 'alice' } }, { email: { contains: 'alice' } }],
    posts: { some: { published: true } }, // relation filters: some, none, every
  },
  orderBy: { createdAt: 'desc' },
});
```

## Relations in Queries

```typescript
// include: fetch full related objects
await prisma.user.findUnique({ where: { id: 1 }, include: { posts: true, profile: true } });

// select: pick specific fields
await prisma.user.findUnique({
  where: { id: 1 },
  select: { name: true, posts: { select: { title: true } } },
});

// Nested writes: create parent + children in one call
await prisma.user.create({
  data: {
    email: 'a@b.com',
    posts: { create: [{ title: 'Post 1' }, { title: 'Post 2' }] },
    profile: { create: { bio: 'Hello' } },
  },
  include: { posts: true, profile: true },
});

// Connect existing records
await prisma.post.update({
  where: { id: 1 },
  data: { categories: { connect: [{ id: 1 }, { id: 2 }] } },
});
```

## Aggregations

```typescript
await prisma.user.count({ where: { role: 'ADMIN' } });

await prisma.product.aggregate({
  _sum: { price: true }, _avg: { price: true },
  _min: { price: true }, _max: { price: true }, _count: true,
});

await prisma.user.groupBy({
  by: ['role'],
  _count: { id: true },
  _avg: { age: true },
  having: { age: { _avg: { gt: 25 } } },
});
```

## Raw Queries

```typescript
const users = await prisma.$queryRaw`SELECT * FROM users WHERE email = ${email}`;
await prisma.$executeRaw`UPDATE users SET name = ${name} WHERE id = ${id}`;
```

Tagged template literals are parameterized automatically. Never use string concatenation.

## Seeding

Add to `package.json`: `{ "prisma": { "seed": "ts-node prisma/seed.ts" } }`

```typescript
// prisma/seed.ts
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
async function main() {
  await prisma.user.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: { email: 'admin@example.com', name: 'Admin', role: 'ADMIN' },
  });
}
main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => prisma.$disconnect());
```

```bash
npx prisma db seed   # also runs automatically after prisma migrate reset
```

## Prisma Studio

```bash
npx prisma studio    # opens visual data editor at http://localhost:5555
```

## Multiple Databases

Use separate schema files with custom client output paths:

```prisma
// prisma/schema-analytics.prisma
datasource db {
  provider = "postgresql"
  url      = env("ANALYTICS_DATABASE_URL")
}
generator client {
  provider = "prisma-client-js"
  output   = "../generated/analytics-client"
}
```

```bash
npx prisma generate --schema=prisma/schema-analytics.prisma
```

```typescript
import { PrismaClient as AnalyticsClient } from '../generated/analytics-client';
const analytics = new AnalyticsClient();
```

## Common Patterns

### Pagination

```typescript
// Offset-based
await prisma.user.findMany({
  skip: (page - 1) * pageSize, take: pageSize, orderBy: { createdAt: 'desc' },
});
// Cursor-based (better for large datasets)
await prisma.user.findMany({
  take: 20, skip: 1, cursor: { id: lastSeenId }, orderBy: { id: 'asc' },
});
```

### Soft Deletes

Add `deletedAt DateTime?` to the model. Filter with `where: { deletedAt: null }`. Use Prisma client extensions to apply the filter globally.

### Timestamps

Use `createdAt DateTime @default(now())` and `updatedAt DateTime @updatedAt` on models.

### Transactions

```typescript
// Batch (all-or-nothing, no inter-query dependencies)
const [user, post] = await prisma.$transaction([
  prisma.user.create({ data: { email: 'a@b.com' } }),
  prisma.post.create({ data: { title: 'Hello', authorId: 1 } }),
]);

// Interactive (access results of previous queries)
await prisma.$transaction(async (tx) => {
  const user = await tx.user.findUniqueOrThrow({ where: { id: 1 } });
  await tx.account.update({
    where: { userId: user.id },
    data: { balance: { decrement: 100 } },
  });
});
```

## Performance

### Singleton Client

Prevent multiple instances during hot reload:

```typescript
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };
export const prisma = globalForPrisma.prisma || new PrismaClient();
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

### Connection Pooling

Set pool size in the URL: `?connection_limit=10&pool_timeout=30`. For serverless, use Prisma Accelerate or an external pooler like PgBouncer.

### N+1 Prevention

```typescript
// Bad: N+1
const users = await prisma.user.findMany();
for (const u of users) { await prisma.post.findMany({ where: { authorId: u.id } }); }

// Good: single query
const users = await prisma.user.findMany({ include: { posts: true } });
```

Use `findMany` with `where: { id: { in: ids } }` instead of multiple `findUnique` calls.

### Query Logging and Indexes

```typescript
const prisma = new PrismaClient({ log: ['query', 'info', 'warn', 'error'] });
```

Add `@@index` for columns used in `where`, `orderBy`, and join conditions:

```prisma
model Post {
  id       Int    @id @default(autoincrement())
  authorId Int
  status   String
  @@index([authorId])
  @@index([status, authorId])
}
```
