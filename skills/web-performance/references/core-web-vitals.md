# Core Web Vitals and Performance Optimization

## Core Web Vitals (CWV)

Google's three essential metrics for measuring user experience:

### 1. Largest Contentful Paint (LCP)
**What:** Time when the largest visible element on the page becomes visible.

**Target:** < 2.5 seconds

**Causes of Poor LCP:**
- Large, unoptimized images
- Slow server response time (TTFB)
- Render-blocking JavaScript/CSS
- Client-side rendering without optimization

**Optimization:**
```html
<!-- ❌ SLOW: Large image, deferred loading -->
<img src="hero.jpg" alt="Hero" />

<!-- ✅ FAST: Optimized image with priority -->
<img src="hero.webp" alt="Hero" fetchpriority="high" loading="eager" />
```

```css
/* ❌ Render-blocking */
<link rel="stylesheet" href="critical.css" />
<script src="app.js"></script>

/* ✅ Non-blocking */
<link rel="preload" href="app.js" as="script" />
<script src="app.js" async></script>
<link rel="stylesheet" href="critical.css" />
<link rel="stylesheet" href="non-critical.css" media="print" onload="this.media='all'" />
```

### 2. First Input Delay (FID)
**What:** Time between user input and browser response.

**Target:** < 100 milliseconds

**Causes of Poor FID:**
- Large JavaScript execution
- Main thread blocked
- Heavy computations

**Optimization:**
```javascript
// ❌ Blocks main thread
button.addEventListener('click', () => {
    processLargeDataset(hugeData);  // 500ms operation
    updateUI();
});

// ✅ Offload to Web Worker
const worker = new Worker('processor.js');
button.addEventListener('click', () => {
    worker.postMessage(hugeData);
    worker.onmessage = (e) => updateUI(e.data);
});

// ✅ Or break into chunks with requestIdleCallback
function processInChunks(data) {
    let processed = 0;
    
    function processChunk() {
        const chunk = data.slice(processed, processed + 100);
        processData(chunk);
        processed += 100;
        
        if (processed < data.length) {
            requestIdleCallback(processChunk);
        }
    }
    
    requestIdleCallback(processChunk);
}
```

### 3. Cumulative Layout Shift (CLS)
**What:** Unexpected movement of page elements.

**Target:** < 0.1 (0-10%)

**Causes:**
- Ads/embeds without dimensions
- Font loading causing layout shift
- Images without aspect ratio
- Dynamically injected content

**Optimization:**
```html
<!-- ❌ Causes CLS: No dimensions specified -->
<img src="hero.jpg" alt="Hero" />
<iframe src="..."></iframe>

<!-- ✅ Prevents CLS: Aspect ratio preserved -->
<img src="hero.jpg" alt="Hero" width="1200" height="600" />
<div style="aspect-ratio: 16/9;">
    <iframe src="..." style="width: 100%; height: 100%;"></iframe>
</div>

<!-- ✅ Use size containment -->
<img src="hero.jpg" alt="Hero" style="contain: layout;" />
```

**Font Loading:**
```css
/* ❌ Default: Invisible text during load (FOIT) */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2');
}

/* ✅ Swap: Show fallback immediately */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2');
    font-display: swap;  /* Show serif until custom font loads */
}

/* ✅ Optional: Higher timeout for custom fonts */
@font-face {
    font-family: 'CustomFont';
    src: url('font.woff2');
    font-display: optional;  /* Use only if ready quickly */
}
```

## Performance Optimization Techniques

### 1. Code Splitting
```javascript
// ❌ One large bundle: 500KB
import * as heavyLib from 'heavy-library';

// ✅ Split by route
const Home = lazy(() => import('./pages/Home'));
const Admin = lazy(() => import('./pages/Admin'));

<Suspense fallback={<Loading />}>
    <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<Admin />} />
    </Routes>
</Suspense>
```

### 2. Image Optimization
```html
<!-- ✅ Modern format with fallback -->
<picture>
    <source srcset="image.webp" type="image/webp" />
    <source srcset="image.jpg" type="image/jpeg" />
    <img src="image.jpg" alt="Description" />
</picture>

<!-- ✅ Responsive images -->
<img 
    srcset="small.jpg 480w, medium.jpg 768w, large.jpg 1200w"
    sizes="(max-width: 600px) 480px, (max-width: 1000px) 768px, 1200px"
    src="large.jpg" 
    alt="Responsive" 
/>

<!-- ✅ Lazy loading -->
<img src="..." alt="..." loading="lazy" />
```

### 3. Caching Strategies
```javascript
// Browser cache headers
res.setHeader('Cache-Control', 'public, max-age=3600');  // 1 hour

// Immutable assets (with hash in filename)
res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');

// Don't cache HTML
res.setHeader('Cache-Control', 'no-cache, must-revalidate');
```

### 4. Compression
```nginx
# Nginx configuration
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_comp_level 6;
gzip_min_length 1000;

# Brotli (better compression)
brotli on;
brotli_types text/plain text/css application/json application/javascript;
```

### 5. Content Delivery Network (CDN)
```javascript
// Serve assets from CDN by geography
const CDN_URL = {
    'US': 'https://us-cdn.example.com',
    'EU': 'https://eu-cdn.example.com',
    'ASIA': 'https://asia-cdn.example.com'
}[getRegion()];

const imageUrl = `${CDN_URL}/images/hero.webp`;
```

### 6. Service Workers
```javascript
// Cache API responses
self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('/api')) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                if (response) return response;
                
                return fetch(event.request).then((response) => {
                    const responseClone = response.clone();
                    caches.open('api-cache-v1').then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                });
            })
        );
    }
});
```

## Performance Monitoring

### Web Vitals API
```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

getCLS(console.log);  // CLS value
getFID(console.log);  // FID value
getLCP(console.log);  // LCP value

// Send to analytics
getLCP(metric => {
    navigator.sendBeacon('/analytics', JSON.stringify(metric));
});
```

### Performance Observer
```javascript
const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
        console.log(`${entry.name}: ${entry.duration}ms`);
    }
});

observer.observe({ entryTypes: ['measure', 'navigation'] });
```

## Tools for Performance Testing

- **Lighthouse** - Chrome DevTools built-in auditing
- **WebPageTest** - Detailed waterfall charts
- **GTmetrix** - Visual metrics and recommendations
- **Speedcurve** - Continuous monitoring
- **PageSpeed Insights** - Google's official tool
- **Chrome DevTools** - Network, Performance, Rendering tabs
