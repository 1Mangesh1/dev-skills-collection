# JavaScript and CSS Bundle Optimization

## Analyzing Bundle Size

### Tools
- **webpack-bundle-analyzer** - Visual bundle size analysis
- **bundlesize** - Enforce bundle size limits
- **source-map-explorer** - Interactive treemap visualization
- **npm analyse** - Understand package sizes

### Webpack Configuration for Optimization

```javascript
// webpack.config.js
module.exports = {
  mode: 'production',
  
  optimization: {
    // Code splitting
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          priority: 10,
        },
        common: {
          minChunks: 2,
          priority: 5,
          reuseExistingChunk: true,
        },
      },
    },
    
    // Minification
    minimize: true,
    minimizer: [
      new TerserPlugin({
        terserOptions: {
          compress: {
            drop_console: true,
          },
        },
      }),
    ],
    
    // Runtime chunk
    runtimeChunk: 'single',
  },
  
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
            plugins: ['@babel/plugin-proposal-dynamic-import'],
          },
        },
      },
    ],
  },
};
```

## Tree Shaking

Remove unused code from bundles.

```javascript
// ❌ CommonJS - Cannot be tree-shaken
module.exports = {
    usedFunction: () => {},
    unusedFunction: () => {},
};

// ✅ ES6 modules - Can be tree-shaken
export const usedFunction = () => {};
export const unusedFunction = () => {};

// Only import what you need
import { usedFunction } from './utils';  // unusedFunction is NOT bundled
```

## Dynamic Imports

Load code only when needed.

```javascript
// ❌ All code loaded upfront
import * as analytics from 'heavy-analytics-lib';

// ✅ Load on demand
button.addEventListener('click', async () => {
    const { trackEvent } = await import('heavy-analytics-lib');
    trackEvent('button-clicked');
});

// ✅ React lazy loading
const HeavyComponent = React.lazy(() => import('./HeavyComponent'));

function App() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <HeavyComponent />
        </Suspense>
    );
}
```

## Polyfill Management

Don't ship polyfills to modern browsers.

```javascript
// ❌ Ship everything to everyone
import '@babel/polyfill';

// ✅ Conditional polyfill loading
if (!window.Promise) {
    const script = document.createElement('script');
    script.src = '/polyfills/promise.js';
    document.head.appendChild(script);
}

// ✅ Modern approach with useBuiltIns
// In .babelrc
{
  "presets": [
    [
      "@babel/preset-env",
      {
        "useBuiltIns": "entry",
        "corejs": 3
      }
    ]
  ]
}
```

## Dependency Audit

### Finding Heavy Dependencies

```bash
# See detailed size breakdown
npm list

# Find duplicate dependencies
npm ls express

# Audit for vulnerabilities and size
npx npm-check-updates

# Analyze unused dependencies
npx depcheck
```

### Lighter Alternatives

| Heavy | Alternative | Size Reduction |
|-------|-------------|-----------------|
| moment | date-fns, dayjs | 96%, 97% |
| lodash | lodash-es + tree-shake | 70% |
| react | preact | 95% |
| jQuery | native DOM APIs | 100% |
| babel-core | SWC | 50% faster |

## Critical Path Rendering

Optimize time to first paint.

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Critical CSS inline -->
    <style>
        body { color: black; }
        .container { max-width: 1200px; }
    </style>
    
    <!-- Non-critical CSS deferred -->
    <link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'" />
    <noscript><link rel="stylesheet" href="styles.css" /></noscript>
    
    <!-- Preload critical resources -->
    <link rel="preload" href="/app.js" as="script" />
    <link rel="preload" href="/font.woff2" as="font" type="font/woff2" crossorigin />
</head>
<body>
    <div id="root"><!-- App rendered here --></div>
    
    <!-- Deferred scripts -->
    <script src="/app.js" defer></script>
</body>
</html>
```

## Monitoring Bundle Changes

```javascript
// bundlesize.config.json
{
  "files": [
    {
      "path": "./dist/main.*.js",
      "maxSize": "300KB"
    },
    {
      "path": "./dist/vendor.*.js",
      "maxSize": "200KB"
    },
    {
      "path": "./dist/styles.*.css",
      "maxSize": "50KB"
    }
  ]
}
```

Run in CI to prevent bundle bloat:
```bash
npx bundlesize
```
