---
name: web-performance
description: Web performance analysis and optimization across the full stack. Use when the user asks about Core Web Vitals, Lighthouse audits, page speed, load times, bundle size reduction, image optimization, caching strategies, code splitting, lazy loading, font loading, compression, CDN configuration, render-blocking resources, performance budgets, real user monitoring, synthetic monitoring, server-side rendering performance, Time to First Byte, First Contentful Paint, Largest Contentful Paint, Cumulative Layout Shift, or any aspect of making websites and web applications faster.
---

# Web Performance Optimization

Reference for diagnosing and improving web application performance, covering measurement, asset delivery, rendering, caching, and monitoring.

## 1. Core Web Vitals

### Largest Contentful Paint (LCP)
Measures time until the largest visible content element (image, video poster, or text block) finishes rendering.
- Good: <= 2.5s | Needs improvement: <= 4.0s | Poor: > 4.0s
- Causes of poor LCP: slow TTFB, render-blocking CSS/JS, slow hero image loads, client-side rendering delays.

### Interaction to Next Paint (INP)
Replaced FID in March 2024. Measures latency of all click, tap, and keyboard interactions, reports near the worst case.
- Good: <= 200ms | Needs improvement: <= 500ms | Poor: > 500ms
- Causes of poor INP: long main-thread tasks, excessive DOM size, layout thrashing, heavy event handlers.

### Cumulative Layout Shift (CLS)
Measures unexpected layout shifts across the page lifespan.
- Good: <= 0.1 | Needs improvement: <= 0.25 | Poor: > 0.25
- Causes of poor CLS: images/iframes without dimensions, dynamically injected content above the fold, font reflow (FOUT), late-loading CSS.

## 2. Measurement Tools

### Lighthouse and PageSpeed Insights
- Run Lighthouse from Chrome DevTools, CLI (`npx lighthouse URL`), or the Node API.
- PageSpeed Insights (`pagespeed.web.dev`) combines lab (Lighthouse) and field (CrUX) data.
- Score weights: LCP 25%, TBT 30%, CLS 25%, FCP 10%, Speed Index 10%.
- Lab data is reproducible but synthetic. Field data reflects real users but requires traffic volume.

### Chrome DevTools Performance Tab
- Record a page load or interaction; inspect the flame chart for long tasks (>50ms).
- Check the "Timings" lane for LCP, FCP, and DCL markers.
- Use the "Coverage" tab to find unused CSS and JavaScript.

### WebPageTest
- Test from multiple locations on real devices and browsers.
- Waterfall view shows DNS, connect, TLS, TTFB, and download phases per resource.
- Filmstrip view shows visual progress frame by frame.
- Use scripted tests for multi-step flows; compare runs side-by-side.

## 3. Image Optimization

**Modern formats**: WebP is 25-35% smaller than JPEG. AVIF is 20-50% smaller than WebP for photos. Use `<picture>` for format negotiation:
```html
<picture>
  <source type="image/avif" srcset="photo.avif">
  <source type="image/webp" srcset="photo.webp">
  <img src="photo.jpg" alt="Description" width="800" height="600">
</picture>
```

**Responsive images**: Serve different sizes via `srcset` and `sizes` to avoid oversized downloads:
```html
<img srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
     sizes="(max-width: 600px) 400px, (max-width: 1000px) 800px, 1200px"
     src="photo-800.jpg" alt="Description" width="800" height="600">
```

**Lazy loading**: Use `loading="lazy"` on offscreen images. Do not lazy-load the LCP image; use `fetchpriority="high"` on it instead.

**Image CDNs** (Cloudinary, imgix, Cloudflare Images) resize, compress, and convert images on the fly via URL parameters.

## 4. JavaScript Performance

### Code Splitting
```javascript
// Route-based splitting in React
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
// Manual dynamic import
const { Editor } = await import('./Editor');
```
- Split by route so users only download code for the current page.
- Split heavy libraries (charting, PDF, maps) into separate chunks.

### Tree Shaking
- Use ES module syntax (`import`/`export`) so bundlers can eliminate dead code.
- Avoid `import * as lib` when you only need specific functions.
- Ensure third-party packages provide an ES module build (`"module"` field in package.json).
- Mark packages as side-effect-free: `"sideEffects": false` in package.json.

### Reducing Main Thread Work
- Break long tasks using `requestIdleCallback`, `scheduler.postTask`, or `setTimeout(fn, 0)`.
- Move heavy computation to Web Workers.
- Avoid synchronous layout reads inside loops (layout thrashing).
- Defer non-critical JS with `<script defer>` or `<script type="module">`.

## 5. CSS Performance

**Critical CSS**: Inline above-the-fold CSS in `<head>`, load the full stylesheet asynchronously:
```html
<head>
  <style>/* Critical CSS inlined here */</style>
  <link rel="preload" href="styles.css" as="style" onload="this.rel='stylesheet'">
  <noscript><link rel="stylesheet" href="styles.css"></noscript>
</head>
```
Tools like the `critical` npm package can extract critical CSS automatically.

**Reducing render-blocking CSS**: Split CSS per route, use `media` attributes on non-applicable stylesheets, avoid `@import` (it creates sequential requests).

**CSS Containment**:
```css
.card {
  contain: layout style paint;
  content-visibility: auto;
  contain-intrinsic-size: 0 200px;
}
```
`content-visibility: auto` skips rendering for offscreen elements. Provide `contain-intrinsic-size` to preserve scroll position.

## 6. Font Loading

```css
@font-face {
  font-family: 'CustomFont';
  src: url('custom.woff2') format('woff2');
  font-display: swap; /* or optional, fallback */
}
```
- `swap`: shows fallback text immediately, swaps on load. Risk of layout shift.
- `optional`: uses fallback for the whole visit if the font does not load quickly. Best for non-critical fonts.
- Preload critical fonts: `<link rel="preload" href="custom.woff2" as="font" type="font/woff2" crossorigin>`.
- Subset unused glyphs with `pyftsubset`, `glyphhanger`, or Google Fonts `&text=` parameter.
- Variable fonts replace multiple weight/style files with a single file.

## 7. Caching Strategies

### Cache-Control Headers
```
Cache-Control: public, max-age=31536000, immutable   # hashed assets
Cache-Control: no-cache                               # HTML (always revalidate)
Cache-Control: private, max-age=0, must-revalidate    # API responses
```
- `immutable`: skip revalidation on reload; safe only for content-hashed URLs.
- `no-cache`: always revalidate (not the same as `no-store`).
- `stale-while-revalidate`: serve stale content while fetching fresh copy in the background.

### ETags
ETags enable conditional requests via `If-None-Match`. The server responds 304 Not Modified if unchanged, saving bandwidth.

### Service Workers
```javascript
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((response) => {
        const clone = response.clone();
        caches.open('v1').then((cache) => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
```
Strategies: **cache-first** (static assets), **network-first** (API calls), **stale-while-revalidate** (balance of speed and freshness).

## 8. CDN Setup and Configuration

- Serve static assets from edge nodes geographically close to users.
- Use a cookieless subdomain for static assets to reduce request header size.
- Match CDN cache TTLs to your Cache-Control headers.
- Enable Brotli/gzip compression at the edge.
- Use CDN-level image optimization where available.
- Tie cache invalidation/purge workflows to your deployment pipeline.

## 9. Compression

| Algorithm | Savings vs. Uncompressed | Browser Support | Notes |
|-----------|--------------------------|-----------------|-------|
| gzip | 60-80% | Universal | Baseline everywhere |
| Brotli | 15-25% smaller than gzip | All modern browsers | Best for pre-compressed static assets |
| zstd | Comparable to Brotli | Chrome 123+, Firefox 126+ | Faster compression, emerging support |

- Pre-compress static assets at build time (Brotli level 11) for best ratios.
- Use dynamic compression at server/CDN for HTML and API responses.
- Set `Vary: Accept-Encoding` so caches store separate versions per encoding.

## 10. Preloading and Prefetching

```html
<link rel="preload" href="critical.js" as="script">
<link rel="preload" href="hero.avif" as="image" type="image/avif">
<link rel="prefetch" href="/next-page.js">
<link rel="preconnect" href="https://api.example.com">
<link rel="dns-prefetch" href="https://analytics.example.com">
```
- **preload**: high-priority fetch for current-page resources. Limit to 2-3 critical items.
- **prefetch**: low-priority speculative fetch for next-navigation resources.
- **preconnect**: early DNS + TCP + TLS to third-party origins.
- **dns-prefetch**: DNS-only resolution, lighter than preconnect, wider support.
- Use `fetchpriority="high"` on the LCP image, `fetchpriority="low"` on non-critical resources.

## 11. Rendering Strategies

**Server-Side Rendering (SSR)**: Server generates full HTML per request. Faster FCP, better SEO, but higher server load. Frameworks: Next.js, Nuxt, SvelteKit, Remix.

**Static Site Generation (SSG)**: Pages pre-rendered at build time, served from CDN. Fastest TTFB. Not suitable for highly dynamic content. ISR (Next.js) bridges the gap.

**Client-Side Rendering (CSR)**: Minimal HTML shell; JS fetches data and renders. Slower initial paint. Good for authenticated apps behind login. Mitigate with code splitting and skeleton screens.

**Streaming and Partial Hydration**: Streaming SSR sends HTML in chunks as data resolves. Partial hydration only hydrates interactive components. React Server Components mix server and client rendering in one tree.

## 12. Bundle Analysis

**webpack-bundle-analyzer**:
```bash
npx webpack --profile --json > stats.json
npx webpack-bundle-analyzer stats.json
```
Look for duplicate libraries, oversized dependencies, and unstripped locale data.

**source-map-explorer**:
```bash
npx source-map-explorer dist/main.js dist/main.js.map
```
Works with any bundler that produces source maps.

**Import Cost** editor plugins show the size of each import inline during development.

## 13. Database Query Impact on Page Load

Slow queries directly increase TTFB for SSR pages and API response times for CSR apps.
- Add indexes for columns in WHERE, JOIN, and ORDER BY clauses.
- Avoid N+1 query patterns; use eager loading or batched queries.
- Cache frequently accessed, rarely changing data in Redis or Memcached.
- Use APM tools (Datadog, New Relic, Sentry) to identify slow queries.
- Run independent data fetches in parallel for SSR pages.

## 14. Real User Monitoring (RUM)

- The `web-vitals` JS library reports LCP, INP, CLS, FCP, and TTFB to your analytics endpoint.
- The PerformanceObserver API provides raw timing data for resources, long tasks, and layout shifts.
- Google CrUX aggregates field data from Chrome users, accessible via BigQuery or the CrUX API.
- Commercial RUM: Datadog RUM, New Relic Browser, Speedcurve, Sentry Performance.
- Segment data by device type, connection speed, and geography.
- Track custom timings for business-critical interactions (time to first search result, checkout).

## 15. Performance Budgets

| Metric | Example Budget |
|--------|---------------|
| Total JS (compressed) | < 200 KB |
| Total CSS (compressed) | < 50 KB |
| Total images per page | < 500 KB |
| Total font files | < 100 KB |
| LCP | < 2.5s |
| INP | < 200ms |
| CLS | < 0.1 |
| Total page weight | < 1 MB |

Enforcement: `bundlesize` or `size-limit` in CI, Lighthouse CI assertions, webpack `performance.maxAssetSize`.

## 16. Common Wins

- **Reduce HTTP requests**: combine small files, use SVG symbol sheets, inline critical resources.
- **Minification**: Terser for JS, cssnano or Lightning CSS for CSS.
- **HTTP/2 and HTTP/3**: multiplexing eliminates domain sharding; many small files perform well.
- **Lazy load offscreen content**: images, iframes, below-fold components.
- **Remove unused dependencies**: audit with `depcheck` or `knip`.
- **Avoid layout shifts**: set explicit dimensions on images, videos, and ad slots.
- **Reduce third-party impact**: load scripts async, use facades for heavy embeds (YouTube, chat).
- **103 Early Hints**: send preload hints before the full response is ready.

## 17. Performance Audit Checklist

1. Measure with Lighthouse, WebPageTest, and field data (CrUX or RUM).
2. Set performance budgets for bundle sizes and Core Web Vitals.
3. Optimize LCP: preload the element, serve modern formats, set `fetchpriority="high"`.
4. Reduce INP: break long tasks, debounce handlers, minimize DOM size.
5. Fix CLS: set dimensions on media, avoid injecting content above the fold.
6. Enable Brotli or gzip on all text resources.
7. Configure caching with content-hashed filenames and long max-age.
8. Implement code splitting and lazy loading for routes and heavy components.
9. Inline critical CSS, defer non-critical stylesheets.
10. Preload fonts, use `font-display: swap` or `optional`, subset unused glyphs.
11. Serve static assets through a CDN.
12. Analyze bundles for duplicate or oversized dependencies.
13. Optimize database queries affecting TTFB.
14. Deploy RUM for continuous real-user monitoring.
15. Audit third-party scripts for size and main-thread impact.
