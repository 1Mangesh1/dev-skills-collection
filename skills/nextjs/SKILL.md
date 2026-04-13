---
name: nextjs
description: Next.js patterns for routing, data fetching, server components, and deployment. Use when user mentions "next.js", "nextjs", "app router", "pages router", "server components", "server actions", "next/image", "next/link", "getServerSideProps", "getStaticProps", "middleware", or building React applications with Next.js.
---

# Next.js Development Patterns

## App Router vs Pages Router

The App Router (Next.js 13.4+) is recommended for new projects. The Pages Router remains supported.

**Use App Router when:** starting a new project, you need Server Components/streaming/Server Actions, nested layouts, or parallel routes.
**Use Pages Router when:** maintaining an existing codebase, or depending on libraries without App Router support.

Both routers can coexist. Files in `app/` use App Router; files in `pages/` use Pages Router. Do not define the same route in both.

## File-Based Routing (App Router)

```
app/
  layout.tsx        # Root layout (required, wraps all pages, must have <html> and <body>)
  page.tsx          # Home route (/)
  loading.tsx       # Suspense fallback (shown while page streams)
  error.tsx         # Error boundary (must be a Client Component)
  not-found.tsx     # 404 UI (triggered by notFound())
  global-error.tsx  # Error boundary for the root layout
  template.tsx      # Like layout but re-mounts on navigation
  dashboard/
    layout.tsx      # Nested layout for /dashboard/*
    page.tsx        # /dashboard
```

- `layout.tsx` persists across navigations. `page.tsx` makes a route publicly accessible.
- `loading.tsx` auto-wraps the page in `<Suspense>`.
- `error.tsx` requires `"use client"` and receives `error` and `reset` props.

## Server Components vs Client Components

All components are Server Components by default in the App Router.

**Server Components** run only on the server, can access databases/secrets directly, cannot use hooks or event handlers, and reduce client bundle size.

**Client Components** require `"use client"` as the first line. Needed for interactivity, hooks, browser APIs. They still SSR on initial load, then hydrate.

```tsx
"use client";
import { useState } from "react";
export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

**Composition pattern:** Keep Server Components as outer wrappers, pass Client Components as children. Only add `"use client"` when genuinely needed.

## Data Fetching

### App Router (Server Components)

```tsx
// Cached indefinitely (like getStaticProps)
const res = await fetch("https://api.example.com/data");
// Revalidate every 60s (ISR)
const res = await fetch(url, { next: { revalidate: 60 } });
// No caching (like getServerSideProps)
const res = await fetch(url, { cache: "no-store" });
```

Segment-level config for non-fetch sources:
```tsx
export const revalidate = 60;
export const dynamic = "force-dynamic";
```

### Pages Router

- `getStaticProps` -- build time (or ISR revalidation).
- `getServerSideProps` -- every request.
- `getStaticPaths` -- defines dynamic paths for static generation.

## Server Actions

Server-side functions callable from forms and Client Components.

```tsx
// app/actions.ts
"use server";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  await db.post.create({ data: { title } });
  revalidatePath("/posts");
  redirect("/posts");
}
```

```tsx
// app/posts/new/page.tsx
import { createPost } from "@/app/actions";
export default function NewPost() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <button type="submit">Create</button>
    </form>
  );
}
```

Can also be called with `startTransition` in Client Components. Always validate input server-side.

## Dynamic Routes

```
app/blog/[slug]/page.tsx          -- /blog/hello-world
app/docs/[...catchAll]/page.tsx   -- /docs/a, /docs/a/b/c
app/shop/[[...optional]]/page.tsx -- /shop, /shop/a, /shop/a/b
```

```tsx
export default async function BlogPost({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  return <article>{post.content}</article>;
}

export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```

## Route Groups and Parallel Routes

**Route groups** use parentheses to organize without affecting URLs:
```
app/(marketing)/about/page.tsx  --> /about
app/(shop)/cart/page.tsx        --> /cart
```
Each group can have its own `layout.tsx`.

**Parallel routes** use `@`-prefixed slots rendered simultaneously in a layout:
```
app/layout.tsx     # Props: children, analytics, team
app/@analytics/page.tsx
app/@team/page.tsx
```

```tsx
export default function Layout({ children, analytics, team }: {
  children: React.ReactNode; analytics: React.ReactNode; team: React.ReactNode;
}) {
  return <div>{children}{analytics}{team}</div>;
}
```

## Middleware

Define `middleware.ts` at the project root (or `src/`). Runs before requests complete, on the Edge Runtime.

```tsx
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("session")?.value;
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  const country = request.geo?.country;
  if (country === "DE") {
    return NextResponse.rewrite(new URL("/de" + request.nextUrl.pathname, request.url));
  }
  const response = NextResponse.next();
  response.headers.set("x-request-id", crypto.randomUUID());
  return response;
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

Keep middleware lightweight. Avoid heavy computation or large dependencies.

## API Routes

### App Router (Route Handlers)

```tsx
// app/api/posts/route.ts
import { NextResponse } from "next/server";

export async function GET() {
  const posts = await db.post.findMany();
  return NextResponse.json(posts);
}

export async function POST(request: Request) {
  const body = await request.json();
  const post = await db.post.create({ data: body });
  return NextResponse.json(post, { status: 201 });
}
```

Supports GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS. GET-only route files are cached by default.

### Pages Router

```tsx
// pages/api/posts.ts
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "POST") { /* handle */ }
  res.status(200).json({ posts: [] });
}
```

## Image Optimization

```tsx
import Image from "next/image";
import heroImage from "@/public/hero.jpg";

<Image src={heroImage} alt="Hero" priority />
<Image src="https://cdn.example.com/photo.jpg" alt="Photo"
  width={800} height={600} sizes="(max-width: 768px) 100vw, 800px" />
```

- `priority` on above-the-fold images (disables lazy loading).
- `sizes` helps the browser pick the correct srcset image.
- Configure `remotePatterns` in `next.config.js` for external domains.
- `fill` prop with a positioned parent for responsive container-filling images.

## Metadata and SEO

```tsx
// Static
export const metadata = {
  title: "My App",
  description: "A description",
  openGraph: { title: "My App", images: ["/og.png"] },
};

// Dynamic
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  return { title: post.title, description: post.summary };
}
```

Sitemap and robots:
```tsx
// app/sitemap.ts
export default async function sitemap() {
  const posts = await getAllPosts();
  return [
    { url: "https://example.com", lastModified: new Date() },
    ...posts.map((p) => ({ url: `https://example.com/blog/${p.slug}`, lastModified: p.updatedAt })),
  ];
}

// app/robots.ts
export default function robots() {
  return {
    rules: { userAgent: "*", allow: "/", disallow: "/private/" },
    sitemap: "https://example.com/sitemap.xml",
  };
}
```

## Environment Variables

- `NEXT_PUBLIC_` prefix: inlined into the client bundle at build time, visible to the browser.
- All other variables: server-only (Server Components, Route Handlers, Middleware).
- Use `.env.local` for local overrides. Commit `.env.example` with placeholders.
- Consider `@t3-oss/env-nextjs` or `zod` for startup validation.

```
DATABASE_URL=postgres://localhost:5432/mydb        # server only
NEXT_PUBLIC_API_URL=https://api.example.com         # available in browser
```

## Caching

Four layers:

1. **Request Memoization** -- Duplicate `fetch` calls with same URL/options are deduplicated within a single render.
2. **Data Cache** -- `fetch` responses persisted. Invalidate with `revalidatePath`, `revalidateTag`, or time-based revalidation.
3. **Full Route Cache** -- Static routes cached as HTML + RSC payload at build time. Invalidated when Data Cache invalidates.
4. **Router Cache** -- RSC payloads cached in the browser per session. Configurable staleness.

**Invalidation:**
```tsx
import { revalidatePath, revalidateTag } from "next/cache";

const res = await fetch(url, { next: { tags: ["posts"] } });
revalidateTag("posts");     // tag-based
revalidatePath("/blog");    // path-based
export const dynamic = "force-dynamic"; // opt out entirely
```

Tune Router Cache in `next.config.js`:
```js
module.exports = { experimental: { staleTimes: { dynamic: 0, static: 180 } } };
```

## Deployment

**Vercel:** Push to a connected Git repo. Zero config. Supports Edge Functions, ISR, image optimization.

**Self-hosted:**
```bash
next build && next start -p 3000
```

**Docker:**
```dockerfile
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
FROM base AS build
RUN npm ci
COPY . .
RUN npm run build
FROM base AS runner
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

Requires `output: "standalone"` in `next.config.js`.

**Static export:** Set `output: "export"` in `next.config.js`. Outputs static HTML/CSS/JS to `out/`. No ISR, middleware, non-GET route handlers, or image optimization.

## Common Patterns

### Auth Middleware
```tsx
const publicPaths = ["/login", "/register", "/api/auth"];
export function middleware(request: NextRequest) {
  const isPublic = publicPaths.some((p) => request.nextUrl.pathname.startsWith(p));
  if (isPublic) return NextResponse.next();
  const session = request.cookies.get("session");
  if (!session) return NextResponse.redirect(new URL("/login", request.url));
  return NextResponse.next();
}
```

### Internationalization (i18n)
```tsx
const locales = ["en", "fr", "de"];
const defaultLocale = "en";
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasLocale = locales.some((l) => pathname.startsWith(`/${l}/`) || pathname === `/${l}`);
  if (hasLocale) return NextResponse.next();
  const preferred = request.headers.get("accept-language")?.split(",")[0].split("-")[0];
  const locale = locales.includes(preferred ?? "") ? preferred : defaultLocale;
  return NextResponse.rewrite(new URL(`/${locale}${pathname}`, request.url));
}
```

### Dynamic OG Images
```tsx
// app/api/og/route.tsx
import { ImageResponse } from "next/og";
export async function GET(request: Request) {
  const title = new URL(request.url).searchParams.get("title") ?? "Default";
  return new ImageResponse(
    (<div style={{ display: "flex", fontSize: 60, background: "white",
      width: "100%", height: "100%", alignItems: "center", justifyContent: "center" }}>
      {title}
    </div>),
    { width: 1200, height: 630 }
  );
}
```

## Performance Tips

- **Streaming with Suspense:** Wrap slow components in `<Suspense>` with a fallback. The shell renders immediately.
- **Partial Prerendering (experimental):** Static shell with dynamic holes that stream in.
- **Parallel data fetching:** Use `Promise.all` for independent fetches instead of sequential awaits.
- **Minimize `"use client"`:** Push interactivity to leaf components to reduce client JS.
- **Lazy-load heavy components:**
  ```tsx
  import dynamic from "next/dynamic";
  const Chart = dynamic(() => import("./chart"), { ssr: false });
  ```
- **Optimize fonts:** Use `next/font` for self-hosted fonts with zero layout shift.
- **Analyze bundles:** `ANALYZE=true next build` with `@next/bundle-analyzer`.
- **Prefer Server Components** for data display -- zero client bundle cost.
- **Use `React.cache`** for request-level deduplication of non-fetch functions.
