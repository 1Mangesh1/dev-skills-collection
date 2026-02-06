# Web Performance Quick Start

Measure and optimize web application performance and user experience.

## Core Web Vitals (Google's Key Metrics)

| Metric | Target | What It Measures |
|--------|--------|------------------|
| **LCP** | < 2.5s | Largest content visible |
| **FID** | < 100ms | Response to user input |
| **CLS** | < 0.1 | Visual stability |

## Quick Wins

1. **Optimize Images**
   - Use WebP format
   - Lazy load with `loading="lazy"`
   - Responsive images with srcset

2. **Code Splitting**
   - Split large bundles
   - Load routes on demand
   - Dynamic imports

3. **Minify & Compress**
   - Minify CSS/JS/HTML
   - Enable gzip/brotli
   - Tree shake unused code

4. **Caching**
   - Set Cache-Control headers
   - Service workers for offline
   - CDN for static assets

5. **Fonts**
   - Font subsetting
   - Preload critical fonts
   - system-ui fallback

## Performance Audit Tools

- **Lighthouse** - Built into Chrome DevTools
- **WebPageTest** - Detailed analysis
- **Speedcurve** - Continuous monitoring
- **Bundle Analyzer** - Webpack bundle sizes

## Optimization Checklist

- [ ] Images optimized (format, size, lazy)
- [ ] Minified CSS/JS/HTML
- [ ] Gzip/brotli enabled
- [ ] Code splitting implemented
- [ ] Critical resources preloaded
- [ ] Static assets cached
- [ ] Service worker implemented
- [ ] Fonts optimized
- [ ] Third-party scripts defer loaded
- [ ] No render-blocking resources

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| High LCP | Optimize images, defer JS, use CDN |
| High FID | Break up JavaScript, use workers |
| High CLS | Reserve space for images, avoid layout shifts |
| Large bundle | Code splitting, tree shaking |
| Slow fonts | System fonts, async loading |

## Performance Budget

```
JavaScript: 200KB
CSS: 50KB
Images: 500KB
Total: 750KB target
```

## Measurement Tools

```bash
# CLI
npm install -g lighthouse
lighthouse https://example.com --view

# In browser
Open DevTools → Lighthouse
```

## Metrics to Track

- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- First Input Delay (FID)
- Time to Interactive (TTI)

## Resources

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse Docs](https://developers.google.com/web/tools/lighthouse)
- [MDN Web Performance](https://developer.mozilla.org/en-US/docs/Web/Performance)
- [WebPageTest](https://www.webpagetest.org/)

## See Also

- SKILL.md - Deep dive on performance optimization
- metadata.json - Tools and resources
