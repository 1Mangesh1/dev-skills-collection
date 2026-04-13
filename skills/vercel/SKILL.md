---
name: vercel
description: Vercel deployment, serverless functions, and edge configuration. Use when user mentions "vercel", "vercel deploy", "vercel CLI", "serverless functions", "edge functions", "vercel.json", "preview deployments", "vercel domains", "vercel env", "vercel cron", "vercel KV", "vercel postgres", "vercel blob", "ISR", or deploying web applications to Vercel.
---

# Vercel

## CLI Essentials

```bash
npm i -g vercel                        # install CLI
vercel login                           # authenticate (browser flow)
vercel link                            # link current directory to a Vercel project
vercel                                 # deploy to preview
vercel --prod                          # deploy to production
vercel dev                             # run local dev server (mirrors Vercel environment)
vercel dev --listen 4000               # custom port

# Environment variables
vercel env ls                          # list all env vars
vercel env add SECRET_KEY              # add interactively (prompts for value and scope)
vercel env add DATABASE_URL production < .env.production  # pipe value for specific scope
vercel env pull .env.local             # pull remote env vars to local file
vercel env rm SECRET_KEY production    # remove from specific environment

# Domains
vercel domains ls                      # list domains
vercel domains add example.com         # add domain
vercel domains inspect example.com     # DNS and certificate status

# Logs and inspection
vercel logs https://my-deploy-url.vercel.app   # stream deployment logs
vercel inspect <deployment-url>                # deployment details (functions, routes, size)
vercel ls                                      # list recent deployments
vercel rollback <deployment-url>               # revert production to a previous deployment
```

## Project Configuration (vercel.json)

```jsonc
{
  // Rewrites (URL stays the same, content served from destination)
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" },
    { "source": "/(.*)", "destination": "/index.html" }   // SPA fallback
  ],

  // Redirects
  "redirects": [
    { "source": "/old-page", "destination": "/new-page", "permanent": true },
    { "source": "/blog/:slug", "destination": "https://blog.example.com/:slug", "statusCode": 308 }
  ],

  // Custom headers
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Cache-Control", "value": "s-maxage=86400" }
      ]
    }
  ],

  // Function configuration
  "functions": {
    "api/heavy-task.ts": {
      "memory": 1024,                  // MB (128–3008)
      "maxDuration": 60                // seconds (Hobby: 60, Pro: 300, Enterprise: 900)
    },
    "api/edge-fn.ts": {
      "runtime": "edge"
    }
  },

  // Cron jobs
  "crons": [
    {
      "path": "/api/cron/daily-cleanup",
      "schedule": "0 0 * * *"          // standard cron syntax (UTC)
    },
    {
      "path": "/api/cron/hourly-sync",
      "schedule": "0 * * * *"
    }
  ],

  // Build and output
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm ci",
  "framework": "nextjs",               // auto-detected; override if needed
  "regions": ["iad1", "sfo1"],         // deploy functions to specific regions

  // Clean URLs: /about instead of /about.html
  "cleanUrls": true,
  "trailingSlash": false
}
```

## Framework Detection and Build Settings

Vercel auto-detects frameworks: Next.js, Nuxt, SvelteKit, Remix, Astro, Vite, CRA, Gatsby, Angular, Hugo, etc. Override in project settings or vercel.json when auto-detection fails.

```jsonc
// Override build settings in vercel.json
{
  "framework": "vite",
  "buildCommand": "vite build",
  "outputDirectory": "dist",
  "installCommand": "pnpm install",
  "devCommand": "vite dev --port $PORT"
}
```

Node.js version: set in `package.json` engines field or project settings. Supports 18.x (default) and 20.x.

## Environment Variables

Three scopes: **Development**, **Preview**, **Production**.

- Production: available only on production deployments
- Preview: available on preview deployments (each PR gets one)
- Development: available when running `vercel dev`

System env vars are auto-injected: `VERCEL_ENV`, `VERCEL_URL`, `VERCEL_BRANCH_URL`, `VERCEL_GIT_COMMIT_SHA`, `VERCEL_GIT_COMMIT_REF`.

Sensitive values: mark as "Sensitive" in dashboard (encrypted, never shown in logs). For local dev, use `vercel env pull` to sync to `.env.local`.

## Serverless Functions

Place files in the `/api` directory. Each file becomes an endpoint matching its path.

```typescript
// api/hello.ts → /api/hello
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default function handler(req: VercelRequest, res: VercelResponse) {
  const { name = 'World' } = req.query;
  res.status(200).json({ message: `Hello ${name}!` });
}
```

### Streaming Responses

```typescript
// api/stream.ts
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default async function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  for (let i = 0; i < 5; i++) {
    res.write(`data: chunk ${i}\n\n`);
    await new Promise((r) => setTimeout(r, 500));
  }
  res.end();
}
```

### Runtime Options

```typescript
// Set max duration and memory per-function
export const config = {
  maxDuration: 30,          // seconds
  memory: 512,              // MB
};
```

Supported runtimes: Node.js (default), Go, Python, Ruby. Install `@vercel/python`, `@vercel/go`, etc. for non-Node runtimes.

## Edge Functions

Run on Vercel's edge network (no cold starts, ~0ms startup, limited API surface).

```typescript
// api/geo.ts
export const config = { runtime: 'edge' };

export default function handler(request: Request) {
  const country = request.headers.get('x-vercel-ip-country') || 'unknown';
  const city = request.headers.get('x-vercel-ip-city') || 'unknown';
  const latitude = request.headers.get('x-vercel-ip-latitude');
  const longitude = request.headers.get('x-vercel-ip-longitude');

  return Response.json({ country, city, latitude, longitude });
}
```

### Middleware (Next.js)

```typescript
// middleware.ts (project root)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const country = request.geo?.country || 'US';
  // Redirect non-US traffic
  if (country !== 'US' && request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL(`/${country.toLowerCase()}`, request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|favicon.ico).*)'],
};
```

## Deployment Workflow

```bash
# Git-based (recommended): push to GitHub/GitLab/Bitbucket
git push origin feature-branch         # → creates preview deployment automatically
# Merging to main/production branch    # → creates production deployment

# CLI-based
vercel                                 # preview deployment
vercel --prod                          # production deployment
vercel promote <deployment-url>        # promote any deployment to production

# Instant rollback
vercel rollback                        # rollback production to previous deployment
```

Preview deployments get unique URLs: `project-git-branch-team.vercel.app`. Each PR comment shows the preview URL.

## Custom Domains

```bash
vercel domains add myapp.com
vercel domains add www.myapp.com
vercel domains add "*.myapp.com"       # wildcard subdomain (Pro plan+)
```

DNS configuration:
- **Apex domain** (myapp.com): A record → `76.76.21.21`
- **Subdomain** (www.myapp.com): CNAME → `cname.vercel-dns.com`
- **Nameservers** (full control): point NS records to Vercel's nameservers

SSL certificates are auto-provisioned and renewed via Let's Encrypt.

## Storage

### Vercel KV (Redis-compatible)

```typescript
import { kv } from '@vercel/kv';

// Set/Get
await kv.set('user:123', { name: 'Alice', plan: 'pro' });
const user = await kv.get('user:123');

// With expiry
await kv.set('session:abc', data, { ex: 3600 });   // expires in 1 hour

// Hash operations
await kv.hset('config', { theme: 'dark', lang: 'en' });
const theme = await kv.hget('config', 'theme');

// Lists
await kv.lpush('queue', 'task1');
const task = await kv.rpop('queue');
```

### Vercel Postgres

```typescript
import { sql } from '@vercel/postgres';

// Query
const { rows } = await sql`SELECT * FROM users WHERE id = ${userId}`;

// Insert
await sql`INSERT INTO users (name, email) VALUES (${name}, ${email})`;

// With connection pooling (for serverless)
import { db } from '@vercel/postgres';
const client = await db.connect();
try {
  await client.sql`BEGIN`;
  await client.sql`UPDATE accounts SET balance = balance - ${amount} WHERE id = ${fromId}`;
  await client.sql`UPDATE accounts SET balance = balance + ${amount} WHERE id = ${toId}`;
  await client.sql`COMMIT`;
} catch (e) {
  await client.sql`ROLLBACK`;
  throw e;
} finally {
  client.release();
}
```

### Vercel Blob

```typescript
import { put, del, list, head } from '@vercel/blob';

// Upload
const blob = await put('avatars/user-123.png', file, { access: 'public' });
console.log(blob.url);   // https://abc123.public.blob.vercel-storage.com/avatars/user-123.png

// Upload from server action (Next.js)
const blob = await put(filename, body, {
  access: 'public',
  contentType: 'image/png',
  addRandomSuffix: true,
});

// List, head, delete
const { blobs } = await list({ prefix: 'avatars/' });
const metadata = await head(blob.url);
await del(blob.url);
```

## Edge Config (Feature Flags)

Ultra-low latency key-value store read at the edge (~0ms reads).

```typescript
import { get, getAll, has } from '@vercel/edge-config';

// Read values (typically feature flags)
const isEnabled = await get<boolean>('new-dashboard');
const allFlags = await getAll();
const exists = await has('maintenance-mode');

// In middleware for feature gating
import { NextResponse } from 'next/server';
import { get } from '@vercel/edge-config';

export async function middleware() {
  const maintenance = await get<boolean>('maintenance-mode');
  if (maintenance) {
    return NextResponse.rewrite(new URL('/maintenance', request.url));
  }
  return NextResponse.next();
}
```

Update Edge Config via API or dashboard. Changes propagate globally in ~seconds.

## ISR (Incremental Static Regeneration)

### Time-based ISR (Next.js App Router)

```typescript
// app/products/page.tsx
export const revalidate = 60;   // revalidate every 60 seconds

export default async function Products() {
  const products = await fetch('https://api.example.com/products').then(r => r.json());
  return <ProductList products={products} />;
}
```

### On-demand Revalidation

```typescript
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from 'next/cache';
import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  const secret = request.headers.get('x-revalidation-secret');
  if (secret !== process.env.REVALIDATION_SECRET) {
    return Response.json({ error: 'Invalid secret' }, { status: 401 });
  }

  const { path, tag } = await request.json();
  if (tag) revalidateTag(tag);
  else if (path) revalidatePath(path);

  return Response.json({ revalidated: true, now: Date.now() });
}
```

```bash
# Trigger revalidation
curl -X POST https://myapp.com/api/revalidate \
  -H "x-revalidation-secret: $SECRET" \
  -H "Content-Type: application/json" \
  -d '{"path": "/products"}'
```

## Monorepo Support

```jsonc
// vercel.json at repo root
{
  "projects": [
    { "name": "web", "rootDirectory": "apps/web" },
    { "name": "docs", "rootDirectory": "apps/docs" }
  ]
}
```

In project settings (dashboard or CLI):
- **Root Directory**: `apps/web` — Vercel only builds this subdirectory
- **Include/Ignore Build Step**: skip builds when no relevant files changed

```bash
# Ignore build step — custom script in project settings
# Only rebuild if files in this project or shared packages changed
git diff --quiet HEAD^ HEAD -- apps/web/ packages/shared/ || exit 0
```

Works with Turborepo, Nx, pnpm workspaces. Vercel auto-detects Turborepo and uses `turbo run build --filter=<project>`.

## Speed Insights and Web Analytics

```bash
npm i @vercel/speed-insights @vercel/analytics
```

```tsx
// app/layout.tsx (Next.js)
import { SpeedInsights } from '@vercel/speed-insights/next';
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <SpeedInsights />
        <Analytics />
      </body>
    </html>
  );
}
```

Speed Insights tracks Core Web Vitals (LCP, FID, CLS, TTFB, INP) with real user data. Analytics provides pageviews, unique visitors, and referrers — no cookies, GDPR-compliant.

## Deployment Protection

```jsonc
// vercel.json
{
  "passwordProtection": {
    "deploymentType": "preview"        // "all" | "preview"
  }
}
```

Options:
- **Vercel Authentication**: only team members can view (enabled by default for preview deployments)
- **Password Protection** (Pro+): set a shared password for preview or all deployments
- **Trusted IPs** (Enterprise): restrict access by IP range
- **Deployment Protection Bypass**: generate bypass URLs for CI/testing with `x-vercel-protection-bypass` header

## Troubleshooting

### Build Failures

```bash
vercel logs <deployment-url>           # check build logs
vercel inspect <deployment-url>        # check build output and routes
```

Common causes:
- Missing env vars in build scope (add to "Preview" and "Production")
- Node.js version mismatch (set in package.json engines or project settings)
- Out of memory: increase function memory or optimize build (`NODE_OPTIONS=--max-old-space-size=4096`)
- Missing dependencies: ensure `devDependencies` aren't pruned if needed at build time

### Function Timeouts

- Hobby: 60s max, Pro: 300s, Enterprise: 900s
- Use streaming for long-running responses
- Offload to background jobs (use Vercel Cron or external queue)
- Set `maxDuration` in function config to extend timeout

### Cold Starts

- Serverless functions: 250ms–1s cold start typical
- Reduce cold starts: keep bundles small, minimize imports, use dynamic imports
- Edge functions: no cold starts (~0ms startup)
- Use `@vercel/functions` warm-up pattern for critical paths

## Cost Optimization

- **Function duration**: minimize execution time; use edge functions where possible (cheaper, no cold start)
- **Bandwidth**: enable compression, optimize images with `next/image`, set cache headers (`s-maxage`, `stale-while-revalidate`)
- **Edge caching**: use `Cache-Control: s-maxage=31536000` on static assets; ISR reduces function invocations
- **Function invocations**: batch operations, use SWR/React Query to reduce API calls
- **Image optimization**: set `images.minimumCacheTTL` in `next.config.js` to reduce re-optimizations
- **Serverless regions**: deploy functions to a single region near your database to reduce latency and cost
- **Bundle size**: tree-shake, lazy-load routes, use `@vercel/nft` to trace dependencies accurately
