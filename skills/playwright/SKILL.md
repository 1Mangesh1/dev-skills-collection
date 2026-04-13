---
name: playwright
description: Playwright for end-to-end testing, browser automation, and web scraping. Use when user mentions "playwright", "e2e testing", "end to end test", "browser testing", "browser automation", "web scraping", "headless browser", "cross-browser testing", "page.goto", "locator", or automating browser interactions.
---

# Playwright

## Setup

```bash
npm init playwright@latest          # scaffolds project with config, sample test, browsers
npx playwright install              # install all browsers
npx playwright install chromium     # install single browser
```

### Configuration

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    { name: 'mobile-chrome', use: { ...devices['Pixel 5'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## Writing Tests

```ts
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should do something specific', async ({ page }) => {
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Success')).toBeVisible();
  });
});
```

Playwright auto-waits for elements to be visible, stable, enabled, and receiving events before performing actions. Assertions auto-retry until the timeout (default 5s).

## Locators

Prefer role-based and user-facing locators over CSS selectors.

```ts
// Role-based (best for accessibility)
page.getByRole('button', { name: 'Sign In' })
page.getByRole('heading', { name: 'Dashboard', level: 2 })
page.getByRole('textbox', { name: 'Email' })
page.getByRole('checkbox', { name: 'Remember me' })

// Text and label-based
page.getByText('Welcome back')
page.getByLabel('Email address')
page.getByPlaceholder('Enter your email')
page.getByTestId('submit-button')       // matches [data-testid="submit-button"]

// CSS and XPath (last resort)
page.locator('.nav-item.active')
page.locator('xpath=//div[@class="container"]//span')

// Filtering and chaining
page.getByRole('listitem').filter({ hasText: 'Product A' })
page.getByRole('listitem').filter({ has: page.getByRole('button', { name: 'Buy' }) })
page.locator('.card').nth(2)
page.locator('.card').first()
```

## Actions

```ts
// Click variants
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('button').dblclick();
await page.getByRole('button').click({ button: 'right' });

// Text input
await page.getByLabel('Email').fill('user@example.com');       // clears then sets value
await page.getByLabel('Name').pressSequentially('John', { delay: 50 }); // simulates typing
await page.getByLabel('Name').clear();

// Keyboard
await page.keyboard.press('Enter');
await page.keyboard.press('Control+A');

// Select, checkbox, radio
await page.getByLabel('Country').selectOption('us');
await page.getByLabel('Country').selectOption({ label: 'United States' });
await page.getByRole('checkbox', { name: 'Agree' }).check();
await page.getByRole('checkbox', { name: 'Agree' }).uncheck();

// Hover, focus, drag
await page.getByText('Menu').hover();
await page.getByLabel('Email').focus();
await page.getByTestId('source').dragTo(page.getByTestId('target'));
```

## Assertions

```ts
await expect(page.getByText('Welcome')).toBeVisible();
await expect(page.getByText('Loading')).toBeHidden();
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page.getByRole('heading')).toHaveText(/dashboard/i);
await expect(page.getByRole('status')).toContainText('3 items');
await expect(page.getByLabel('Email')).toHaveValue('user@example.com');
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('My App - Dashboard');
await expect(page.getByRole('button')).toBeEnabled();
await expect(page.getByRole('checkbox')).toBeChecked();
await expect(page.getByRole('listitem')).toHaveCount(5);
await expect(page.getByTestId('card')).toHaveClass(/highlighted/);
await expect(page.getByTestId('card')).toHaveAttribute('data-status', 'active');
await expect(page.getByText('Error')).not.toBeVisible();

// Soft assertions (do not stop the test on failure)
await expect.soft(page.getByText('Title')).toHaveText('Expected');
```

## Page Navigation and Waiting

```ts
await page.goto('https://example.com');
await page.goto('/relative-path');       // uses baseURL from config
await page.goBack();
await page.reload();

await page.waitForURL('**/dashboard');
await page.waitForSelector('.dynamic-content', { state: 'visible' });
await page.waitForSelector('.spinner', { state: 'detached' });

const response = await page.waitForResponse(
  resp => resp.url().includes('/api/users') && resp.status() === 200
);

await page.waitForLoadState('networkidle');
await page.waitForFunction(() => document.title.includes('Ready'));
await page.getByText('Loaded').click({ timeout: 10000 });
```

## Network Interception

```ts
// Mock an API response
await page.route('**/api/users', async route => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{ id: 1, name: 'Alice' }]),
  });
});

// Modify a real response
await page.route('**/api/settings', async route => {
  const response = await route.fetch();
  const json = await response.json();
  json.featureFlag = true;
  await route.fulfill({ response, json });
});

// Block resources to speed up tests
await page.route('**/*.{png,jpg,jpeg,gif,svg}', route => route.abort());

// Inspect outgoing requests
await page.route('**/api/submit', async route => {
  const postData = route.request().postDataJSON();
  expect(postData.email).toBe('user@example.com');
  await route.continue();
});

// HAR recording and replay
await page.routeFromHAR('tests/data/api.har', { update: true });  // record
await page.routeFromHAR('tests/data/api.har');                     // replay
```

## Authentication

Save login state once, reuse across all tests:

```ts
// auth.setup.ts
import { test as setup } from '@playwright/test';
const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: authFile });
});
```

```ts
// In playwright.config.ts projects array
{ name: 'setup', testMatch: /.*\.setup\.ts/ },
{
  name: 'chromium',
  dependencies: ['setup'],
  use: { ...devices['Desktop Chrome'], storageState: 'playwright/.auth/user.json' },
},
```

Add `playwright/.auth/` to `.gitignore`.

## Multiple Pages, Tabs, and Popups

```ts
const newPage = await page.context().newPage();
await newPage.goto('/another-page');

// Handle popup (OAuth window, target="_blank")
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Sign in with Google' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();

// Isolated sessions with separate browser contexts
const context1 = await browser.newContext();
const context2 = await browser.newContext();
const page1 = await context1.newPage();
const page2 = await context2.newPage();
```

## Screenshots and Video

```ts
await page.screenshot({ path: 'screenshots/home.png' });
await page.screenshot({ path: 'full.png', fullPage: true });
await page.getByTestId('chart').screenshot({ path: 'chart.png' });
```

Configure globally in `playwright.config.ts` under `use`: `screenshot: 'only-on-failure'`, `video: 'retain-on-failure'`.

## Visual Regression Testing

```ts
await expect(page).toHaveScreenshot();
await expect(page).toHaveScreenshot('homepage.png');
await expect(page).toHaveScreenshot({ maxDiffPixels: 100 });
await expect(page.getByTestId('header')).toHaveScreenshot('header.png');
```

Update baselines with `npx playwright test --update-snapshots`. Baselines are stored alongside the test file in a `-snapshots/` directory. Commit them to version control.

## Parallel Execution and Sharding

```ts
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,   // parallelize tests within a single file
  workers: 4,            // fixed worker count (or '50%' for percentage of CPUs)
});

// Force serial execution for a specific describe block
test.describe.configure({ mode: 'serial' });
```

Shard across CI machines: `npx playwright test --shard=1/3`, `--shard=2/3`, `--shard=3/3`.

## Debugging

```bash
npx playwright test --headed                    # see the browser
npx playwright test --debug                     # step through with Inspector
npx playwright codegen https://example.com      # record actions as code
npx playwright show-trace trace.zip             # open trace viewer
npx playwright test --grep "login"              # filter by test name
npx playwright test tests/login.spec.ts         # run specific file
```

Use `await page.pause()` inside a test to pause execution and open Inspector.

Trace viewer shows a timeline of actions, DOM snapshots at each step, network requests, and console logs. Enable with `trace: 'on-first-retry'` in config or record manually:

```ts
await page.context().tracing.start({ screenshots: true, snapshots: true });
// ... actions ...
await page.context().tracing.stop({ path: 'trace.zip' });
```

## Page Object Model

```ts
// pages/login.page.ts
import { type Locator, type Page, expect } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign In' });
  }

  async goto() { await this.page.goto('/login'); }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// tests/login.spec.ts
test('successful login', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/playwright.yml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with: { name: playwright-report, path: playwright-report/, retention-days: 30 }
```

### Sharded CI

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}
```

### Docker

```dockerfile
FROM mcr.microsoft.com/playwright:v1.48.0-noble
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npx playwright test
```

## Common Patterns

### File Upload and Download

```ts
await page.getByLabel('Upload').setInputFiles('tests/fixtures/doc.pdf');
await page.getByLabel('Upload').setInputFiles(['a.png', 'b.png']);  // multiple
await page.getByLabel('Upload').setInputFiles([]);                   // clear

const downloadPromise = page.waitForEvent('download');
await page.getByRole('link', { name: 'Download Report' }).click();
const download = await downloadPromise;
await download.saveAs('downloads/' + download.suggestedFilename());
```

### Iframe Handling

```ts
const frame = page.frameLocator('#my-iframe');
await frame.getByRole('button', { name: 'Click me' }).click();
await expect(frame.getByText('Done')).toBeVisible();
```

### Dialog Handling

```ts
page.on('dialog', dialog => dialog.accept());      // accept all alerts/confirms
page.on('dialog', dialog => dialog.dismiss());      // dismiss all

page.once('dialog', async dialog => {
  expect(dialog.message()).toBe('Are you sure?');
  await dialog.accept();
});
await page.getByRole('button', { name: 'Delete' }).click();
```

### Waiting for API Before Asserting

```ts
const responsePromise = page.waitForResponse('**/api/save');
await page.getByRole('button', { name: 'Save' }).click();
const response = await responsePromise;
expect(response.status()).toBe(200);
await expect(page.getByText('Saved')).toBeVisible();
```

### Form Validation Testing

```ts
test('validates required fields', async ({ page }) => {
  await page.goto('/contact');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Email is required')).toBeVisible();

  await page.getByLabel('Email').fill('invalid');
  await expect(page.getByText('Invalid email format')).toBeVisible();

  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Message').fill('Hello');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Message sent')).toBeVisible();
});
```
