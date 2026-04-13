---
name: tailwind-css
description: Tailwind CSS utility-first patterns, configuration, and component recipes. Use when user mentions "tailwind", "tailwindcss", "utility classes", "tailwind config", "tailwind components", "responsive design with tailwind", "dark mode tailwind", "tailwind plugins", or styling with utility-first CSS.
---

# Tailwind CSS

## Setup

### Installation (v3)

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx,vue,svelte}"],
  theme: { extend: {} },
  plugins: [],
}
```

### CSS Entry Point

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### PostCSS Config

```js
module.exports = {
  plugins: { tailwindcss: {}, autoprefixer: {} },
}
```

## Core Concepts

Tailwind is utility-first: compose designs in markup using single-purpose classes instead of writing custom CSS. Recommended class order: layout/position, display/flex/grid, spacing, sizing, typography, backgrounds, borders, effects, transitions. Responsive/state prefixes go outermost.

```html
<div class="flex items-center gap-4 rounded-lg bg-white p-6 shadow-md">
  <img class="h-12 w-12 rounded-full" src="avatar.jpg" alt="" />
  <div>
    <p class="text-sm font-medium text-gray-900">Jane Smith</p>
    <p class="text-sm text-gray-500">Engineering</p>
  </div>
</div>
```

## Layout

```html
<!-- Flexbox -->
<div class="flex items-center justify-between gap-4">...</div>
<div class="flex flex-col items-start gap-2">...</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-6">...</div>
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">...</div>

<!-- Container -->
<div class="container mx-auto px-4">...</div>

<!-- Spacing: p-{n}, m-{n}, gap-{n}. 1 unit = 0.25rem = 4px -->
<!-- Sizing -->
<div class="h-screen w-full max-w-lg min-h-0">...</div>
<!-- w-: full, screen, min, max, fit, auto, 1/2, 1/3, 2/3, 1/4, 3/4 -->
```

## Typography

```html
<p class="text-base font-medium leading-6 tracking-wide text-gray-700">...</p>
<!-- Font Size: text-xs, text-sm, text-base, text-lg, text-xl, text-2xl...text-9xl -->
<!-- Font Weight: font-thin(100)...font-normal(400)...font-bold(700)...font-black(900) -->
<!-- Line Height: leading-none(1), leading-tight(1.25), leading-normal(1.5), leading-loose(2) -->
<!-- Letter Spacing: tracking-tighter, tracking-tight, tracking-normal, tracking-wide, tracking-widest -->
<p class="truncate">...</p>           <!-- single line ellipsis -->
<p class="line-clamp-3">...</p>       <!-- multi-line clamp -->
```

## Responsive Design

Mobile-first breakpoints. Unprefixed = all sizes. Prefixed = that breakpoint and above.

| Prefix | Min-width | Target         |
|--------|-----------|----------------|
| `sm:`  | 640px     | Large phones   |
| `md:`  | 768px     | Tablets        |
| `lg:`  | 1024px    | Laptops        |
| `xl:`  | 1280px    | Desktops       |
| `2xl:` | 1536px    | Large screens  |

```html
<div class="w-full md:w-1/2 lg:w-1/3">...</div>
<div class="hidden lg:block">Visible on large screens only</div>
<div class="block lg:hidden">Visible below large screens only</div>
```

## Dark Mode

### Class Strategy (manual toggle)

```js
module.exports = { darkMode: 'class' }
```

```html
<html class="dark">
  <body class="bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
    <p class="text-gray-600 dark:text-gray-300">Adapts to dark mode.</p>
  </body>
</html>
```

### Media Strategy (follows OS preference)

```js
module.exports = { darkMode: 'media' }
```

No parent class needed. `dark:` variants apply based on `prefers-color-scheme`.

## Hover, Focus, and Active States

```html
<button class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
  Click me
</button>
<input class="border focus:border-blue-500 focus-visible:ring-2 disabled:opacity-50 disabled:cursor-not-allowed" />
<li class="first:pt-0 last:pb-0 odd:bg-gray-50 even:bg-white">...</li>
```

## Group and Peer Modifiers

```html
<!-- Group: parent state affects child styling -->
<div class="group rounded-lg p-6 hover:bg-blue-500">
  <p class="text-gray-900 group-hover:text-white">Title</p>
  <p class="text-gray-500 group-hover:text-blue-100">Changes on parent hover</p>
</div>

<!-- Peer: sibling state affects another sibling -->
<input class="peer" placeholder="Email" />
<p class="hidden peer-focus:block text-sm text-gray-500">Enter your work email</p>
<p class="hidden peer-invalid:block text-sm text-red-500">Invalid email format</p>
```

Named groups for nested contexts: `group/sidebar`, `group-hover/sidebar:text-white`.

## Custom Colors and Extending the Theme

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eff6ff', 500: '#3b82f6', 900: '#1e3a8a' },
        coral: '#ff6b6b',
      },
      spacing: { '18': '4.5rem', '88': '22rem' },
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
    },
  },
}
```

Use `extend` to add values without overriding defaults. Defining keys directly under `theme` (not `extend`) replaces the entire default scale for that property.

## Arbitrary Values

Bracket notation for one-off values not in the default scale:

```html
<div class="w-[137px] h-[calc(100vh-4rem)] bg-[#1a1a1a] text-[13px]">...</div>
<div class="grid grid-cols-[200px_1fr_200px] gap-[1.25rem]">...</div>
<div class="top-[var(--header-height)]">...</div>
<div class="[mask-type:alpha]">...</div>  <!-- arbitrary properties -->
```

## Important Modifier

Prefix any utility with `!` to apply `!important`:

```html
<div class="!text-red-500">Always red regardless of specificity conflicts</div>
```

Use sparingly. Typically needed only when overriding third-party library styles.

## Animation Utilities

```html
<svg class="animate-spin h-5 w-5">...</svg>
<div class="animate-pulse">Loading placeholder</div>
<div class="animate-ping">Notification dot</div>
<div class="animate-bounce">Scroll indicator</div>

<button class="transition-colors duration-200 ease-in-out hover:bg-blue-600">...</button>
<div class="transition-all duration-300 ease-out hover:scale-105 hover:shadow-lg">...</div>
<div class="hover:scale-110 hover:-translate-y-1 hover:rotate-3">...</div>
```

## Reusable Component Patterns

### Button

```html
<button class="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
  Save Changes
</button>
```

### Card

```html
<div class="overflow-hidden rounded-lg bg-white shadow ring-1 ring-gray-200">
  <div class="p-6">
    <h3 class="text-lg font-semibold text-gray-900">Card Title</h3>
    <p class="mt-2 text-sm text-gray-600">Card description text.</p>
  </div>
  <div class="bg-gray-50 px-6 py-3">
    <button class="text-sm font-medium text-blue-600 hover:text-blue-500">Action</button>
  </div>
</div>
```

### Input

```html
<input type="text" class="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm placeholder-gray-400 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500" placeholder="Enter value" />
```

### Badge

```html
<span class="inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">Active</span>
<span class="inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">Expired</span>
```

### Navbar

```html
<nav class="sticky top-0 z-50 border-b border-gray-200 bg-white/80 backdrop-blur">
  <div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
    <a href="/" class="text-lg font-bold text-gray-900">Logo</a>
    <div class="hidden items-center gap-6 md:flex">
      <a href="#" class="text-sm font-medium text-gray-700 hover:text-gray-900">Features</a>
      <button class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Sign Up</button>
    </div>
  </div>
</nav>
```

### Modal Overlay

```html
<div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
  <div class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
    <h2 class="text-lg font-semibold text-gray-900">Confirm Action</h2>
    <p class="mt-2 text-sm text-gray-600">Are you sure you want to proceed?</p>
    <div class="mt-6 flex justify-end gap-3">
      <button class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100">Cancel</button>
      <button class="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">Confirm</button>
    </div>
  </div>
</div>
```

## @apply for Component Extraction

```css
@layer components {
  .btn-primary {
    @apply inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
  }
}
```

When to use: repeated patterns across many files that cannot use a shared component (e.g., prose styles, base form elements).

When NOT to use: when a framework component (React, Vue, Svelte) can encapsulate the pattern -- prefer components over `@apply`. Do not use for one-off styles. Avoid creating an `@apply`-heavy stylesheet that recreates traditional CSS.

## Content Configuration and Tree-Shaking

Tailwind scans files in `content` for class names and generates only matching CSS. Misconfigured paths are the most common cause of missing styles.

```js
content: [
  "./src/**/*.{js,ts,jsx,tsx}",
  "./public/index.html",
  "./node_modules/@acme/ui/**/*.js",  // specific third-party packages only
]
```

Dynamic class names via string concatenation (`text-${color}-500`) will not be detected. Use complete strings or safelist:

```js
module.exports = {
  safelist: ['bg-red-500', { pattern: /^text-(red|green|blue)-/ }],
}
```

## Common Class Combinations

```html
<!-- Center anything -->
<div class="flex items-center justify-center">...</div>
<div class="grid place-items-center">...</div>

<!-- Full-screen centered -->
<div class="flex min-h-screen items-center justify-center">...</div>

<!-- Visually hidden but accessible -->
<span class="sr-only">Screen reader text</span>

<!-- Aspect ratio: aspect-video, aspect-square -->

<!-- Divide between children -->
<ul class="divide-y divide-gray-200">...</ul>

<!-- Gradient -->
<div class="bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500">...</div>

<!-- Sticky header -->
<header class="sticky top-0 z-40 bg-white/90 backdrop-blur">...</header>

<!-- Scrollable container -->
<div class="h-64 overflow-y-auto">...</div>

<!-- Image cover -->
<img class="h-48 w-full object-cover" src="..." alt="" />
```

## Tailwind v4 Changes

Tailwind CSS v4 shifts configuration from JavaScript to CSS.

### CSS-First Configuration

```css
@import "tailwindcss";

@theme {
  --color-brand-500: #3b82f6;
  --color-brand-900: #1e3a8a;
  --font-family-sans: "Inter", system-ui, sans-serif;
  --breakpoint-3xl: 1920px;
}
```

### Key v4 Differences

- `@theme` replaces `theme.extend`. All design tokens are CSS custom properties.
- `@import "tailwindcss"` replaces the three `@tailwind` directives.
- Automatic content detection replaces manual `content` configuration.
- `@utility` directive for custom utilities; `@variant` for custom variants.
- `darkMode` option replaced by `@variant dark` overrides.
- No separate PostCSS plugin; uses standalone CLI or Vite plugin.

### v4 Installation

```bash
npm install tailwindcss @tailwindcss/vite   # Vite
npm install tailwindcss @tailwindcss/postcss # PostCSS
npx @tailwindcss/cli -i input.css -o output.css  # CLI
```

Custom utilities: `@utility tab-4 { tab-size: 4; }` then use as class `tab-4`.
