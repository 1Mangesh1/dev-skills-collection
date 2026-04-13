---
name: mongodb
description: MongoDB queries, aggregation, indexing, and administration. Use when user mentions "mongodb", "mongo", "mongosh", "mongoose", "nosql", "document database", "mongodb atlas", "aggregation pipeline", "mongodb query", "collection", "mongodb index", "replica set", "mongodb backup", "mongodump", or working with MongoDB databases.
---

# MongoDB

## mongosh Basics

```bash
# Connect
mongosh                                          # localhost:27017
mongosh "mongodb://localhost:27017/mydb"
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/mydb"
mongosh --host rs0/host1:27017,host2:27017 --authenticationDatabase admin -u admin -p
```

```javascript
show dbs                    // list databases
use mydb                    // switch database (creates on first write)
show collections            // list collections in current db
db.stats()                  // database stats
db.collection.stats()       // collection stats
db.getCollectionNames()     // programmatic collection list
db.dropDatabase()           // drop current database
db.createCollection("logs", { capped: true, size: 1048576, max: 1000 })
```

## CRUD Operations

### Insert

```javascript
db.users.insertOne({ name: "Alice", email: "alice@example.com", age: 30 })
db.users.insertMany([
  { name: "Bob", email: "bob@example.com", age: 25 },
  { name: "Carol", email: "carol@example.com", age: 35 }
])
// insertMany with ordered: false continues on error
db.users.insertMany(docs, { ordered: false })
```

### Find

```javascript
db.users.find()                                    // all documents
db.users.find({ age: { $gt: 25 } })               // age > 25
db.users.findOne({ email: "alice@example.com" })   // first match
db.users.find({ status: "active" }, { name: 1, email: 1, _id: 0 })  // projection
db.users.find().sort({ age: -1 }).limit(10).skip(20)                 // sort, paginate
db.users.countDocuments({ status: "active" })
db.users.distinct("status")
```

### Update

```javascript
db.users.updateOne(
  { email: "alice@example.com" },
  { $set: { age: 31, updatedAt: new Date() } }
)
db.users.updateMany(
  { status: "inactive" },
  { $set: { archived: true }, $currentDate: { updatedAt: true } }
)
// Upsert: insert if not found
db.users.updateOne(
  { email: "dave@example.com" },
  { $set: { name: "Dave", age: 28 } },
  { upsert: true }
)
db.users.replaceOne(
  { _id: ObjectId("...") },
  { name: "Alice", email: "alice@new.com", age: 31 }
)
```

### Delete

```javascript
db.users.deleteOne({ email: "bob@example.com" })
db.users.deleteMany({ status: "inactive", lastLogin: { $lt: ISODate("2024-01-01") } })
db.users.findOneAndDelete({ email: "bob@example.com" })  // returns deleted doc
```

## Query Operators

### Comparison and Logical

```javascript
{ age: { $eq: 30 } }                    // equals (same as { age: 30 })
{ age: { $gt: 25, $lte: 40 } }          // range
{ status: { $in: ["active", "pending"] } }
{ status: { $nin: ["banned"] } }
{ $and: [{ age: { $gte: 18 } }, { status: "active" }] }
{ $or: [{ role: "admin" }, { age: { $gte: 21 } }] }
{ age: { $not: { $gt: 65 } } }
```

### Element and Evaluation

```javascript
{ phone: { $exists: true } }             // field exists
{ age: { $type: "number" } }             // BSON type check
{ name: { $regex: /^alice/i } }          // regex match
{ bio: { $regex: "engineer", $options: "i" } }
{ score: { $mod: [10, 0] } }             // score divisible by 10
```

### Array Operators

```javascript
{ tags: { $all: ["mongodb", "nosql"] } }           // array contains all
{ tags: { $size: 3 } }                              // array has exactly 3 elements
{ results: { $elemMatch: { score: { $gt: 90 }, subject: "math" } } }
{ "scores.0": { $gt: 80 } }                         // first element > 80
```

## Update Operators

```javascript
// Field operators
{ $set: { status: "active" } }
{ $unset: { tempField: "" } }            // remove field
{ $inc: { views: 1, score: -5 } }       // increment/decrement
{ $rename: { "old_field": "new_field" } }
{ $min: { lowScore: 50 } }              // update if new value is lower
{ $max: { highScore: 100 } }            // update if new value is higher
{ $mul: { price: 1.1 } }               // multiply by 1.1

// Array operators
{ $push: { tags: "new-tag" } }
{ $push: { scores: { $each: [90, 85], $sort: -1, $slice: 10 } } }  // push, sort, keep top 10
{ $addToSet: { tags: "unique-tag" } }    // add only if not present
{ $pull: { tags: "old-tag" } }           // remove matching elements
{ $pull: { results: { score: { $lt: 50 } } } }  // remove by condition
{ $pop: { queue: -1 } }                 // remove first element (1 for last)
```

## Aggregation Pipeline

```javascript
db.orders.aggregate([
  { $match: { status: "completed", createdAt: { $gte: ISODate("2025-01-01") } } },
  { $group: {
      _id: "$customerId",
      totalSpent: { $sum: "$amount" },
      orderCount: { $sum: 1 },
      avgOrder: { $avg: "$amount" },
      lastOrder: { $max: "$createdAt" }
  }},
  { $sort: { totalSpent: -1 } },
  { $limit: 10 },
  { $project: {
      customerId: "$_id",
      totalSpent: 1,
      orderCount: 1,
      avgOrder: { $round: ["$avgOrder", 2] },
      _id: 0
  }}
])
```

### $lookup (Join)

```javascript
db.orders.aggregate([
  { $lookup: {
      from: "users",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
  }},
  { $unwind: "$customer" },   // flatten single-element array
  { $project: { amount: 1, "customer.name": 1, "customer.email": 1 } }
])

// Pipeline lookup (correlated subquery)
db.orders.aggregate([
  { $lookup: {
      from: "products",
      let: { productIds: "$items.productId" },
      pipeline: [
        { $match: { $expr: { $in: ["$_id", "$$productIds"] } } },
        { $project: { name: 1, price: 1 } }
      ],
      as: "productDetails"
  }}
])
```

### $facet (Multiple Aggregations in One Pass)

```javascript
db.products.aggregate([
  { $facet: {
      priceRanges: [
        { $bucket: { groupBy: "$price", boundaries: [0, 25, 50, 100, Infinity] } }
      ],
      topRated: [
        { $sort: { rating: -1 } },
        { $limit: 5 },
        { $project: { name: 1, rating: 1 } }
      ],
      totalCount: [
        { $count: "count" }
      ]
  }}
])
```

## Indexing

```javascript
// Single field
db.users.createIndex({ email: 1 })                    // ascending
db.users.createIndex({ email: 1 }, { unique: true })  // unique

// Compound (order matters: equality, sort, range)
db.orders.createIndex({ customerId: 1, createdAt: -1 })

// Multikey (automatically indexes array elements)
db.articles.createIndex({ tags: 1 })

// Text index (one per collection)
db.articles.createIndex({ title: "text", body: "text" })
db.articles.find({ $text: { $search: "mongodb aggregation" } })

// TTL (auto-delete documents after expiry)
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 })

// Partial (index subset of documents)
db.orders.createIndex(
  { createdAt: -1 },
  { partialFilterExpression: { status: "active" } }
)

// Wildcard (index all fields or subfields in a document)
db.logs.createIndex({ "metadata.$**": 1 })

// List and manage indexes
db.users.getIndexes()
db.users.dropIndex("email_1")
db.users.dropIndexes()                                 // drops all non-_id indexes
```

## Schema Design Patterns

### Embedding vs Referencing

```javascript
// Embedding: data accessed together, 1:few relationship
// Good for: addresses in user doc, comments on a blog post (bounded)
{
  _id: ObjectId("..."),
  name: "Alice",
  addresses: [
    { type: "home", street: "123 Main St", city: "Springfield" },
    { type: "work", street: "456 Corp Ave", city: "Shelbyville" }
  ]
}

// Referencing: data accessed independently, 1:many or many:many
// Good for: orders referencing products, users referencing groups
{
  _id: ObjectId("..."),
  customerId: ObjectId("..."),   // reference to users collection
  items: [
    { productId: ObjectId("..."), qty: 2, price: 29.99 }
  ]
}
```

### Denormalization

Store computed or copied fields to avoid joins:

```javascript
// Store author name directly on posts (update on author rename)
{ title: "My Post", authorId: ObjectId("..."), authorName: "Alice" }
```

### Polymorphic Pattern

Single collection, different shapes distinguished by a type field:

```javascript
// notifications collection
{ type: "email", to: "alice@example.com", subject: "Welcome", body: "..." }
{ type: "sms", to: "+1234567890", message: "Your code is 1234" }
{ type: "push", deviceToken: "abc...", title: "New message", payload: { ... } }
```

## Mongoose ODM (Node.js)

### Schema and Model

```javascript
const mongoose = require("mongoose");
await mongoose.connect("mongodb://localhost:27017/mydb");

const userSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true },
  age: { type: Number, min: 0 },
  role: { type: String, enum: ["user", "admin"], default: "user" },
  profile: {
    bio: String,
    avatar: String
  },
  tags: [String],
  createdAt: { type: Date, default: Date.now }
});

// Virtuals
userSchema.virtual("isAdmin").get(function () {
  return this.role === "admin";
});

// Instance methods
userSchema.methods.toPublic = function () {
  const { _id, name, email, role } = this.toObject();
  return { id: _id, name, email, role };
};

// Static methods
userSchema.statics.findByEmail = function (email) {
  return this.findOne({ email: email.toLowerCase() });
};

// Middleware (hooks)
userSchema.pre("save", function (next) {
  this.updatedAt = new Date();
  next();
});

const User = mongoose.model("User", userSchema);
```

### Queries with Mongoose

```javascript
const users = await User.find({ role: "admin" }).sort({ name: 1 }).limit(10).lean();
const user = await User.findById(id).select("name email");
await User.findOneAndUpdate({ email }, { $inc: { loginCount: 1 } }, { new: true });
await User.deleteMany({ lastLogin: { $lt: cutoffDate } });
```

### Populate (Reference Resolution)

```javascript
const postSchema = new mongoose.Schema({
  title: String,
  author: { type: mongoose.Schema.Types.ObjectId, ref: "User" }
});
const Post = mongoose.model("Post", postSchema);

const posts = await Post.find().populate("author", "name email").lean();
// Nested populate
const posts = await Post.find().populate({ path: "comments", populate: { path: "user" } });
```

### lean()

`lean()` returns plain JS objects instead of Mongoose documents. Use for read-only queries -- skips hydration, significantly faster.

## Transactions

```javascript
const session = await mongoose.startSession();
session.startTransaction();
try {
  await Account.updateOne({ _id: from }, { $inc: { balance: -amount } }, { session });
  await Account.updateOne({ _id: to }, { $inc: { balance: amount } }, { session });
  await session.commitTransaction();
} catch (err) {
  await session.abortTransaction();
  throw err;
} finally {
  session.endSession();
}
```

Transactions require a replica set (or sharded cluster). For local dev, start mongod with `--replSet rs0` and run `rs.initiate()`.

## MongoDB Atlas

### Connection

```bash
# Connection string from Atlas dashboard
mongosh "mongodb+srv://cluster0.abc123.mongodb.net/mydb" --apiVersion 1 --username admin

# In application code
mongoose.connect("mongodb+srv://admin:password@cluster0.abc123.mongodb.net/mydb?retryWrites=true&w=majority")
```

### Key Settings

- **Network Access**: whitelist IP addresses or use `0.0.0.0/0` for dev (not production).
- **Database Access**: create users with specific roles (readWrite, atlasAdmin).
- **Backups**: Atlas provides continuous backups and point-in-time restore for M10+ clusters. Snapshots can be downloaded or restored to a new cluster.

## Performance

### explain()

```javascript
db.orders.find({ customerId: ObjectId("...") }).explain("executionStats")
```

Key fields: `totalDocsExamined` vs `nReturned` (ratio should be close to 1:1), `executionTimeMillis`, `winningPlan.stage` (IXSCAN good, COLLSCAN bad), `indexBounds`.

### Database Profiler

```javascript
db.setProfilingLevel(1, { slowms: 100 })     // log queries slower than 100ms
db.system.profile.find().sort({ ts: -1 }).limit(5)
db.setProfilingLevel(0)                       // disable profiler
```

### Index Hints

```javascript
db.orders.find({ status: "active" }).hint({ status: 1, createdAt: -1 })
db.orders.find({ status: "active" }).hint("status_1_createdAt_-1")
```

## Backup and Restore

```bash
# Full database dump
mongodump --uri="mongodb://localhost:27017/mydb" --out=/backup/$(date +%F)

# Specific collection
mongodump --uri="mongodb://localhost:27017/mydb" --collection=users --out=/backup

# Compressed dump
mongodump --uri="mongodb://localhost:27017/mydb" --gzip --archive=backup.gz

# Restore full database
mongorestore --uri="mongodb://localhost:27017" /backup/2025-04-13/

# Restore specific collection
mongorestore --uri="mongodb://localhost:27017/mydb" --collection=users /backup/mydb/users.bson

# Restore from compressed archive
mongorestore --uri="mongodb://localhost:27017" --gzip --archive=backup.gz

# Drop existing data before restoring
mongorestore --drop --uri="mongodb://localhost:27017" /backup/2025-04-13/
```

## Replica Sets

### Setup

```bash
# Start three mongod instances
mongod --replSet rs0 --port 27017 --dbpath /data/rs0-0
mongod --replSet rs0 --port 27018 --dbpath /data/rs0-1
mongod --replSet rs0 --port 27019 --dbpath /data/rs0-2
```

```javascript
// Initiate from mongosh connected to one node
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "localhost:27017" },
    { _id: 1, host: "localhost:27018" },
    { _id: 2, host: "localhost:27019" }
  ]
})
rs.status()
rs.conf()
```

### Read Preference and Write Concern

```javascript
// Read preference: where reads go
// primary (default), primaryPreferred, secondary, secondaryPreferred, nearest
db.users.find().readPref("secondaryPreferred")

// In connection string
"mongodb://host1,host2,host3/mydb?replicaSet=rs0&readPreference=secondaryPreferred"

// Write concern: how many nodes acknowledge a write
db.users.insertOne({ name: "Alice" }, { writeConcern: { w: "majority", wtimeout: 5000 } })
```

## Change Streams

```javascript
// Watch a collection for real-time changes
const changeStream = db.collection("orders").watch();
changeStream.on("change", (change) => {
  console.log(change.operationType, change.fullDocument);
});

// With filters
const pipeline = [{ $match: { "fullDocument.status": "shipped" } }];
const changeStream = db.collection("orders").watch(pipeline, { fullDocument: "updateLookup" });

// Resume after disconnect
const changeStream = db.collection("orders").watch([], { resumeAfter: lastResumeToken });

// Mongoose change streams
const stream = Order.watch();
stream.on("change", (data) => { /* handle */ });
```

Requires replica set or sharded cluster. Use `fullDocument: "updateLookup"` to include the full document on update events.

## Common Patterns

### Cursor-Based Pagination

```javascript
// More efficient than skip/limit for large datasets
const pageSize = 20;
// First page
const firstPage = await db.orders.find().sort({ _id: -1 }).limit(pageSize).toArray();
// Next page: use last _id as cursor
const lastId = firstPage[firstPage.length - 1]._id;
const nextPage = await db.orders.find({ _id: { $lt: lastId } }).sort({ _id: -1 }).limit(pageSize).toArray();
```

### Full-Text Search

```javascript
db.articles.createIndex({ title: "text", body: "text" });
db.articles.find(
  { $text: { $search: "mongodb performance" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Atlas Search (more powerful, uses Lucene)
db.articles.aggregate([
  { $search: { index: "default", text: { query: "mongodb performance", path: ["title", "body"] } } },
  { $project: { title: 1, score: { $meta: "searchScore" } } }
])
```

### Geospatial Queries

```javascript
// Store GeoJSON point
db.places.insertOne({
  name: "Central Park",
  location: { type: "Point", coordinates: [-73.965, 40.782] }  // [lng, lat]
})
db.places.createIndex({ location: "2dsphere" })

// Find within radius (meters)
db.places.find({
  location: { $nearSphere: { $geometry: { type: "Point", coordinates: [-73.97, 40.77] }, $maxDistance: 2000 } }
})

// Find within polygon
db.places.find({
  location: { $geoWithin: { $geometry: { type: "Polygon", coordinates: [[[...], ...]] } } }
})
```
