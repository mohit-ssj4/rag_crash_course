# 🚀 Aurora Dynamics - RAG Crash Course

Welcome to the **Retrieval-Augmented Generation (RAG) Crash Course** project! This project demonstrates how to build a production-grade local RAG pipeline from scratch using Python, LangChain, ChromaDB, Hugging Face `sentence-transformers`, and the Groq Cloud API.

The knowledge base in this repository is built around **Aurora Dynamics** (a fictional healthcare robotics company based in Bengaluru, India), which manufactures the Carrier X2 medical transport robot.

For a deep technical breakdown of the architecture, data structures, and pipeline parameters, see [DOCUMENTATION.md](./DOCUMENTATION.md).

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

4. **Run the Pipeline:**
   ```bash
   uv run src/run_pipeline.py
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

4. **Run the Pipeline:**
   ```bash
   python src/run_pipeline.py
   ```

---

## 🏃 Running the Interactive Pipeline

When you run `src/run_pipeline.py`, the system executes the following steps automatically:

1. **Data Loading:** Ingests plain text corporate manuals from the `data/` directory (e.g., leave policies, remote work guidelines, robot maintenance runbooks).
2. **Data Chunking:** Slices the large text files into 1000-character chunks with a 200-character overlap to preserve semantic context.
3. **Local Embedding Generation:** Generates unit-normalized 384-dimensional vector embeddings using the `all-MiniLM-L6-v2` Sentence Transformer model running locally.
4. **Vector Store Insertion:** Saves chunks and vector embeddings into a local, persistent ChromaDB instance situated in `data/vector_store/`.
5. **Interactive Query Loop:** Opens a prompt in your terminal:
   ```text
   [INFO] Vector store initialized. Collection: aurora_docs
   [INFO] Existing documents in collection: 32

   Enter your query:
   ```

### 💬 Example Queries to Try:

- _What is the Series B funding amount for Aurora Dynamics, and who led the round?_
- _What should I do if the Carrier X2 robot shows Error Code 404?_
- _What is the daily stipend amount for working from home under the remote work policy?_
- _Does the Q1 2025 update mention any new hospital deployments?_

Type **`exit`** or **`quit`** to close the session.

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
│   ├── data_loader.py          # Document loader module
│   ├── data_chunker.py         # Text chunking and splitting module
│   ├── embedding_manager.py    # Local SentenceTransformer embeddings generator
│   ├── vector_store.py         # ChromaDB interface
│   ├── llm_client.py           # Dotenv parser and Groq cloud gateway
│   ├── rag_retriever.py        # Cosine retrieval and context synthesizing engine
│   └── run_pipeline.py         # Orchestration flow and CLI query loop
├── .env.example                # Sample environment configuration template
├── pyproject.toml              # Modern Python metadata and dependencies file
├── requirements.txt            # Traditional pip dependency manifest
└── DOCUMENTATION.md            # In-depth architectural documentation
```

---

## ⚖️ License

This project is proprietary and for educational use only.
