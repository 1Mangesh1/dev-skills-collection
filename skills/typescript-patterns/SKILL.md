---
name: typescript-patterns
description: TypeScript patterns, advanced typing, and type safety. Use when user asks to "write TypeScript generics", "create utility types", "fix TypeScript errors", "type a complex object", "use conditional types", "create type guards", "improve TypeScript types", "design type-safe APIs", "use mapped types", "create branded types", "infer types", "type narrowing", "type variance", "overload signatures", "type assertion", or mentions TypeScript patterns, advanced typing, generic constraints, discriminated unions, template literal types, or type inference.
license: MIT
metadata:
  author: 1mangesh1
  version: "1.0.0"
  tags:
    - typescript
    - types
    - generics
    - utility-types
    - type-safety
    - patterns
---

# Advanced TypeScript Patterns

Production-grade TypeScript patterns for building type-safe, maintainable, and scalable applications. This skill covers generics, utility types, conditional types, discriminated unions, branded types, and more.

---

## 1. Advanced Generics with Constraints

### Basic Generic Constraints

```typescript
// Constrain T to objects that have a .length property
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

getLength("hello");       // OK - string has .length
getLength([1, 2, 3]);     // OK - array has .length
// getLength(42);          // Error - number has no .length
```

### Multiple Constraints with Intersection

```typescript
interface HasId {
  id: string;
}

interface HasTimestamp {
  createdAt: Date;
  updatedAt: Date;
}

// T must satisfy both interfaces
function updateEntity<T extends HasId & HasTimestamp>(
  entity: T,
  updates: Partial<Omit<T, "id" | "createdAt">>
): T {
  return { ...entity, ...updates, updatedAt: new Date() };
}
```

### keyof Constraint Pattern

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 30, email: "alice@example.com" };
const name = getProperty(user, "name");   // type: string
const age = getProperty(user, "age");     // type: number
// getProperty(user, "phone");            // Error: "phone" not in keyof user
```

### Generic Factory Pattern

```typescript
interface Constructor<T> {
  new (...args: any[]): T;
}

function createInstance<T>(ctor: Constructor<T>, ...args: any[]): T {
  return new ctor(...args);
}

class UserService {
  constructor(public apiUrl: string) {}
}

const service = createInstance(UserService, "https://api.example.com");
// service is typed as UserService
```

---

## 2. Built-in Utility Types

### Pick, Omit, Partial, Required

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: "admin" | "user" | "moderator";
  preferences: {
    theme: "light" | "dark";
    notifications: boolean;
  };
}

// Pick only the fields you need
type UserSummary = Pick<User, "id" | "name" | "avatar">;

// Omit sensitive fields
type PublicUser = Omit<User, "email" | "preferences">;

// Make all fields optional (useful for update payloads)
type UserUpdate = Partial<Omit<User, "id">>;

// Make optional fields required
type CompleteUser = Required<User>;
// avatar is now required
```

### Record, Extract, Exclude

```typescript
// Record: create an object type with known keys
type UserRole = "admin" | "user" | "moderator";

type RolePermissions = Record<UserRole, string[]>;

const permissions: RolePermissions = {
  admin: ["read", "write", "delete", "manage-users"],
  user: ["read", "write"],
  moderator: ["read", "write", "delete"],
};

// Extract: pull types from a union that match
type NumericEvent = Extract<"click" | "scroll" | "keypress" | 42, string>;
// Result: "click" | "scroll" | "keypress"

// Exclude: remove types from a union
type NonAdminRole = Exclude<UserRole, "admin">;
// Result: "user" | "moderator"
```

### ReturnType, Parameters, InstanceType

```typescript
function fetchUser(id: string, options?: { includeProfile: boolean }) {
  return { id, name: "Alice", email: "alice@example.com" };
}

type FetchUserReturn = ReturnType<typeof fetchUser>;
// { id: string; name: string; email: string }

type FetchUserParams = Parameters<typeof fetchUser>;
// [id: string, options?: { includeProfile: boolean }]

class ApiClient {
  baseUrl: string;
  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }
}

type ApiClientInstance = InstanceType<typeof ApiClient>;
// ApiClient
```

---

## 3. Conditional Types and the `infer` Keyword

### Basic Conditional Types

```typescript
type IsString<T> = T extends string ? true : false;

type A = IsString<"hello">;  // true
type B = IsString<42>;       // false
```

### Extracting Types with `infer`

```typescript
// Extract the return type of a promise
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;

type Result = UnwrapPromise<Promise<string>>;  // string
type Plain = UnwrapPromise<number>;            // number

// Extract element type from an array
type ElementOf<T> = T extends (infer E)[] ? E : never;

type Item = ElementOf<string[]>;   // string
type Nested = ElementOf<number[]>; // number

// Extract function arguments
type FirstArg<T> = T extends (first: infer F, ...rest: any[]) => any ? F : never;

type Arg = FirstArg<(name: string, age: number) => void>; // string
```

### Distributive Conditional Types

```typescript
// Conditional types distribute over unions automatically
type ToArray<T> = T extends any ? T[] : never;

type Result = ToArray<string | number>;
// string[] | number[]  (NOT (string | number)[])

// Prevent distribution with wrapping in tuple
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;

type Result2 = ToArrayNonDist<string | number>;
// (string | number)[]
```

### Recursive Conditional Types

```typescript
// Deeply unwrap nested promises
type DeepUnwrap<T> = T extends Promise<infer U> ? DeepUnwrap<U> : T;

type Deep = DeepUnwrap<Promise<Promise<Promise<string>>>>; // string

// Deep partial - make all nested properties optional
type DeepPartial<T> = T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;

interface Config {
  server: {
    host: string;
    port: number;
    ssl: {
      enabled: boolean;
      cert: string;
    };
  };
}

type PartialConfig = DeepPartial<Config>;
// All nested fields are now optional
```

---

## 4. Mapped Types and Template Literal Types

### Custom Mapped Types

```typescript
// Make all properties readonly
type Immutable<T> = {
  readonly [K in keyof T]: T[K] extends object ? Immutable<T[K]> : T[K];
};

// Make all properties nullable
type Nullable<T> = {
  [K in keyof T]: T[K] | null;
};

// Add a prefix to all keys
type Prefixed<T, P extends string> = {
  [K in keyof T as `${P}${Capitalize<string & K>}`]: T[K];
};

interface FormData {
  name: string;
  email: string;
}

type OnChangeHandlers = Prefixed<FormData, "onChange">;
// { onChangeName: string; onChangeEmail: string }
```

### Template Literal Types

```typescript
type HTTPMethod = "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
type APIVersion = "v1" | "v2";
type Resource = "users" | "posts" | "comments";

// Generate all route combinations
type APIRoute = `/${APIVersion}/${Resource}`;
// "/v1/users" | "/v1/posts" | "/v1/comments" | "/v2/users" | ...

// Event handler types
type DOMEvent = "click" | "focus" | "blur" | "input";
type EventHandler = `on${Capitalize<DOMEvent>}`;
// "onClick" | "onFocus" | "onBlur" | "onInput"

// CSS unit types
type CSSUnit = "px" | "rem" | "em" | "vh" | "vw" | "%";
type CSSValue = `${number}${CSSUnit}`;

const width: CSSValue = "100px";   // OK
const height: CSSValue = "50vh";   // OK
// const bad: CSSValue = "auto";   // Error
```

### Key Remapping with `as`

```typescript
// Create getter functions for each property
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters<Person>;
// { getName: () => string; getAge: () => number }

// Filter keys by value type
type StringKeysOnly<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

interface Mixed {
  name: string;
  age: number;
  email: string;
  active: boolean;
}

type OnlyStrings = StringKeysOnly<Mixed>;
// { name: string; email: string }
```

---

## 5. Discriminated Unions and Exhaustive Checking

### Basic Discriminated Union

```typescript
interface LoadingState {
  status: "loading";
}

interface SuccessState<T> {
  status: "success";
  data: T;
}

interface ErrorState {
  status: "error";
  error: {
    message: string;
    code: number;
  };
}

type RequestState<T> = LoadingState | SuccessState<T> | ErrorState;

function renderState<T>(state: RequestState<T>): string {
  switch (state.status) {
    case "loading":
      return "Loading...";
    case "success":
      return `Data: ${JSON.stringify(state.data)}`;
    case "error":
      return `Error ${state.error.code}: ${state.error.message}`;
  }
}
```

### Exhaustive Checking with `never`

```typescript
// This function ensures all union variants are handled at compile time
function assertNever(value: never): never {
  throw new Error(`Unhandled discriminated union member: ${JSON.stringify(value)}`);
}

type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return (shape.base * shape.height) / 2;
    default:
      // If a new variant is added to Shape but not handled here,
      // TypeScript will produce a compile error on this line.
      return assertNever(shape);
  }
}
```

### Action/Event Pattern (Redux-style)

```typescript
type Action =
  | { type: "ADD_TODO"; payload: { text: string } }
  | { type: "TOGGLE_TODO"; payload: { id: number } }
  | { type: "REMOVE_TODO"; payload: { id: number } }
  | { type: "SET_FILTER"; payload: { filter: "all" | "active" | "completed" } };

interface TodoState {
  todos: Array<{ id: number; text: string; completed: boolean }>;
  filter: "all" | "active" | "completed";
}

function todoReducer(state: TodoState, action: Action): TodoState {
  switch (action.type) {
    case "ADD_TODO":
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: Date.now(), text: action.payload.text, completed: false },
        ],
      };
    case "TOGGLE_TODO":
      return {
        ...state,
        todos: state.todos.map((t) =>
          t.id === action.payload.id ? { ...t, completed: !t.completed } : t
        ),
      };
    case "REMOVE_TODO":
      return {
        ...state,
        todos: state.todos.filter((t) => t.id !== action.payload.id),
      };
    case "SET_FILTER":
      return { ...state, filter: action.payload.filter };
    default:
      return assertNever(action as never);
  }
}
```

---

## 6. Type Guards and Type Narrowing

### Custom Type Guard Functions

```typescript
interface Cat {
  type: "cat";
  purrs: boolean;
}

interface Dog {
  type: "dog";
  barks: boolean;
}

type Animal = Cat | Dog;

// Type predicate: `animal is Cat`
function isCat(animal: Animal): animal is Cat {
  return animal.type === "cat";
}

function handleAnimal(animal: Animal) {
  if (isCat(animal)) {
    console.log(animal.purrs); // TypeScript knows this is Cat
  } else {
    console.log(animal.barks); // TypeScript knows this is Dog
  }
}
```

### Assertion Functions

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

function processInput(input: unknown) {
  assertIsString(input);
  // After assertion, TypeScript knows input is string
  console.log(input.toUpperCase());
}
```

### `in` Operator Narrowing

```typescript
interface APIResponse {
  data: unknown;
}

interface APIError {
  error: string;
  statusCode: number;
}

function handleResponse(res: APIResponse | APIError) {
  if ("error" in res) {
    // TypeScript narrows to APIError
    console.error(`Error ${res.statusCode}: ${res.error}`);
  } else {
    // TypeScript narrows to APIResponse
    console.log(res.data);
  }
}
```

### Narrowing with `satisfies`

```typescript
// satisfies validates the type without widening it
type Color = "red" | "green" | "blue";
type ColorMap = Record<Color, string | [number, number, number]>;

const palette = {
  red: [255, 0, 0],
  green: "#00ff00",
  blue: [0, 0, 255],
} satisfies ColorMap;

// palette.red is inferred as [number, number, number], not string | [number, number, number]
const redChannel = palette.red[0]; // OK - TypeScript knows it is a tuple
```

---

## 7. Branded / Opaque Types for Type Safety

### Preventing Primitive Type Confusion

```typescript
// Brand type utility
type Brand<T, B extends string> = T & { readonly __brand: B };

type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;
type Email = Brand<string, "Email">;

// Constructor functions with validation
function createUserId(id: string): UserId {
  if (!id.match(/^usr_[a-zA-Z0-9]{12}$/)) {
    throw new Error("Invalid user ID format");
  }
  return id as UserId;
}

function createEmail(email: string): Email {
  if (!email.includes("@")) {
    throw new Error("Invalid email format");
  }
  return email as Email;
}

function sendEmail(to: Email, subject: string): void {
  // ...
}

function getUser(id: UserId): void {
  // ...
}

const userId = createUserId("usr_abc123def456");
const email = createEmail("alice@example.com");

sendEmail(email, "Welcome!");  // OK
// sendEmail(userId, "Welcome!"); // Error: UserId is not assignable to Email
// getUser(email);                // Error: Email is not assignable to UserId
```

### Branded Numeric Types

```typescript
type Celsius = Brand<number, "Celsius">;
type Fahrenheit = Brand<number, "Fahrenheit">;
type Kilometers = Brand<number, "Kilometers">;
type Miles = Brand<number, "Miles">;

function celsiusToFahrenheit(c: Celsius): Fahrenheit {
  return ((c * 9) / 5 + 32) as Fahrenheit;
}

function milesToKilometers(m: Miles): Kilometers {
  return (m * 1.60934) as Kilometers;
}

const temp = 100 as Celsius;
const converted = celsiusToFahrenheit(temp); // Fahrenheit
// celsiusToFahrenheit(100 as Fahrenheit);   // Error: type mismatch
```

---

## 8. Builder Pattern with Types

### Type-Safe Builder

```typescript
interface QueryConfig {
  table: string;
  columns: string[];
  where: string[];
  orderBy: string | null;
  limit: number | null;
}

type RequiredFields = "table" | "columns";

class QueryBuilder<T extends Partial<QueryConfig> = {}> {
  private config: Partial<QueryConfig> = {};

  from<Table extends string>(
    table: Table
  ): QueryBuilder<T & { table: Table }> {
    this.config.table = table;
    return this as any;
  }

  select(
    ...columns: string[]
  ): QueryBuilder<T & { columns: string[] }> {
    this.config.columns = columns;
    return this as any;
  }

  where(condition: string): QueryBuilder<T & { where: string[] }> {
    this.config.where = [...(this.config.where ?? []), condition];
    return this as any;
  }

  orderBy(column: string): this {
    this.config.orderBy = column;
    return this;
  }

  limit(count: number): this {
    this.config.limit = count;
    return this;
  }

  // Only available when required fields are set
  build(
    this: QueryBuilder<Pick<QueryConfig, RequiredFields>>
  ): QueryConfig {
    return {
      table: this.config.table!,
      columns: this.config.columns!,
      where: this.config.where ?? [],
      orderBy: this.config.orderBy ?? null,
      limit: this.config.limit ?? null,
    };
  }
}

// Usage
const query = new QueryBuilder()
  .from("users")
  .select("id", "name", "email")
  .where("active = true")
  .orderBy("name")
  .limit(10)
  .build(); // Only compiles because from() and select() were called
```

---

## 9. Runtime Validation with Zod

### Schema Definition and Inference

```typescript
import { z } from "zod";

// Define schema
const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150).optional(),
  role: z.enum(["admin", "user", "moderator"]),
  tags: z.array(z.string()).default([]),
  metadata: z.record(z.string(), z.unknown()).optional(),
  createdAt: z.coerce.date(),
});

// Infer the TypeScript type from the schema
type User = z.infer<typeof UserSchema>;
// {
//   id: string;
//   name: string;
//   email: string;
//   age?: number;
//   role: "admin" | "user" | "moderator";
//   tags: string[];
//   metadata?: Record<string, unknown>;
//   createdAt: Date;
// }

// Validate at runtime
function createUser(input: unknown): User {
  return UserSchema.parse(input); // throws ZodError if invalid
}

// Safe parsing (no throw)
function tryCreateUser(input: unknown): User | null {
  const result = UserSchema.safeParse(input);
  if (result.success) {
    return result.data;
  }
  console.error("Validation errors:", result.error.flatten());
  return null;
}
```

### API Request/Response Validation

```typescript
const CreateUserRequest = UserSchema.omit({ id: true, createdAt: true });
const UpdateUserRequest = CreateUserRequest.partial();

const APIResponse = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema,
    meta: z
      .object({
        page: z.number(),
        total: z.number(),
      })
      .optional(),
  });

const UserListResponse = APIResponse(z.array(UserSchema));
type UserListResponse = z.infer<typeof UserListResponse>;
```

---

## 10. Common TypeScript Errors and Fixes

### TS2322: Type 'X' is not assignable to type 'Y'

```typescript
// Problem
const status: "active" | "inactive" = "active";
let mutable = status;
// mutable is inferred as string, not the literal type

// Fix: use const assertion or explicit type
let mutable: typeof status = status;
// OR
const statuses = ["active", "inactive"] as const;
type Status = (typeof statuses)[number]; // "active" | "inactive"
```

### TS2345: Argument of type 'X' is not assignable to parameter of type 'Y'

```typescript
// Problem: passing an object literal with extra properties
interface Options {
  timeout: number;
}

function configure(opts: Options) {}

// Fix: use a variable (excess property check only applies to literals)
const opts = { timeout: 5000, retries: 3 };
configure(opts); // OK - no excess property check on variables
```

### TS7053: Element implicitly has an 'any' type (index access)

```typescript
// Problem
const config: Record<string, unknown> = {};
const value = config["key"]; // unknown

// Fix: use a type guard or assertion
function getString(obj: Record<string, unknown>, key: string): string {
  const val = obj[key];
  if (typeof val !== "string") {
    throw new Error(`Expected string at key "${key}"`);
  }
  return val;
}
```

### TS2339: Property does not exist on type

```typescript
// Problem with union types
type Result = { ok: true; value: string } | { ok: false; error: string };

function handle(result: Result) {
  // result.value  // Error: property doesn't exist on { ok: false; ... }

  // Fix: narrow the type first
  if (result.ok) {
    console.log(result.value); // OK after narrowing
  } else {
    console.log(result.error);
  }
}
```

---

## 11. Declaration Merging and Module Augmentation

### Interface Merging

```typescript
// Extend a third-party library's types
declare module "express" {
  interface Request {
    user?: {
      id: string;
      role: string;
    };
    requestId: string;
  }
}

// Now express Request has your custom fields
import { Request } from "express";
function handler(req: Request) {
  console.log(req.user?.id);     // OK
  console.log(req.requestId);    // OK
}
```

### Global Augmentation

```typescript
// Add custom properties to globalThis
declare global {
  interface Window {
    __APP_CONFIG__: {
      apiUrl: string;
      environment: "development" | "staging" | "production";
    };
  }

  // Add utility to Array prototype (declaration only)
  interface Array<T> {
    groupBy<K extends string>(fn: (item: T) => K): Record<K, T[]>;
  }
}

export {}; // Required to make this a module
```

### Namespace Merging

```typescript
// Merge a namespace with a function (overloaded module pattern)
function currency(amount: number): string;
function currency(amount: number, code: string): string;
function currency(amount: number, code?: string): string {
  return `${(code ?? "USD")} ${amount.toFixed(2)}`;
}

namespace currency {
  export const codes = ["USD", "EUR", "GBP", "JPY"] as const;
  export type Code = (typeof codes)[number];
  export function convert(amount: number, from: Code, to: Code): number {
    // conversion logic
    return amount;
  }
}

currency(42);                       // "USD 42.00"
currency.convert(100, "USD", "EUR"); // uses namespace
```

---

## 12. Strict Mode Best Practices

### Recommended tsconfig.json Strict Settings

```jsonc
{
  "compilerOptions": {
    // Enable all strict checks
    "strict": true,

    // Individual flags (all enabled by "strict": true)
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,

    // Additional strictness beyond "strict"
    "noUncheckedIndexedAccess": true,   // arr[0] is T | undefined
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,

    // Module and target
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "target": "ES2022",
    "lib": ["ES2022"],

    // Output
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

### Handling Strict Null Checks

```typescript
// With strictNullChecks enabled
function getUser(id: string): User | undefined {
  return users.get(id);
}

// Option 1: Early return guard
function getUserName(id: string): string {
  const user = getUser(id);
  if (!user) {
    throw new Error(`User ${id} not found`);
  }
  return user.name; // user is narrowed to User
}

// Option 2: Non-null assertion (use sparingly, only when you are certain)
function unsafeGetName(id: string): string {
  return getUser(id)!.name;
}

// Option 3: Optional chaining with nullish coalescing
function safeGetName(id: string): string {
  return getUser(id)?.name ?? "Anonymous";
}
```

### noUncheckedIndexedAccess Pattern

```typescript
// With noUncheckedIndexedAccess, array/record access returns T | undefined
const items: string[] = ["a", "b", "c"];
const first = items[0]; // string | undefined

// Guard before use
if (first !== undefined) {
  console.log(first.toUpperCase()); // OK
}

// Or use a helper
function at<T>(arr: T[], index: number): T {
  const item = arr[index];
  if (item === undefined) {
    throw new RangeError(`Index ${index} out of bounds`);
  }
  return item;
}
```

---

## Quick Reference: When to Use What

| Pattern | Use Case |
|---|---|
| **Generics** | Reusable functions/classes that work with multiple types |
| **Utility types** | Transform existing types (pick fields, make optional, etc.) |
| **Conditional types** | Types that depend on other types at compile time |
| **Mapped types** | Transform all properties of a type systematically |
| **Template literals** | Generate string literal union types |
| **Discriminated unions** | Model states, events, actions with tagged variants |
| **Type guards** | Runtime checks that narrow types for the compiler |
| **Branded types** | Prevent mixing up primitives (UserId vs OrderId) |
| **Builder pattern** | Enforce required steps at compile time |
| **Zod schemas** | Runtime validation with automatic type inference |
| **Declaration merging** | Extend third-party or global types |
| **Strict mode** | Catch more bugs at compile time |

---

## References

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/)
- [TypeScript Deep Dive](https://basarat.gitbook.io/typescript/)
- [Type Challenges](https://github.com/type-challenges/type-challenges)
- [Zod Documentation](https://zod.dev/)
- [Total TypeScript](https://www.totaltypescript.com/)
