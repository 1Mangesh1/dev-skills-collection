---
name: ollama
description: Ollama for running local LLMs — model management, API usage, and integration patterns. Use when user mentions "ollama", "local LLM", "run llama locally", "local AI", "ollama run", "ollama pull", "self-hosted model", "offline AI", "local inference", or running language models on their own machine.
---

# Ollama

## Install and Setup

macOS:
```bash
brew install ollama
```

Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Windows: Download from https://ollama.com/download/windows.

Start the server:
```bash
ollama serve
```

The server listens on `http://localhost:11434` by default. Set `OLLAMA_HOST` to change the bind address.

## Pull and Run Models

```bash
ollama pull llama3       # download without running
ollama run llama3        # run (auto-pulls if missing)
ollama list              # list downloaded models
```

## Interactive Chat vs One-Shot Generation

Interactive chat (opens a REPL, type `/bye` to exit):
```bash
ollama run llama3
```

One-shot generation (pipe input, get output, exit):
```bash
echo "Explain quicksort in two sentences" | ollama run llama3
cat main.py | ollama run codellama "Review this code for bugs"
```

## REST API

### Generate (completion)
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is the sky blue?",
  "stream": false
}'
```

### Chat (multi-turn)
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
  ],
  "stream": false
}'
```

### Embeddings
```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": "Ollama is a tool for running local LLMs"
}'
```

Set `"stream": true` (the default) to receive newline-delimited JSON chunks.

## Model Management

```bash
ollama list                    # list downloaded models
ollama show llama3             # show model details (parameters, template, license)
ollama cp llama3 my-llama3     # copy/alias a model
ollama rm my-llama3            # delete a model
ollama ps                      # list currently loaded/running models
```

`ollama ps` shows VRAM usage, quantization level, and time until unload.

## Modelfile

A Modelfile defines a custom model:

```dockerfile
FROM llama3

SYSTEM "You are a senior software engineer. Be concise. Provide code examples."

PARAMETER temperature 0.3
PARAMETER num_ctx 8192
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER stop "<|eot_id|>"
```

Key parameters:
- `temperature` -- randomness (0.0 = deterministic, 1.0+ = creative).
- `num_ctx` -- context window in tokens. Higher values use more VRAM.
- `top_p` -- nucleus sampling threshold.
- `top_k` -- limits token selection pool.
- `repeat_penalty` -- penalizes repeated tokens.
- `stop` -- stop sequence(s).
- `num_gpu` -- layers to offload to GPU (0 for CPU-only).

## Create Custom Models from Modelfile

```bash
ollama create my-coder -f ./Modelfile
ollama run my-coder
```

To update, edit the Modelfile and run `ollama create` again with the same name.

## GPU vs CPU Detection and Configuration

Ollama auto-detects NVIDIA (CUDA), AMD (ROCm), and Apple Silicon (Metal) GPUs.

```bash
ollama ps   # PROCESSOR column shows gpu or cpu
```

Force CPU-only:
```bash
CUDA_VISIBLE_DEVICES="" ollama serve    # per-session
OLLAMA_NUM_GPU=0 ollama serve           # server-wide
```

Per-model GPU control in a Modelfile:
```dockerfile
PARAMETER num_gpu 0    # force CPU
PARAMETER num_gpu 999  # offload all layers to GPU (default)
```

For multi-GPU, set `CUDA_VISIBLE_DEVICES=0,1`.

## Popular Models and When to Use Which

| Model | Size | Best for |
|---|---|---|
| `llama3` (8B) | 4.7 GB | General chat, reasoning, instruction following |
| `llama3:70b` | 40 GB | Higher quality when you have the VRAM |
| `codellama` (7B) | 3.8 GB | Code generation, completion, infilling |
| `mistral` (7B) | 4.1 GB | Fast general-purpose, structured output |
| `phi3` (3.8B) | 2.2 GB | Small footprint, good quality for its size |
| `gemma2` (9B) | 5.4 GB | Strong reasoning, multilingual |
| `deepseek-coder-v2` (16B) | 8.9 GB | Code generation, multi-language |
| `nomic-embed-text` | 274 MB | Text embeddings for RAG |
| `llava` (7B) | 4.7 GB | Multi-modal image understanding |

For constrained hardware (8 GB RAM), use `phi3` or `llama3` with q4 quantization.

## Embeddings for RAG

Use `nomic-embed-text` (768 dimensions) or `mxbai-embed-large` (1024 dimensions).

```bash
curl http://localhost:11434/api/embed -d '{
  "model": "nomic-embed-text",
  "input": ["document chunk one", "document chunk two"]
}'
```

Response contains an `"embeddings"` array of float vectors. Store in a vector database (ChromaDB, pgvector, Qdrant, FAISS) for similarity search.

## Integration with Python

### Using requests
```python
import requests

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3",
    "prompt": "Explain monads simply",
    "stream": False
})
print(response.json()["response"])
```

### Using ollama-python (`pip install ollama`)
```python
import ollama

# Chat
response = ollama.chat(model="llama3", messages=[
    {"role": "user", "content": "Explain monads simply"}
])
print(response["message"]["content"])

# Embeddings
result = ollama.embed(model="nomic-embed-text", input="some text")
print(len(result["embeddings"][0]))  # 768

# Streaming
for chunk in ollama.chat(model="llama3", messages=[
    {"role": "user", "content": "Write a haiku"}
], stream=True):
    print(chunk["message"]["content"], end="", flush=True)
```

## Integration with JavaScript

### Using fetch
```javascript
const response = await fetch("http://localhost:11434/api/generate", {
  method: "POST",
  body: JSON.stringify({ model: "llama3", prompt: "Explain closures", stream: false }),
});
const data = await response.json();
console.log(data.response);
```

### Using ollama-js (`npm install ollama`)
```javascript
import { Ollama } from "ollama";
const ollama = new Ollama({ host: "http://localhost:11434" });

const response = await ollama.chat({
  model: "llama3",
  messages: [{ role: "user", content: "Explain closures" }],
});
console.log(response.message.content);
```

## Integration with LangChain

Python (`pip install langchain-ollama`):
```python
from langchain_ollama import ChatOllama, OllamaEmbeddings

llm = ChatOllama(model="llama3", temperature=0.3)
response = llm.invoke("What is dependency injection?")

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectors = embeddings.embed_documents(["first chunk", "second chunk"])
```

JavaScript (`npm install @langchain/ollama`):
```javascript
import { ChatOllama } from "@langchain/ollama";
const llm = new ChatOllama({ model: "llama3", temperature: 0.3 });
const response = await llm.invoke("What is dependency injection?");
```

## Multi-Modal Models

Use `llava` or `llava-llama3` for image understanding:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llava",
  "messages": [{"role": "user", "content": "Describe this image", "images": ["BASE64_DATA"]}],
  "stream": false
}'
```

```python
import ollama, base64

with open("photo.jpg", "rb") as f:
    img = base64.b64encode(f.read()).decode()

response = ollama.chat(model="llava", messages=[
    {"role": "user", "content": "What do you see?", "images": [img]}
])
```

## Performance Tuning

Context size -- use the smallest that fits your workload:
```dockerfile
PARAMETER num_ctx 4096   # default
PARAMETER num_ctx 32768  # long documents, more VRAM
```

Partial GPU offloading when model exceeds VRAM:
```dockerfile
PARAMETER num_gpu 20     # 20 layers on GPU, rest on CPU
```

Batch size for prompt processing speed:
```dockerfile
PARAMETER num_batch 512  # default, increase for faster eval
```

Keep-alive control (how long model stays loaded):
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3", "prompt": "hi", "keep_alive": "30m"
}'
```
Use `"keep_alive": 0` to unload immediately, `-1` to keep indefinitely.

Server-wide environment variables:
- `OLLAMA_MAX_LOADED_MODELS` -- concurrent models in memory (default 1).
- `OLLAMA_NUM_PARALLEL` -- concurrent requests per model.
- `OLLAMA_FLASH_ATTENTION=1` -- reduce memory with flash attention.

## Running as a Service

macOS (Homebrew):
```bash
brew services start ollama
```

Linux (systemd -- created automatically by the install script):
```bash
sudo systemctl enable --now ollama
sudo journalctl -u ollama -f
```

Customize with `sudo systemctl edit ollama`:
```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_NUM_PARALLEL=4"
```

Then `sudo systemctl daemon-reload && sudo systemctl restart ollama`.

Docker:
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama run llama3
```

With NVIDIA GPU: add `--gpus=all` to the run command.
