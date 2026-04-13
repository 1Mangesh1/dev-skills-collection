---
name: htmx
description: htmx for building dynamic web UIs with HTML-over-the-wire. Use when user mentions "htmx", "hx-get", "hx-post", "hx-swap", "hx-trigger", "hypermedia", "HTML over the wire", "server-driven UI", "no JavaScript framework", "htmx boost", "progressive enhancement", "hyperscript", "alpine.js with htmx", or building interactive web pages without heavy JavaScript frameworks.
---

# htmx

## Fundamentals

htmx gives HTML attributes superpowers: any element can issue HTTP requests, and the server returns HTML fragments that get swapped into the DOM. No JSON APIs, no client-side rendering, no build step. The server is the single source of truth.

```html
<!-- Include htmx -->
<script src="https://unpkg.com/htmx.org@2.0.4"></script>

<!-- Any element can make requests -->
<button hx-get="/api/users" hx-target="#user-list" hx-swap="innerHTML">
  Load Users
</button>
<div id="user-list"></div>
```

## Core Request Attributes

```html
<!-- GET -->
<div hx-get="/items">Load Items</div>

<!-- POST -->
<button hx-post="/items" hx-vals='{"name": "New Item"}'>Create</button>

<!-- PUT -->
<button hx-put="/items/42" hx-vals='{"name": "Updated"}'>Update</button>

<!-- PATCH -->
<button hx-patch="/items/42" hx-vals='{"status": "done"}'>Mark Done</button>

<!-- DELETE with confirmation -->
<button hx-delete="/items/42" hx-confirm="Delete this item?">Delete</button>
```

## Swap Strategies

`hx-swap` controls how the response HTML replaces content.

```html
<!-- Replace inner content of target (default) -->
<div hx-get="/content" hx-swap="innerHTML">Load</div>

<!-- Replace entire target element -->
<div hx-get="/content" hx-swap="outerHTML">Replace Me</div>

<!-- Insert before target's first child -->
<div hx-get="/new-row" hx-swap="afterbegin">Prepend</div>

<!-- Insert after target's last child -->
<div hx-get="/new-row" hx-swap="beforeend">Append</div>

<!-- Insert before the target element -->
<div hx-get="/sibling" hx-swap="beforebegin">Before</div>

<!-- Insert after the target element -->
<div hx-get="/sibling" hx-swap="afterend">After</div>

<!-- Delete target after request -->
<button hx-delete="/items/42" hx-swap="delete" hx-target="closest tr">Remove</button>

<!-- No swap — fire request but keep DOM unchanged -->
<button hx-post="/track-click" hx-swap="none">Track</button>

<!-- Swap modifiers -->
<div hx-get="/data" hx-swap="innerHTML swap:300ms settle:500ms scroll:top show:top">
  Smooth transitions
</div>
```

## Targets

`hx-target` specifies where the response gets placed.

```html
<!-- CSS selector -->
<button hx-get="/users" hx-target="#results">Search</button>

<!-- Relative selectors -->
<button hx-get="/edit" hx-target="closest .card">Edit Card</button>
<button hx-get="/detail" hx-target="find .content">Show Detail</button>
<button hx-get="/next" hx-target="next .panel">Next Panel</button>
<button hx-get="/prev" hx-target="previous .panel">Prev Panel</button>

<!-- this — swap the element itself -->
<div hx-get="/self-update" hx-target="this">Click to reload</div>

<!-- Target the body -->
<a hx-get="/page" hx-target="body">Full page swap</a>
```

## Triggers

`hx-trigger` controls when the request fires.

```html
<!-- Default: click for buttons/links, change for inputs, submit for forms -->
<input hx-get="/search" hx-trigger="keyup" hx-target="#results" name="q">

<!-- Modifiers -->
<input hx-get="/search" hx-trigger="keyup changed delay:300ms" name="q">
<input hx-get="/validate" hx-trigger="keyup throttle:500ms" name="email">
<div hx-get="/news" hx-trigger="every 30s">Live feed</div>

<!-- from: — listen to events on other elements -->
<div hx-get="/updates" hx-trigger="click from:body">Refresh on any click</div>

<!-- Multiple triggers -->
<input hx-get="/search" hx-trigger="keyup changed delay:300ms, search" name="q">

<!-- Intersection observer — fires when element enters viewport -->
<div hx-get="/lazy-content" hx-trigger="intersect once">Loading...</div>

<!-- Load trigger — fires on page load -->
<div hx-get="/dashboard-stats" hx-trigger="load">Loading stats...</div>

<!-- Custom events -->
<div hx-get="/refresh" hx-trigger="refreshData from:body">Data</div>
```

## Indicators

Show loading state during requests.

```html
<button hx-get="/slow-data" hx-indicator="#spinner">
  Load Data
  <span id="spinner" class="htmx-indicator">Loading...</span>
</button>

<style>
  .htmx-indicator { display: none; }
  .htmx-request .htmx-indicator { display: inline; }
  .htmx-request.htmx-indicator { display: inline; }
</style>

<!-- Indicator on parent -->
<div hx-indicator="closest .card">
  <button hx-get="/data">Load</button>
  <div class="htmx-indicator">
    <svg class="animate-spin h-5 w-5">...</svg>
  </div>
</div>

<!-- Disable button during request -->
<button hx-get="/data" hx-disabled-elt="this">Submit</button>
<!-- Disable multiple elements -->
<button hx-post="/save" hx-disabled-elt="closest form">Save</button>
```

## Form Handling

```html
<!-- Forms automatically include all inputs -->
<form hx-post="/contacts" hx-target="#contact-list" hx-swap="beforeend">
  <input name="name" required>
  <input name="email" type="email" required>
  <button type="submit">Add Contact</button>
</form>

<!-- Include inputs from outside the triggering element -->
<input id="search-input" name="q">
<button hx-get="/search" hx-include="#search-input" hx-target="#results">Search</button>

<!-- Include entire form -->
<button hx-post="/save" hx-include="closest form">Save</button>

<!-- Add extra values not in the form -->
<button hx-post="/save" hx-vals='{"source": "web", "version": 2}'>Save</button>

<!-- Dynamic values with JavaScript -->
<button hx-post="/save" hx-vals="js:{ts: Date.now()}">Save with Timestamp</button>

<!-- Control which params are sent -->
<form hx-post="/update" hx-params="*">Send all</form>
<form hx-post="/update" hx-params="none">Send none</form>
<form hx-post="/update" hx-params="name,email">Send specific</form>
<form hx-post="/update" hx-params="not password">Exclude specific</form>

<!-- File upload -->
<form hx-post="/upload" hx-encoding="multipart/form-data">
  <input type="file" name="document">
  <button>Upload</button>
</form>
```

## Out-of-Band Swaps

Update multiple parts of the page from a single response.

```html
<!-- Server response can include out-of-band swaps -->
<!-- Main response gets swapped into target as usual -->
<!-- Elements with hx-swap-oob get swapped into matching IDs -->
```

Server returns:

```html
<div id="main-content">
  <!-- This goes to the normal target -->
  <p>Item saved successfully.</p>
</div>
<div id="item-count" hx-swap-oob="true">Total: 43 items</div>
<div id="notification" hx-swap-oob="innerHTML">Saved at 2:30 PM</div>
<tr id="row-42" hx-swap-oob="outerHTML">
  <td>Updated Row</td>
</tr>
```

## Headers

### Request Headers (sent by htmx)

```
HX-Request: true              — always sent, use to detect htmx requests
HX-Target: element-id         — id of the target element
HX-Trigger: element-id        — id of the triggered element
HX-Trigger-Name: name-attr    — name attribute of the trigger
HX-Current-URL: url            — current URL of the browser
HX-Prompt: value              — user response from hx-prompt
HX-Boosted: true              — if request is via hx-boost
```

### Response Headers (sent by server)

```
HX-Redirect: /new-url         — client-side redirect
HX-Refresh: true              — full page refresh
HX-Retarget: #new-target      — change the target element
HX-Reswap: outerHTML          — change the swap strategy
HX-Trigger: eventName         — trigger client-side event after settle
HX-Trigger: {"showToast": {"message": "Saved!"}}  — trigger with detail
HX-Push-Url: /new-url         — push URL to browser history
```

## Backend Integration

### Express (Node.js)

```js
const express = require('express');
const app = express();
app.use(express.urlencoded({ extended: true }));

app.get('/contacts', (req, res) => {
  const isHtmx = req.headers['hx-request'];
  const contacts = getContacts(req.query.q);
  const html = contacts.map(c =>
    `<tr><td>${c.name}</td><td>${c.email}</td></tr>`
  ).join('');
  if (isHtmx) return res.send(html);           // return fragment
  res.render('contacts', { contacts });          // return full page
});

app.delete('/contacts/:id', (req, res) => {
  deleteContact(req.params.id);
  res.set('HX-Trigger', 'contactsChanged');
  res.send('');                                  // empty response with delete swap
});
```

### Flask (Python)

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    results = search_contacts(q)
    if request.headers.get('HX-Request'):
        return render_template('partials/contact_rows.html', contacts=results)
    return render_template('search.html', contacts=results)

@app.route('/contacts', methods=['POST'])
def create_contact():
    contact = create(request.form)
    resp = make_response(render_template('partials/contact_row.html', contact=contact))
    resp.headers['HX-Trigger'] = 'contactsChanged'
    return resp
```

### Django

```python
from django.http import HttpResponse
from django.template.loader import render_to_string

def contact_list(request):
    contacts = Contact.objects.filter(name__icontains=request.GET.get('q', ''))
    if request.headers.get('HX-Request'):
        html = render_to_string('partials/rows.html', {'contacts': contacts})
        return HttpResponse(html)
    return render(request, 'contacts.html', {'contacts': contacts})
```

### Go

```go
func handleSearch(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query().Get("q")
    results := searchContacts(q)
    if r.Header.Get("HX-Request") != "" {
        tmpl.ExecuteTemplate(w, "contact-rows", results)
        return
    }
    tmpl.ExecuteTemplate(w, "full-page", results)
}
```

## Common Patterns

### Active Search

```html
<input type="search" name="q"
  hx-get="/search"
  hx-trigger="input changed delay:300ms, search"
  hx-target="#search-results"
  hx-indicator="#search-spinner"
  placeholder="Search contacts...">
<span id="search-spinner" class="htmx-indicator">Searching...</span>
<table><tbody id="search-results"></tbody></table>
```

### Infinite Scroll

```html
<table><tbody id="results">
  <!-- rows here -->
  <tr hx-get="/contacts?page=2"
      hx-trigger="revealed"
      hx-swap="afterend"
      hx-select="tbody > tr">
    <td>Loading more...</td>
  </tr>
</tbody></table>
```

### Click to Edit

```html
<!-- Display mode -->
<div hx-get="/contacts/42/edit" hx-trigger="click" hx-swap="outerHTML">
  <p>John Doe — john@example.com</p>
</div>

<!-- Server returns edit form -->
<form hx-put="/contacts/42" hx-swap="outerHTML">
  <input name="name" value="John Doe">
  <input name="email" value="john@example.com">
  <button>Save</button>
  <button hx-get="/contacts/42" hx-swap="outerHTML">Cancel</button>
</form>
```

### Bulk Update

```html
<form hx-put="/contacts/bulk" hx-target="#table-body" hx-swap="innerHTML">
  <input type="checkbox" id="select-all"
    onclick="document.querySelectorAll('.row-check').forEach(c => c.checked = this.checked)">
  <table><tbody id="table-body">
    <tr>
      <td><input type="checkbox" class="row-check" name="ids" value="1"></td>
      <td>Contact 1</td>
    </tr>
  </tbody></table>
  <button>Activate Selected</button>
</form>
```

### Lazy Loading

```html
<div hx-get="/dashboard/chart" hx-trigger="load" hx-swap="outerHTML">
  <div class="skeleton-loader" style="height: 300px;"></div>
</div>
```

### Delete Row with Animation

```html
<tr>
  <td>Item Name</td>
  <td>
    <button hx-delete="/items/42"
            hx-target="closest tr"
            hx-swap="outerHTML swap:500ms"
            hx-confirm="Delete this item?">
      Delete
    </button>
  </td>
</tr>

<style>
  tr.htmx-swapping { opacity: 0; transition: opacity 500ms ease-out; }
</style>
```

## Boosting

`hx-boost` converts standard links and forms into AJAX requests with history support. Drop-in progressive enhancement.

```html
<!-- Boost all links and forms in this container -->
<div hx-boost="true">
  <a href="/about">About</a>              <!-- becomes hx-get="/about" -->
  <a href="/contact">Contact</a>

  <form action="/search" method="get">     <!-- becomes hx-get="/search" -->
    <input name="q">
    <button>Search</button>
  </form>
</div>

<!-- Boost the entire body for SPA-like navigation -->
<body hx-boost="true">
  <!-- All navigation is now AJAX -->
</body>

<!-- Exclude specific links -->
<a href="/download.pdf" hx-boost="false">Download PDF</a>

<!-- Push URL to history (default with boost) -->
<a hx-get="/page" hx-push-url="true">Navigate</a>
<a hx-get="/modal" hx-push-url="false">Open Modal</a>
```

## WebSocket and SSE Extensions

```html
<!-- Load extension -->
<script src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js"></script>

<!-- WebSocket -->
<div hx-ext="ws" ws-connect="/ws/chat">
  <div id="chat-messages"></div>
  <form ws-send>
    <input name="message">
    <button>Send</button>
  </form>
</div>

<!-- Server-Sent Events -->
<script src="https://unpkg.com/htmx-ext-sse@2.0.0/sse.js"></script>
<div hx-ext="sse" sse-connect="/events">
  <div sse-swap="notification">Waiting for notifications...</div>
  <div sse-swap="status">Status: unknown</div>
</div>
```

## Alpine.js + htmx

Alpine handles client-side state; htmx handles server communication.

```html
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx.org@2.0.4"></script>

<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>

  <div x-show="open" x-transition>
    <div hx-get="/panel-content" hx-trigger="intersect once" hx-swap="innerHTML">
      Loading...
    </div>
  </div>
</div>

<!-- Alpine reacts to htmx events -->
<div x-data="{ saving: false }"
     @htmx:before-request.window="saving = true"
     @htmx:after-request.window="saving = false">
  <span x-show="saving">Saving...</span>
  <form hx-post="/save">
    <input name="data">
    <button>Save</button>
  </form>
</div>
```

## CSS Transitions

htmx adds classes during the swap lifecycle for animation hooks.

```css
/* Element being removed */
.htmx-swapping { opacity: 0; transition: opacity 0.5s ease-out; }

/* New content settling in */
.htmx-added { opacity: 0; }
.htmx-settling { opacity: 1; transition: opacity 0.3s ease-in; }

/* During request */
.htmx-request { opacity: 0.5; }
```

```html
<!-- Use swap/settle timing to match CSS transitions -->
<div hx-get="/new-content" hx-swap="innerHTML swap:500ms settle:300ms">
  Animated swap
</div>

<!-- View Transitions API (modern browsers) -->
<div hx-get="/page" hx-swap="innerHTML transition:true">Navigate</div>
```

## Validation Patterns

```html
<!-- Inline field validation -->
<input name="email" type="email"
  hx-post="/validate/email"
  hx-trigger="blur changed"
  hx-target="next .error"
  hx-swap="innerHTML">
<span class="error"></span>

<!-- Server returns validation HTML -->
<!-- Success: empty string or checkmark -->
<!-- Failure: <span class="text-red-500">Email already taken</span> -->

<!-- Form-level validation with error summary -->
<form hx-post="/register" hx-target="#form-errors" hx-swap="innerHTML">
  <div id="form-errors"></div>
  <input name="username" required>
  <input name="email" type="email" required>
  <button>Register</button>
</form>

<!-- Prevent request if client validation fails -->
<form hx-post="/save"
      hx-trigger="submit"
      hx-on::before-request="if(!this.checkValidity()){event.preventDefault();this.reportValidity()}">
  <input name="name" required>
  <button>Save</button>
</form>
```

## htmx Events

```html
<!-- Listen to htmx events -->
<div hx-get="/data" hx-trigger="load"
     hx-on::after-settle="console.log('Content loaded')">
  Loading...
</div>

<!-- JavaScript event listeners -->
<script>
  document.body.addEventListener('htmx:beforeRequest', (e) => {
    console.log('Request starting:', e.detail.pathInfo);
  });
  document.body.addEventListener('htmx:afterSwap', (e) => {
    console.log('Content swapped into:', e.detail.target);
  });
  document.body.addEventListener('htmx:responseError', (e) => {
    alert('Request failed: ' + e.detail.xhr.status);
  });

  // Respond to server-triggered events via HX-Trigger header
  document.body.addEventListener('showToast', (e) => {
    showNotification(e.detail.message);
  });
</script>
```

## htmx vs React/Vue Trade-offs

**Choose htmx when:**
- Server-rendered apps (Django, Rails, Laravel, Go templates)
- CRUD-heavy applications with straightforward interactions
- Enhancing existing multi-page apps without a rewrite
- Team knows backend well but not frontend frameworks
- SEO is critical and SSR complexity is unwanted
- Minimal client-side state management needed

**Choose React/Vue/Svelte when:**
- Complex client-side state (real-time collaboration, drag-and-drop)
- Rich interactive UIs (spreadsheets, design tools, IDEs)
- Offline-first or PWA requirements
- Large ecosystem of UI component libraries needed
- Team already invested in a JS framework
- Need for native mobile apps via React Native or similar

**Hybrid approach:** Use htmx for most pages, embed React/Vue components for complex widgets. htmx handles navigation and data mutations; JS frameworks handle rich interactivity.
