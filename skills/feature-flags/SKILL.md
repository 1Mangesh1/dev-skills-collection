---
name: feature-flags
description: Feature flag implementation, management, and best practices for gradual rollouts. Use when user mentions "feature flag", "feature toggle", "feature gate", "canary release", "percentage rollout", "A/B testing", "LaunchDarkly", "Unleash", "Flagsmith", "gradual rollout", "kill switch", "dark launch", "trunk-based development with flags", or controlling feature visibility in production.
---

# Feature Flags

## Flag Types

| Type | Purpose | Lifetime | Example |
|------|---------|----------|---------|
| Release | Gate incomplete features | Days-weeks | `new-checkout-flow` |
| Experiment | A/B test variations | Weeks-months | `pricing-page-variant` |
| Ops / Kill switch | Runtime control, emergency disable | Permanent-ish | `disable-search-indexing` |
| Permission | Entitlement gating | Permanent | `premium-analytics` |

## Implementation Patterns

### Boolean Flag

```typescript
if (featureFlags.isEnabled("new-dashboard")) {
  return <NewDashboard />;
}
return <LegacyDashboard />;
```

### Multivariate Flag

```typescript
const variant = featureFlags.getVariant("checkout-flow");
switch (variant) {
  case "single-page": return <SinglePageCheckout />;
  case "multi-step":  return <MultiStepCheckout />;
  default:            return <ClassicCheckout />;
}
```

### User-Targeted Flag

```typescript
const context = { userId: user.id, email: user.email, plan: user.plan, country: user.country };
const enabled = featureFlags.isEnabled("beta-feature", context);
```

## SDK Integration

### LaunchDarkly

```typescript
import * as LaunchDarkly from "@launchdarkly/node-server-sdk";
const client = LaunchDarkly.init(process.env.LD_SDK_KEY);
await client.waitForInitialization();
const ctx = { kind: "user", key: user.id, email: user.email, plan: user.plan };
const show = await client.variation("new-feature", ctx, false);
client.on("update:new-feature", () => console.log("Flag changed"));
process.on("SIGTERM", () => client.close());
```

### Unleash

```typescript
import { initialize } from "unleash-client";
const unleash = initialize({
  url: process.env.UNLEASH_API_URL, appName: "my-app",
  customHeaders: { Authorization: process.env.UNLEASH_API_TOKEN },
});
unleash.on("ready", () => {
  const enabled = unleash.isEnabled("new-feature", { userId: user.id });
});
```

### Flagsmith

```typescript
import Flagsmith from "flagsmith-nodejs";
const flagsmith = new Flagsmith({ environmentKey: process.env.FLAGSMITH_KEY });
const flags = await flagsmith.getIdentityFlags(user.id, { plan: user.plan });
const enabled = flags.isFeatureEnabled("new-feature");
const value = flags.getFeatureValue("banner-text");
```

### Statsig

```typescript
import Statsig from "statsig-node";
await Statsig.initialize(process.env.STATSIG_SERVER_KEY);
const enabled = Statsig.checkGate({ userID: user.id, custom: { plan: user.plan } }, "new-feature");
```

### GrowthBook

```typescript
import { GrowthBook } from "@growthbook/growthbook";
const gb = new GrowthBook({
  apiHost: "https://cdn.growthbook.io",
  clientKey: process.env.GROWTHBOOK_CLIENT_KEY,
  attributes: { id: user.id, plan: user.plan, country: user.country },
  trackingCallback: (exp, result) => {
    analytics.track("experiment_viewed", { experimentId: exp.key, variationId: result.key });
  },
});
await gb.init();
const enabled = gb.isOn("new-feature");
```

## DIY Implementation

### Environment Variables

```typescript
// Simplest approach — binary on/off, requires redeploy to change
function isEnabled(flag: string): boolean {
  return process.env[`FF_${flag.toUpperCase().replace(/-/g, "_")}`] === "true";
}
```

### Database-Backed Flags

```sql
CREATE TABLE feature_flags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  enabled BOOLEAN DEFAULT false,
  rollout_percentage INT DEFAULT 0 CHECK (rollout_percentage BETWEEN 0 AND 100),
  allowed_users TEXT[] DEFAULT '{}',
  allowed_segments TEXT[] DEFAULT '{}',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

```typescript
class FeatureFlagService {
  private cache = new Map<string, { flag: FeatureFlag; expiresAt: number }>();

  async isEnabled(name: string, ctx?: FlagContext): Promise<boolean> {
    const flag = await this.getFlag(name);
    if (!flag?.enabled) return false;
    if (ctx?.userId && flag.allowed_users.includes(ctx.userId)) return true;
    if (ctx?.segment && flag.allowed_segments.includes(ctx.segment)) return true;
    if (flag.rollout_percentage > 0 && flag.rollout_percentage < 100 && ctx?.userId) {
      return (this.hash(ctx.userId, name) % 100) < flag.rollout_percentage;
    }
    return flag.rollout_percentage === 100;
  }

  private hash(userId: string, flagName: string): number {
    let h = 0;
    const s = `${userId}:${flagName}`;
    for (let i = 0; i < s.length; i++) h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    return Math.abs(h);
  }

  private async getFlag(name: string): Promise<FeatureFlag | null> {
    const cached = this.cache.get(name);
    if (cached && cached.expiresAt > Date.now()) return cached.flag;
    const flag = await db.query("SELECT * FROM feature_flags WHERE name = $1", [name]);
    if (flag) this.cache.set(name, { flag, expiresAt: Date.now() + 30_000 });
    return flag;
  }
}
```

## Lifecycle Management

### Creation

Name flags with ownership: `<team>.<feature>` (e.g. `payments.new-checkout`). Record type, owner, ticket, and expected removal date at creation.

### Rollout Schedule

```
Day 1:  Internal only (allowlist)    Day 5:  10% (monitor metrics)
Day 3:  1% (smoke test)              Day 8:  50% (validate at scale)
Day 10: 100% (full rollout)          Day 14: Remove flag + dead code
```

### Cleanup

```bash
# Find stale flags — search for references, compare against flag service
grep -r "isEnabled\|getVariant\|checkGate\|isOn" --include="*.ts" | \
  grep -oP '"[a-z0-9-]+"' | sort -u > used_flags.txt
```

Warn on overdue flags during evaluation. Log owner and ticket for flags past expected removal date.

## Testing with Flags

### Unit Tests -- Override Flag Values

```typescript
describe("Dashboard", () => {
  afterEach(() => featureFlags.clearOverrides());

  it("renders new dashboard when flag is on", () => {
    featureFlags.override("new-dashboard", true);
    expect(render(<Dashboard />).getByTestId("new-dashboard")).toBeInTheDocument();
  });

  it("renders legacy dashboard when flag is off", () => {
    featureFlags.override("new-dashboard", false);
    expect(render(<Dashboard />).getByTestId("legacy-dashboard")).toBeInTheDocument();
  });
});
```

### Integration Tests -- Test All Variants

```typescript
for (const variant of ["single-page", "multi-step", "control"]) {
  it(`completes purchase with ${variant}`, async () => {
    featureFlags.override("checkout-flow", variant);
    await addItemToCart(testProduct);
    await submitPayment(testCard);
    expect(await getOrderStatus()).toBe("confirmed");
  });
}
```

### Avoid Combinatorial Explosion

```typescript
// BAD: 2^n tests for n flags (5 flags = 32, 10 flags = 1024)
// GOOD: Test flags independently, plus critical interactions only
const criticalCombos = [
  { "new-checkout": true, "new-payments": true },
  { "new-checkout": true, "new-payments": false },
];
for (const combo of criticalCombos) {
  it(`works with ${JSON.stringify(combo)}`, async () => {
    Object.entries(combo).forEach(([f, v]) => featureFlags.override(f, v));
  });
}
```

## Gradual Rollout Strategies

### Percentage-Based (Sticky)

```typescript
// Deterministic hashing — user always gets same experience
function isInRollout(userId: string, flagName: string, percentage: number): boolean {
  const hash = murmurHash3(`${flagName}:${userId}`) % 100;
  return hash < percentage;
}
```

### User Segments

```typescript
const segments = {
  "beta-testers": (u) => u.betaOptIn === true,
  "employees":    (u) => u.email.endsWith("@company.com"),
  "power-users":  (u) => u.actionsLast30Days > 100,
  "new-users":    (u) => daysSince(u.createdAt) < 7,
};
```

### Geographic Rollout

```typescript
const geoRollout = {
  phase1: { regions: ["us-east-1"], percentage: 100 },
  phase2: { regions: ["us-east-1", "eu-west-1"], percentage: 100 },
  phase3: { regions: ["*"], percentage: 100 },
};
```

## Trunk-Based Development with Flags

```
main ────●────●────●────●────●──── (always deployable)
          |    |    |    |    |
       add   build  wire  ramp  remove flag
       flag  behind  UI   to    + dead code
       stub  flag         100%
```

Wrap incomplete work behind a flag from the first commit. Push to main daily. Flag stays off in production until ready.

```typescript
// Commits 1-N: Build behind flag
function SearchResults({ query }) {
  if (featureFlags.isEnabled("new-search")) {
    return <ElasticSearchResults query={query} />;
  }
  return <LegacySearchResults query={query} />;
}

// Cleanup commit: Remove flag and legacy path
function SearchResults({ query }) {
  return <ElasticSearchResults query={query} />;
}
```

## Anti-Patterns

### Permanent Release Flags

```typescript
// BAD: Release flag left for months — becomes invisible tech debt
if (featureFlags.isEnabled("new-header")) { /* added Jan 2024, never removed */ }
// FIX: Set expiry at creation, enforce with CI lint rules
```

### Flag Dependencies

```typescript
// BAD: Flags that depend on other flags — undefined states when only one is on
if (featureFlags.isEnabled("new-checkout") && featureFlags.isEnabled("new-payments")) {}
// FIX: Single flag controlling related changes together
if (featureFlags.isEnabled("checkout-v2")) {}
```

### Nested Flags

```typescript
// BAD: 2^3 = 8 hidden states
if (isEnabled("a")) { if (isEnabled("b")) { if (isEnabled("c")) {} } }
// FIX: Flatten to explicit variants
const variant = featureFlags.getVariant("feature-bundle"); // "a" | "ab" | "abc" | "control"
```

### Flags as Configuration

```typescript
// BAD: Operational params stored as flags
const maxRetries = featureFlags.getVariant("max-retries");
// FIX: Use remote config or env vars for operational parameters
const maxRetries = config.get("maxRetries", 3);
```

## Operational Concerns

### Performance and Caching

```typescript
// Cache flags in memory with background refresh to avoid per-request latency
class CachedFlagClient {
  private cache = new Map<string, { value: any; expiresAt: number }>();
  constructor(private client: FlagClient, private ttl = 30_000) {
    setInterval(() => this.refreshAll(), ttl); // background refresh
  }
  async isEnabled(flag: string, ctx?: FlagContext): Promise<boolean> {
    const c = this.cache.get(flag);
    if (c && c.expiresAt > Date.now()) return c.value;
    return this.evaluate(flag, ctx);
  }
}
```

### Safe Defaults

```typescript
// System must work when flag service is down
const show = await featureFlags.isEnabled("new-feature", context).catch((err) => {
  logger.error("Flag evaluation failed", { flag: "new-feature", err });
  return false; // safe default: feature off
});
```

### Monitoring and Audit

```typescript
// Track evaluations for debugging and alerting
metrics.increment("feature_flag.evaluated", { flag: name, result: String(result) });

// Alert on changes
featureFlags.on("change", (flag, oldVal, newVal) => {
  alerting.notify(`Flag "${flag}" changed: ${oldVal} -> ${newVal}`);
});
```

```sql
-- Audit trail for compliance and debugging
CREATE TABLE flag_audit_log (
  id SERIAL PRIMARY KEY,
  flag_name VARCHAR(100) NOT NULL,
  action VARCHAR(20) NOT NULL,  -- created, updated, deleted, toggled
  old_value JSONB, new_value JSONB,
  changed_by VARCHAR(100) NOT NULL, reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```
