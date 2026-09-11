# 🚀 Aurora Dynamics - RAG Crash Course

Welcome to the **Retrieval-Augmented Generation (RAG) Crash Course** project! This project demonstrates how to build a production-grade local RAG pipeline from scratch using Python, LangChain, ChromaDB, Hugging Face `sentence-transformers`, and the Groq Cloud API.

The knowledge base in this repository is built around **Aurora Dynamics** (a fictional healthcare robotics company based in Bengaluru, India), which manufactures the Carrier X2 medical transport robot.

This codebase has been fully refactored to separate offline ingestion from online retrieval, centralize configuration loading, implement secure severity-aware global logging, build robust API retries with backoffs, and establish a 100% offline-isolated unit testing suite.

For a deep technical breakdown of the architecture, data structures, and pipeline parameters, see [DOCUMENTATION.md](./DOCUMENTATION.md).

For validation queries, hallucination defense details, and QA matrices, see [VALIDATION.md](./VALIDATION.md).

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python:** Version `3.13` or higher (configured in `.python-version`)
- **Git**
- A **Groq API Key** (Get one from [Groq Console](https://console.groq.com/))

---

## ⚙️ Quick Start & Setup

This repository is optimized to use **`uv`**, the blazing-fast Python package installer and resolver. You can also use standard Python `venv` and `pip`. Choose one of the setups below:

### Option A: Using `uv` (Recommended)

1. **Install `uv`** (if not already installed):

   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Synchronize Dependencies:**
   `uv` will automatically read `pyproject.toml` and build a virtual environment for you.

   ```bash
   uv sync
   ```

3. **Configure Environment Variables:**
   Copy the example environment file and add your Groq API key:

   ```bash
   cp .env.example .env
   ```

   Open `.env` in your editor and enter your Groq API Key:

   ```env
   GROQ_API_KEY="your-actual-groq-api-key-here"
   ```

---

### Option B: Using Standard Python `venv` and `pip`

1. **Create and Activate a Virtual Environment:**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On Windows (Command Prompt)
   .venv\Scripts\activate
   # On Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # On macOS/Linux
   source .venv/bin/activate
   ```

2. **Install Dependencies:**

   ```bash
   pip install --upgrade pip
   # Install from requirements.txt
   pip install -r requirements.txt
   # Or install from pyproject.toml
   pip install .
   ```

3. **Configure Environment Variables:**

   ```bash
   copy .env.example .env     # Windows CMD
   # or
   cp .env.example .env       # macOS/Linux/Git Bash
   ```

   Open `.env` in your editor and enter your Groq API Key:

   ```env
   GROQ_API_KEY="your-actual-groq-api-key-here"
   ```

---

## 🏃 Running the Command-Line Interface

The application exposes a single, unified entry point inside `src/cli.py` featuring three explicit subparsers:

### 1. Ingest Raw Documents (Offline)
Parses raw plain-text manuals from the `data/` directory, chunks them, generates 384-dimensional semantic embeddings running completely locally on your CPU, and indexes them into ChromaDB:
```bash
# Using uv
uv run python -m src.cli ingest

# Using standard Python environment
python -m src.cli ingest
```

### 2. Direct Single Query (Online)
Direct-loads the pre-computed database index from disk, runs semantic search and retrieval, and outputs the synthesized context-bounded response in under 1 second. **Zero raw documents are read, and zero embeddings are generated for raw text during retrieval:**
```bash
# Using uv
uv run python -m src.cli query "How many days of paid annual leave do employees get?"

# Using standard Python environment
python -m src.cli query "How many days of paid annual leave do employees get?"
```

### 3. Multi-Turn Interactive Shell (Online)
Enters an interactive chat session keeping database and model instances warm in memory for rapid, consecutive semantic searches:
```bash
# Using uv
uv run python -m src.cli interactive

# Using standard Python environment
python -m src.cli interactive
```
*Prompt syntax:* `Aurora-RAG >`  
*Exit keywords:* Type `exit` or `quit` to cleanly terminate.

### 4. Backward-Compatible Wrapper
The original `src/run_pipeline.py` script has been retrofitted to delegate directly to the new CLI's ingestion and interactive modes, maintaining backward compatibility:
```bash
uv run python src/run_pipeline.py
```

---

### 💬 Example Queries to Try:

- *A robot stopped in a corridor and is blinking orange. What do I do?* (Support Runbook)
- *How much does the Carrier X2 cost and what does the price include?* (Subscription pricing)
- *Where does Aurora Dynamics have offices, and which one is hiring the most in 2025?* (Multi-document synthesis)
- *What color is the Carrier X2?* (Hallucination defense; outputs refusal because fact does not exist in the corpus)

---

## 🧪 Running Automated Tests (100% Offline-Safe)

We use `pytest` for unit and integration testing. All tests are completely isolated from internet access or live token usage by employing autouse mocks inside `tests/conftest.py`:
```bash
# Run all tests using uv
uv run --with pytest python -m pytest tests/
```
**Total:** 17 tests covering environment validation, whitelisted global logging, subcommand parsing, empty-state protections, and Groq request retries.

---

## 📁 Directory Structure

```text
rag_crash_course/
├── data/                       # Ground-truth corporate document repository
│   ├── 01-company-overview.txt # Company history, offices, and funding
│   ├── 02-product-overview.txt # Carrier X2 hardware, sensors, and payload
│   ├── 03-leave-policy.txt     # Leave allowances and parental policies
│   ├── 04-remote-work-policy.txt # Core hours, security, and WFH stipends
│   ├── 05-support-runbook.txt  # Troubleshooting steps and Carrier X2 error codes
│   ├── 06-q1-2025-update.txt   # Latest business performance and news
│   └── vector_store/           # ChromaDB database folder (auto-generated)
├── src/                        # Core application code
│   ├── config.py               # CENTRALIZED settings loader and validator (New)
│   ├── logger.py               # CENTRALIZED global logger formatting and whitelist (New)
│   ├── data_loader.py          # Document loader module (Integrated with logging)
│   ├── data_chunker.py         # Text chunking and splitting module
│   ├── embedding_manager.py    # Local SentenceTransformer embeddings generator
│   ├── vector_store.py         # ChromaDB interface (PEP-8 compliant)
│   ├── llm_client.py           # Groq cloud gateway (Config integrated)
│   ├── rag_retriever.py        # Cosine retrieval and retry boundaries engine (Refactored)
│   ├── cli.py                  # UNIFIED CLI Subcommand dispatcher (New)
│   └── run_pipeline.py         # Retrofitted backwards-compatible wrapper
├── tests/                      # Automated unit test suite (New)
│   ├── conftest.py             # Global autouse mocks for offline-safety (New)
│   ├── test_cli.py             # Subcommand parsing and empty-state warning tests (New)
│   ├── test_config.py          # Configuration loading and type validation tests (New)
│   ├── test_logger.py          # Formatter and secure levels whitelist tests (New)
│   └── test_retriever.py       # Retriever and Groq transient error retry tests (New)
├── .env.example                # Sample environment configuration template
├── pyproject.toml              # Modern Python metadata and dependencies file
├── requirements.txt            # Traditional pip dependency manifest
├── DOCUMENTATION.md            # In-depth architectural documentation (Updated)
├── VALIDATION.md               # Multi-scenario validation QA report (New)
└── README.md                   # Quick-start guide (Updated)
```

---

## ⚖️ License

This project is proprietary and for educational use only.
