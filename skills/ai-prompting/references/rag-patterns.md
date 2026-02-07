# Retrieval-Augmented Generation (RAG)

## What is RAG?

RAG augments LLM prompts with relevant context retrieved from external sources (documents, databases, APIs). This improves response accuracy and grounds answers in specific data.

## Flow

```
User Query
    ↓
Retrieve Relevant Documents
    ↓
Augment Prompt with Context
    ↓
Send to LLM
    ↓
Generate Response
```

## Implementation Steps

### 1. Prepare Knowledge Base
```bash
# Convert documents to embeddings
python embed_documents.py --input docs/ --output embeddings.json
```

### 2. Retrieve Relevant Context
```python
results = retriever.search(query, top_k=3)
context = "\n".join([doc.content for doc in results])
```

### 3. Augment Prompt
```
Context:
{retrieved_context}

Question: {user_query}

Answer based on the above context:
```

### 4. Generate Response
```python
response = llm.generate(augmented_prompt)
```

## Tools & Libraries

- **Embedding Models**: OpenAI Embeddings, Sentence Transformers
- **Vector Databases**: Pinecone, Weaviate, Chroma
- **RAG Frameworks**: LangChain, LlamaIndex, Haystack

## Best Practices

1. **Quality > Quantity** - Better to retrieve 3 highly relevant docs than 10 mediocre ones
2. **Hybrid Search** - Combine semantic + keyword search
3. **Reranking** - Re-rank retrieved docs by relevance to query
4. **Chunk Wisely** - Balance chunk size vs semantic coherence
5. **Update Regularly** - Keep knowledge base current

## Prompt Template for RAG

```
You are a helpful assistant. Use the provided context to answer questions accurately.
If the context doesn't contain relevant information, say "I don't have that information."

Context:
---
{context}
---

Question: {question}
Answer:
```
