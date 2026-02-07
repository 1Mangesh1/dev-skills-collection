# Caching Strategies

## Browser Caching

Control browser cache with HTTP headers:

```
Cache-Control: public, max-age=31536000
```

### Values

- `public` - Cache in browser and CDN
- `private` - Only in browser
- `max-age=3600` - Cache for 1 hour
- `immutable` - Never changes (use for versioned assets)

### Examples

```
# Static assets (1 year)
Cache-Control: public, max-age=31536000, immutable

# HTML (no cache, revalidate each time)
Cache-Control: public, max-age=0, must-revalidate

# API responses (1 hour)
Cache-Control: private, max-age=3600
```

## Service Workers

Offline support and advanced caching:

```javascript
// Offline-first strategy
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('/offline.html'))
  );
});
```

## CDN Caching

Content Delivery Network for geographic distribution:

```
User in NY → Nearest CDN Edge (NYC)
User in London → Nearest CDN Edge (London)
```

Popular CDNs:
- Cloudflare
- AWS CloudFront
- Akamai
- Fastly

## Versioning for Cache Busting

When you update assets, change the filename:

```html
<!-- Before -->
<script src="/app.js"></script>

<!-- After - cached version automatically updates -->
<script src="/app-abc123.js"></script>
```

Build tools handle this automatically:
- Webpack
- Vite
- Parcel

## Cache Invalidation Patterns

```
/styles-abc123.css  → /styles-def456.css  (file content changed)
```

**Never change URLs**, always create new ones for versioned assets.
