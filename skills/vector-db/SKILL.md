---
name: vector-db
description: Vector databases for embeddings, semantic search, and RAG pipelines. Use when user mentions "vector database", "embeddings", "semantic search", "RAG", "retrieval augmented generation", "pinecone", "chromadb", "pgvector", "qdrant", "weaviate", "similarity search", "embedding store", or building AI search features.
---

# Vector Databases

## What Vector Databases Do

Vector databases store high-dimensional numerical representations (embeddings) and enable fast similarity search. Unlike traditional databases that match exact values, vector databases find the closest vectors to a query vector, enabling semantic matching.

Core capabilities:
- Store embeddings alongside metadata and original content
- Perform approximate nearest neighbor (ANN) search at scale
- Filter results by metadata combined with vector similarity
- Handle millions to billions of vectors with sub-second query times

## Embedding Basics

An embedding is a fixed-length array of floats capturing semantic meaning. Text with similar meaning produces vectors that are close together in the embedding space.

- **Dimensions**: Vector length. Common sizes: 384, 768, 1536, 3072. Higher = more nuance, more cost.
- **Embedding model**: Converts raw data into vectors. Different models produce different dimensions.
- **Distance metric**: How similarity between two vectors is measured.

## Generating Embeddings

### OpenAI

```python
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(
    input="What is a vector database?",
    model="text-embedding-3-small"  # 1536 dimensions
)
vector = response.data[0].embedding
```

### Sentence-Transformers (Local)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dimensions
vectors = model.encode(["What is a vector database?", "How does search work?"])
```

### Cohere

```python
import cohere
co = cohere.Client("your-api-key")
response = co.embed(
    texts=["What is a vector database?"],
    model="embed-english-v3.0",
    input_type="search_document"  # Use "search_query" for queries
)
vector = response.embeddings[0]
```

## ChromaDB (Local, Python)

Lightweight, embedded vector database. Good for prototyping and small-to-medium workloads.

```bash
pip install chromadb
```

```python
import chromadb

client = chromadb.Client()  # In-memory
# client = chromadb.PersistentClient(path="./chroma_data")  # Persistent

collection = client.create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}  # cosine, l2, or ip
)

# Add documents (ChromaDB auto-generates embeddings with its default model)
collection.add(
    ids=["doc1", "doc2", "doc3"],
    documents=[
        "Vector databases store embeddings",
        "PostgreSQL is a relational database",
        "Semantic search finds similar meaning"
    ],
    metadatas=[
        {"source": "wiki", "topic": "vectors"},
        {"source": "docs", "topic": "sql"},
        {"source": "wiki", "topic": "search"}
    ]
)

# Query
results = collection.query(
    query_texts=["How do vector stores work?"],
    n_results=2,
    where={"source": "wiki"}  # Optional metadata filter
)
# results["documents"], results["distances"], results["metadatas"]
```

To use pre-computed embeddings, pass `embeddings=[[...]]` instead of `documents` in both `add()` and `query()` (via `query_embeddings`).

## pgvector (PostgreSQL Extension)

Adds vector column type and similarity operators to PostgreSQL. Use when you already run Postgres and want vectors alongside relational data.

### Setup and Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexing

```sql
-- HNSW index (recommended)
CREATE INDEX ON documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- IVFFlat index (faster to build, slower to query)
CREATE INDEX ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

Operator classes: `vector_cosine_ops` (`<=>`), `vector_l2_ops` (`<->`), `vector_ip_ops` (`<#>`).

### Query

```sql
SELECT id, content, 1 - (embedding <=> $1::vector) AS similarity
FROM documents
WHERE metadata->>'category' = 'technical'
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

Python: use `psycopg` with `pgvector.psycopg.register_vector(conn)` to pass vectors directly as parameters.

## Pinecone (Managed Cloud)

Fully managed vector database. No infrastructure to maintain. Supports namespaces for logical partitioning.

```bash
pip install pinecone
```

```python
from pinecone import Pinecone

pc = Pinecone(api_key="your-api-key")

pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",  # cosine, euclidean, dotproduct
    spec={"serverless": {"cloud": "aws", "region": "us-east-1"}}
)

index = pc.Index("my-index")

# Upsert vectors
index.upsert(
    vectors=[
        {"id": "doc1", "values": [0.1, 0.2, ...],
         "metadata": {"source": "wiki", "topic": "databases"}},
        {"id": "doc2", "values": [0.3, 0.4, ...],
         "metadata": {"source": "blog", "topic": "search"}}
    ],
    namespace="articles"
)

# Query with metadata filter
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=5,
    namespace="articles",
    filter={"topic": {"$eq": "databases"}},
    include_metadata=True
)
```

Namespaces partition data within an index. Queries only search within one namespace. Use them to separate tenants, environments, or document types.

## Qdrant (Self-Hosted or Cloud)

High-performance vector database written in Rust. Self-hosted via Docker or managed cloud.

```bash
docker run -p 6333:6333 qdrant/qdrant
pip install qdrant-client
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

client.upsert(
    collection_name="documents",
    points=[
        PointStruct(id=1, vector=[0.1, 0.2, ...],
                    payload={"text": "Vector databases store embeddings", "source": "wiki"}),
        PointStruct(id=2, vector=[0.3, 0.4, ...],
                    payload={"text": "SQL databases use tables", "source": "docs"})
    ]
)

results = client.query_points(
    collection_name="documents",
    query=[0.1, 0.2, ...],
    limit=5,
    query_filter={"must": [{"key": "source", "match": {"value": "wiki"}}]}
)
```

## Distance Metrics

| Metric | Range | Best For | Notes |
|---|---|---|---|
| Cosine | 0 to 1 (distance) | Text similarity | Direction matters, magnitude ignored. Most common default. |
| Euclidean (L2) | 0 to infinity | Image features, spatial data | Sensitive to magnitude. |
| Dot Product | -inf to inf | Pre-normalized vectors | Fastest. Equivalent to cosine for unit vectors. |

- Use **cosine** unless you have a specific reason not to.
- Use **dot product** when vectors are already unit-normalized.
- Use **Euclidean** when vector magnitude carries meaning.

## Indexing Types

**Flat (Brute Force)**: Compares query against every vector. Perfect recall, slowest. Use for under 10k vectors.

**HNSW (Hierarchical Navigable Small World)**: Graph-based approximate search. High recall (>95%), fast queries, higher memory. Best general-purpose index. Key params: `M` (connections per node), `ef_construction` (build quality), `ef` (search quality).

**IVF (Inverted File Index)**: Clusters vectors, searches nearby clusters only. Faster to build than HNSW, lower recall. Key param: `nlist` (number of clusters). Good when you need fast index builds.

## Chunking Strategies

Before embedding, long documents must be split into chunks.

**Fixed-Size**: Split into N-token chunks with overlap. Simple and predictable.
```python
def fixed_chunks(text, size=512, overlap=50):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size - overlap)]
```

**Sentence-Based**: Split on sentence boundaries using `nltk.sent_tokenize()`. Preserves grammatical units.

**Recursive Character Splitting**: Split by paragraphs, then sentences, then words. Keeps semantically related text together. Used by LangChain's `RecursiveCharacterTextSplitter`.

**Semantic Chunking**: Group sentences by embedding similarity. Start a new chunk when similarity drops below threshold. Most coherent results, but slower and more expensive.

Guidelines:
- 256-512 tokens is a good default chunk size.
- Use 10-20% overlap to preserve context at boundaries.
- Smaller chunks = more precise retrieval; larger chunks = more context per result.
- Q&A benefits from smaller chunks; summarization from larger ones.

## Metadata Filtering

All major vector databases support combining vector similarity with metadata filters.

Common operations:
- Equality: `{"category": "technical"}`
- Range: `{"date": {"$gte": "2024-01-01"}}`
- List membership: `{"tags": {"$in": ["python", "rust"]}}`
- Boolean: `{"$and": [...]}`, `{"$or": [...]}`

Pre-filtering reduces the number of vectors compared and improves query speed.

## RAG Pipeline Pattern

Retrieval-Augmented Generation: embed query -> vector search -> inject context -> LLM generates answer.

```python
def rag_query(question, collection, llm_client, embed_model, top_k=5):
    query_vector = embed_model.encode(question).tolist()
    results = collection.query(query_embeddings=[query_vector], n_results=top_k)
    context = "\n\n".join(results["documents"][0])

    response = llm_client.chat.completions.create(
        model="claude-sonnet-4-20250514",
        messages=[
            {"role": "system", "content":
                "Answer using only the provided context. "
                "If the context lacks the answer, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content
```

Key points:
- Always use the same embedding model for documents and queries.
- Retrieve more chunks than you think you need, then let the LLM filter relevance.
- Include metadata (source, page number) so the LLM can cite sources.

## Common Patterns

**Document Q&A**: Chunk documents (256-512 tokens with overlap), embed and store with metadata (doc ID, page, section), retrieve top-k at query time, pass to LLM.

**Code Search**: Parse into functions/classes, embed both code and natural language descriptions, use metadata filters for language/repo/path.

**Recommendation Engine**: Embed items by description/features, embed user preferences or recent interactions, search for similar items filtering out already-seen content.

## Choosing a Vector Database

| Need | Recommendation |
|---|---|
| Prototyping, local dev | ChromaDB |
| Already using PostgreSQL | pgvector |
| Managed, zero-ops | Pinecone |
| Self-hosted, high performance | Qdrant |
| Large-scale production | Qdrant or Pinecone |
| Tight budget, moderate scale | pgvector or ChromaDB with persistent storage |
