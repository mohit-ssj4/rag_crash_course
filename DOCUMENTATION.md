# 📊 Aurora Dynamics RAG Project Documentation

## Executive Summary

This document provides a comprehensive technical overview and architectural blueprint of the **Aurora Dynamics RAG (Retrieval-Augmented Generation)** pipeline. Designed as a localized knowledge retrieval system, the pipeline loads corporate policy and operational manuals, chunks the data, embeds the text using localized sentence-transformer models, stores them in a persistent ChromaDB database, and queries Groq's LLM cloud service for context-bounded QA.

---

## 🏗️ System Architecture

The pipeline follows a modular, feed-forward RAG architecture:

```
[ Raw Text Data ] 📂 (data/*.txt)
        │
        ▼
 [ DataLoader ] 🔄 (langchain Documents with Metadata)
        │
        ▼
[ DataChunker ] ✂️ (Recursive Splitter: 1000 chars, 200 overlap)
        │
        ▼
[ EmbeddingManager ] 🧠 (sentence-transformers: all-MiniLM-L6-v2)
        │
        ▼
 [ VectorStore ] 💾 (ChromaDB Persistent Client / cosine space)
        │
        ▼
[ RAGRetriever ] 🔍 (Similarity search & context filtering)
        │
        ▼
 [ LLM Client ] 💬 (Groq API / openai/gpt-oss-120b)
```

---

## 🧩 Architectural Modules

### 1. Data Ingestion & Loader (`DataLoader`)

- **Location:** `src/data_loader.py`
- **Class:** `DataLoader`
- **Functionality:**
  - Scans a target directory (`data/`) for files matching a glob pattern (default `*.txt`).
  - Reads text files using `utf-8` encoding.
  - Converts raw content into standard LangChain `Document` objects.
  - Attaches semantic metadata for tracking and provenance:
    - `source`: Absolute or relative path to the file.
    - `file_name`: Name of the file.
    - `file_type`: File extension (e.g., `.txt`).

### 2. Text Partitioning & Segmentation (`DataChunker`)

- **Location:** `src/data_chunker.py`
- **Class:** `DataChunker`
- **Functionality:**
  - Ingests loaded LangChain `Document` objects.
  - Uses LangChain's `RecursiveCharacterTextSplitter` to partition long text files into digestible chunks.
  - **Parameters:**
    - `chunk_size`: 1000 characters (default).
    - `chunk_overlap`: 200 characters (default, maintaining context continuity between adjacent chunks).

### 3. Numerical Vector Embedding (`EmbeddingManager`)

- **Location:** `src/embedding_manager.py`
- **Class:** `EmbeddingManager`
- **Functionality:**
  - Employs the `sentence-transformers` library to run semantic modeling locally.
  - **Model:** `all-MiniLM-L6-v2` (compact, high-performance bi-encoder producing 384-dimensional vectors).
  - Normalizes the generated embeddings so they represent unit vectors, optimizing distance comparisons.
  - Batch processes texts using a configurable `batch_size` (default: 32).

### 4. Vector Database & Storage (`VectorStore`)

- **Location:** `src/vector_store.py`
- **Class:** `VectorStore`
- **Functionality:**
  - Manages storage using `chromadb` (ChromaDB persistent client).
  - **Storage Location:** `data/vector_store/` (persisted on disk).
  - **Collection:** `aurora_docs`.
  - **Distance Metric:** Cosine similarity (specified via metadata `{"hnsw:space": "cosine"}`).
  - Each stored document record maps:
    - A unique ID (`doc_<uuid>_<index>`).
    - The vector embedding.
    - Metadata, including original fields plus `doc_index` and `content_length`.
    - Raw text page content.

### 5. LLM Client Gateway (`LLMClient`)

- **Location:** `src/llm_client.py`
- **Functionality:**
  - Uses `python-dotenv` to load environment variables from `.env`.
  - Instantiates the `Groq` client wrapper.
  - Defines the operational large language model.
  - **Model Name:** `openai/gpt-oss-120b` (as defined in code, can be overridden based on API capabilities).

### 6. Retrieval & Context Synthesis (`RAGRetriever`)

- **Location:** `src/rag_retriever.py`
- **Class:** `RAGRetriever`
- **Functionality:**
  - Executes the core Retrieval-Augmented Generation.
  - **Vector Querying:** Converts user query into an embedding using `EmbeddingManager` and searches `VectorStore` for top-k results.
  - **Score Conversion:** Converts Chroma cosine distances into similarity scores (`similarity_score = 1 - distance`).
  - **Filtering:** Filters out matches that fall below the `score_threshold` (minimum similarity score).
  - **Contextual Injection:** Aggregates raw text of the top matches into a cohesive single string context.
  - **System Constraints Prompt:** Instructs the Groq LLM to respond using **ONLY** the provided context:
    - Refuses outside knowledge.
    - Demands exact fallback: `"I don't know based on the available documents."`
    - Forces attribution by requiring the model to state the sources of the answer.

### 7. Orchestration Loop (`run_pipeline`)

- **Location:** `src/run_pipeline.py`
- **Functionality:**
  - Acts as the entrypoint for execution.
  - Chains the entire process flow: Loading -> Chunking -> Embedding -> Vector DB insertion -> Retrieval loop.
  - Spawns an interactive CLI loop where users query the RAG system until typing `exit` or `quit`.

---

## 📊 Sample Corporate Dataset

The default corpus resides in `data/` and contains operational materials for **Aurora Dynamics** (a fictional robotics startup based in Bengaluru):

- `01-company-overview.txt`: Corporate history, mission statement, office locations, and funding history.
- `02-product-overview.txt`: Flagship robot Carrier X2 specs, payloads, navigation, and lidar tech.
- `03-leave-policy.txt`: Standard annual, parental, and sick leave guidelines.
- `04-remote-work-policy.txt`: Core hours, stipends, and physical/digital security requirements.
- `05-support-runbook.txt`: Maintenance, troubleshooting, and error codes for Carrier X2.
- `06-q1-2025-update.txt`: Latest performance updates, hospital deployments, and revenue reports.
