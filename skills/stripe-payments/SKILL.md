---
name: stripe-payments
description: Stripe integration for payments, subscriptions, and checkout. Use when user mentions "stripe", "payment processing", "checkout", "subscriptions", "stripe webhooks", "payment intent", "stripe CLI", "billing", "stripe elements", or integrating payments into an application.
---

# Stripe Payments

## Setup

### API Keys

Stripe uses two key pairs: publishable (client-side) and secret (server-side).

- Dashboard: https://dashboard.stripe.com/apikeys
- Test keys start with `pk_test_` and `sk_test_`
- Live keys start with `pk_live_` and `sk_live_`
- Store secret keys in environment variables, never in source code
- Restricted keys: create keys with limited permissions for specific services

```bash
export STRIPE_SECRET_KEY="sk_test_..."
export STRIPE_PUBLISHABLE_KEY="pk_test_..."
```

### Install SDKs

```bash
# Node.js
npm install stripe

# Python
pip install stripe
```

### Test Mode

All API calls made with test keys hit the test environment. No real charges occur. Use test mode for development and CI. Switch to live keys only in production.

### Stripe CLI

```bash
# Install
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Listen for webhooks locally
stripe listen --forward-to localhost:4242/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created

# View recent logs
stripe logs tail

# List resources
stripe customers list --limit 5
stripe payments list --limit 5
stripe subscriptions list --limit 3

# Create resources from CLI
stripe customers create --email="test@example.com"
stripe prices create --unit-amount=2000 --currency=usd --recurring[interval]=month --product=prod_xxx
```

## Checkout Sessions

### One-Time Payment

```js
const session = await stripe.checkout.sessions.create({
  mode: 'payment',
  line_items: [{
    price_data: {
      currency: 'usd',
      product_data: { name: 'Widget' },
      unit_amount: 2000, // $20.00 in cents
    },
    quantity: 1,
  }],
  success_url: 'https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://example.com/cancel',
});
```

### Subscription Checkout

```js
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  line_items: [{ price: 'price_xxx', quantity: 1 }],
  success_url: 'https://example.com/success',
  cancel_url: 'https://example.com/cancel',
  customer: 'cus_xxx', // optional, attach to existing customer
});
```

### Embedded Checkout

```js
// Server
const session = await stripe.checkout.sessions.create({
  mode: 'payment',
  ui_mode: 'embedded',
  line_items: [{ price: 'price_xxx', quantity: 1 }],
  return_url: 'https://example.com/return?session_id={CHECKOUT_SESSION_ID}',
});
// Return session.client_secret to the frontend
```

## Payment Intents

### Create and Confirm

```js
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000,
  currency: 'usd',
  payment_method: 'pm_card_visa',
  confirm: true,
  automatic_payment_methods: { enabled: true, allow_redirects: 'never' },
});
```

### Manual Capture (authorize then capture)

```js
const intent = await stripe.paymentIntents.create({
  amount: 5000,
  currency: 'usd',
  capture_method: 'manual',
});
// Later, capture the authorized amount
await stripe.paymentIntents.capture(intent.id);
```

## Customers

```js
// Create
const customer = await stripe.customers.create({
  email: 'user@example.com',
  name: 'Jane Doe',
  metadata: { user_id: '123' },
});

// Update
await stripe.customers.update('cus_xxx', { name: 'Jane Smith' });

// Attach a payment method
await stripe.paymentMethods.attach('pm_xxx', { customer: 'cus_xxx' });

// Set default payment method
await stripe.customers.update('cus_xxx', {
  invoice_settings: { default_payment_method: 'pm_xxx' },
});
```

## Subscriptions

### Create

```js
const subscription = await stripe.subscriptions.create({
  customer: 'cus_xxx',
  items: [{ price: 'price_xxx' }],
  default_payment_method: 'pm_xxx',
  payment_behavior: 'default_incomplete',
  expand: ['latest_invoice.payment_intent'],
});
```

### Update, Cancel, Trials

```js
// Change plan (proration handled automatically)
await stripe.subscriptions.update('sub_xxx', {
  items: [{ id: 'si_xxx', price: 'price_new' }],
  proration_behavior: 'create_prorations',
});

// Cancel at period end
await stripe.subscriptions.update('sub_xxx', { cancel_at_period_end: true });

// Cancel immediately
await stripe.subscriptions.cancel('sub_xxx');

// Trial period
await stripe.subscriptions.create({
  customer: 'cus_xxx',
  items: [{ price: 'price_xxx' }],
  trial_period_days: 14,
});
```

### Metered Billing

```js
// Report usage for a metered price
await stripe.subscriptionItems.createUsageRecord('si_xxx', {
  quantity: 100,
  timestamp: Math.floor(Date.now() / 1000),
  action: 'increment', // or 'set'
});
```

## Webhooks

### Setup (Node.js / Express)

```js
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET;

app.post('/webhook', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  switch (event.type) {
    case 'checkout.session.completed':
      handleCheckoutComplete(event.data.object);
      break;
    case 'invoice.paid':
      handleInvoicePaid(event.data.object);
      break;
    case 'customer.subscription.deleted':
      handleSubscriptionCanceled(event.data.object);
      break;
  }
  res.json({ received: true });
});
```

### Common Events

- `checkout.session.completed` -- payment or subscription checkout finished
- `payment_intent.succeeded` -- payment confirmed
- `payment_intent.payment_failed` -- payment declined
- `invoice.paid` -- subscription invoice paid
- `invoice.payment_failed` -- subscription payment failed
- `customer.subscription.created` -- new subscription
- `customer.subscription.updated` -- plan change, trial end, etc.
- `customer.subscription.deleted` -- subscription canceled

### Retry Logic

Stripe retries failed webhook deliveries over 72 hours with exponential backoff. Return 2xx quickly. Process long-running work asynchronously. Use idempotency checks to handle duplicate deliveries.

## Products and Prices

```js
// Create a product
const product = await stripe.products.create({
  name: 'Pro Plan',
  description: 'Full access to all features',
});

// One-time price
await stripe.prices.create({
  product: product.id,
  unit_amount: 4999,
  currency: 'usd',
});

// Recurring price
await stripe.prices.create({
  product: product.id,
  unit_amount: 1999,
  currency: 'usd',
  recurring: { interval: 'month' },
});

// Metered price
await stripe.prices.create({
  product: product.id,
  currency: 'usd',
  recurring: { interval: 'month', usage_type: 'metered' },
  billing_scheme: 'per_unit',
  unit_amount: 10, // $0.10 per unit
});
```

## Stripe Elements

### Payment Element (recommended)

```js
// Client-side
const stripe = Stripe('pk_test_...');
const elements = stripe.elements({
  clientSecret: 'pi_xxx_secret_xxx',
  appearance: {
    theme: 'stripe', // 'stripe', 'night', 'flat'
    variables: { colorPrimary: '#0570de' },
  },
});
const paymentElement = elements.create('payment');
paymentElement.mount('#payment-element');

// On form submit
const { error } = await stripe.confirmPayment({
  elements,
  confirmParams: { return_url: 'https://example.com/complete' },
});
```

### Card Element (legacy, simpler)

```js
const cardElement = elements.create('card');
cardElement.mount('#card-element');

const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
  payment_method: { card: cardElement },
});
```

## Refunds

```js
// Full refund
await stripe.refunds.create({ payment_intent: 'pi_xxx' });

// Partial refund
await stripe.refunds.create({ payment_intent: 'pi_xxx', amount: 500 });

// With reason
await stripe.refunds.create({
  payment_intent: 'pi_xxx',
  reason: 'requested_by_customer', // or 'duplicate', 'fraudulent'
});
```

## Invoices

```js
// Create a draft invoice
const invoice = await stripe.invoices.create({ customer: 'cus_xxx' });

// Add line items
await stripe.invoiceItems.create({
  customer: 'cus_xxx',
  invoice: invoice.id,
  amount: 2500,
  currency: 'usd',
  description: 'Consulting (1 hour)',
});

// Finalize
await stripe.invoices.finalizeInvoice(invoice.id);

// Send to customer
await stripe.invoices.sendInvoice(invoice.id);

// Pay an invoice directly
await stripe.invoices.pay(invoice.id);
```

## Python Integration

```python
import stripe
stripe.api_key = "sk_test_..."

# Checkout session
session = stripe.checkout.Session.create(
    mode="payment",
    line_items=[{"price": "price_xxx", "quantity": 1}],
    success_url="https://example.com/success",
    cancel_url="https://example.com/cancel",
)

# Payment intent
intent = stripe.PaymentIntent.create(amount=2000, currency="usd")

# Customer
customer = stripe.Customer.create(email="user@example.com")

# Webhook verification (Flask)
import flask
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = flask.request.data
    sig = flask.request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400
    if event["type"] == "payment_intent.succeeded":
        handle_payment(event["data"]["object"])
    return "", 200
```

## Testing

### Test Card Numbers

| Card              | Number             | Behavior             |
|-------------------|--------------------|----------------------|
| Visa (success)    | 4242424242424242   | Succeeds             |
| Visa (decline)    | 4000000000000002   | Generic decline      |
| Auth required     | 4000002500003155   | Requires 3DS         |
| Insufficient      | 4000000000009995   | Insufficient funds   |
| Expired           | 4000000000000069   | Expired card         |

Use any future expiry date, any 3-digit CVC, and any postal code.

### Test Clocks (Subscriptions)

```js
// Create a test clock to simulate time progression
const clock = await stripe.testHelpers.testClocks.create({
  frozen_time: Math.floor(Date.now() / 1000),
});

// Create a customer attached to the test clock
const customer = await stripe.customers.create({
  email: 'test@example.com',
  test_clock: clock.id,
});

// Advance time to trigger renewals, trial ends, etc.
await stripe.testHelpers.testClocks.advance(clock.id, {
  frozen_time: Math.floor(Date.now() / 1000) + 86400 * 32, // +32 days
});
```

## Error Handling

### Decline Codes

Handle `err.code` values: `card_declined`, `expired_card`, `incorrect_cvc`, `processing_error`, `insufficient_funds`. Display user-friendly messages; do not expose raw error details.

### Idempotency Keys

```js
await stripe.paymentIntents.create(
  { amount: 2000, currency: 'usd' },
  { idempotencyKey: 'order_123' }
);
```

Use idempotency keys for any create or update operation to prevent duplicate charges on retries. Keys expire after 24 hours.

### General Error Pattern

```js
try {
  await stripe.paymentIntents.create({ amount: 2000, currency: 'usd' });
} catch (err) {
  if (err.type === 'StripeCardError') {
    // Card was declined
  } else if (err.type === 'StripeInvalidRequestError') {
    // Invalid parameters
  } else if (err.type === 'StripeAPIError') {
    // Stripe-side issue, retry with backoff
  } else if (err.type === 'StripeRateLimitError') {
    // Too many requests, retry with backoff
  }
}
```

## Common Patterns

### SaaS Billing

1. Create product and recurring prices for each tier.
2. Use Checkout in subscription mode or create subscriptions directly.
3. Listen for `invoice.paid` and `customer.subscription.updated` webhooks to provision/deprovision access.
4. Handle upgrades/downgrades via `subscriptions.update` with proration.
5. Use `cancel_at_period_end` for graceful cancellation.

### One-Time Purchase

1. Create a Checkout Session in payment mode.
2. On `checkout.session.completed`, fulfill the order.
3. Store the `payment_intent` ID for refund reference.

### Marketplace (Connect)

1. Create connected accounts with `stripe.accounts.create({ type: 'express' })`.
2. Use `payment_intents` with `transfer_data` or `on_behalf_of`.
3. Take platform fees via `application_fee_amount`.
4. Handle payouts to connected accounts.

### Usage-Based Billing

1. Create a metered price with `recurring.usage_type: 'metered'`.
2. Create a subscription with the metered price.
3. Report usage via `subscriptionItems.createUsageRecord`.
4. Stripe invoices at the end of each billing period based on reported usage.
