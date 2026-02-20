# 🤖 Multi-Agent Coding Assistant

A production-quality multi-agent pipeline that autonomously writes, reviews, tests, and optimizes Python code — built with LangGraph, Claude AI, RAG, MCP, and LangSmith.

---

## 🏆 Benchmark Results

| Difficulty | Tasks | Avg Score | Tests Passed |
|-----------|-------|-----------|-------------|
| Easy      | 4     | **100%**  | 4/4 ✅       |
| Medium    | 4     | **85%**   | 4/4 ✅       |
| Hard      | 2     | **80%**   | 2/2 ✅       |
| **Overall** | **10** | **88%** | **10/10 ✅** |

> DSPy prompt optimization confirmed pipeline baseline at **88%** — near-optimal for task set.

---

## 🏗️ Architecture

```
USER TASK
    │
    ▼
┌─────────────────────────────────────────────────┐
│              LangGraph Pipeline                  │
│                                                  │
│  ┌──────────┐    ┌─────────────┐                │
│  │ Planner  │───▶│ Code Writer │◀─── Qdrant RAG │
│  │  Agent   │    │    Agent    │    (TF-IDF,    │
│  └──────────┘    └──────┬──────┘   15 docs)     │
│                         │                        │
│                  ┌──────▼──────┐                │
│                  │  Reviewer   │                 │
│                  │    Agent    │                 │
│                  └──────┬──────┘                │
│                         │                        │
│                  ┌──────▼──────┐                │
│                  │ Test Writer │◀─── Docker      │
│                  │    Agent    │     Sandbox     │
│                  └──────┬──────┘                │
└─────────────────────────┼───────────────────────┘
                          │
                    ┌─────▼──────┐
                    │   Final    │
                    │   Output   │
                    └────────────┘
                          │
                   LangSmith Traces
                   (full observability)
```

---

## ✨ Features

- **Multi-Agent Orchestration** — LangGraph state machine with 4 specialized agents: Planner, Code Writer, Reviewer, Test Writer
- **RAG Knowledge Retrieval** — Qdrant vector database with TF-IDF indexing over 15 Python best-practice documents; queried before every code generation step
- **Sandboxed Code Execution** — pytest runs in an isolated Docker container; zero risk to host machine
- **MCP Tool Server** — 6 tools exposed via Model Context Protocol: `write_file`, `read_file`, `execute_code`, `search_web`, `query_docs`, `list_files`
- **Automated Evaluation** — 5-dimension scoring system (syntax, type hints, docstrings, error handling, test pass rate) across 10 benchmark tasks
- **LangSmith Observability** — Full tracing of every LLM call, token count, latency, and agent chain
- **DSPy Optimization** — BootstrapFewShot prompt optimizer integrated; baseline confirmed at 88%
- **Iterative Refinement** — Code Writer loops up to 3 times based on Reviewer feedback before finalizing

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph |
| LLM | Claude Opus 4.5 (Anthropic) |
| RAG Vector DB | Qdrant (in-memory/persistent) |
| RAG Embeddings | TF-IDF (pure Python, zero DLL deps) |
| Tool Protocol | MCP (Model Context Protocol) |
| Code Execution | Docker (sandboxed pytest) |
| Observability | LangSmith |
| Prompt Optimization | DSPy (BootstrapFewShot) |
| Web Search | Tavily API |

---

## 📁 Project Structure

```
multi-agent-coding-assistant/
├── agents/
│   ├── graph.py          # LangGraph state machine + run_pipeline()
│   ├── planner.py        # Task decomposition agent
│   ├── code_writer.py    # Code generation agent (RAG-enhanced)
│   ├── reviewer.py       # Code quality reviewer
│   └── test_writer.py    # pytest generation + Docker execution
├── mcp_server/
│   └── server.py         # MCP server with 6 tools
├── rag/
│   ├── indexer.py        # TF-IDF vocabulary builder + Qdrant upsert
│   ├── retriever.py      # Query engine (query_points API)
│   └── vocab.json        # Saved vocabulary for query-time vectorization
├── eval/
│   ├── metrics.py        # 5-dimension code quality scorer
│   ├── benchmarks.py     # 10 benchmark tasks (easy/medium/hard)
│   └── eval_results.json # Latest benchmark results
├── dspy_optimizer/
│   ├── signatures.py     # DSPy signatures for each agent
│   ├── optimizer.py      # BootstrapFewShot optimization loop
│   └── optimized_pipeline.json
├── langsmith_dataset.py  # Pushes benchmarks to LangSmith datasets
├── langsmith_setup.py    # LangSmith connection verification
├── run_eval.py           # Evaluation runner
├── smoke_test.py         # Quick end-to-end test
└── .env                  # API keys (not committed)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker Desktop (for sandboxed test execution)
- API keys: Anthropic, Tavily, LangSmith

### Installation

```bash
git clone https://github.com/yourusername/multi-agent-coding-assistant
cd multi-agent-coding-assistant

pip install langgraph langchain-anthropic mcp tavily-python \
            qdrant-client langsmith dspy-ai python-dotenv
```

### Configure environment

```bash
cp .env.example .env
# Fill in your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# TAVILY_API_KEY=tvly-...
# LANGCHAIN_API_KEY=lsv2_pt_...
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=multi-agent-coder
```

### Build the RAG index

```bash
python rag/indexer.py
```

### Run a quick smoke test

```bash
python smoke_test.py
```

### Run full evaluation

```bash
python run_eval.py   # edit difficulty="easy/medium/hard/all"
```

### Run DSPy optimization

```bash
python dspy_optimizer/optimizer.py
```

---

## 📊 Evaluation Scoring

Each generated function is scored across 5 dimensions:

| Metric | Weight | Detection Method |
|--------|--------|-----------------|
| Syntax Valid | 25% | `ast.parse()` |
| Type Hints | 20% | Regex: `-> type` + `param: type` |
| Docstring | 20% | Triple-quote string present |
| Error Handling | 20% | `raise` or `try/except` block |
| Test Pass Rate | 15% | pytest exit code in Docker |

---

## 🔍 LangSmith Tracing

Every pipeline run is fully traced in LangSmith:

```
benchmark-run (task_name)
  └── multi-agent-pipeline
        ├── planner-agent        → plan + LLM tokens
        ├── code-writer-agent    → RAG query + generated code
        ├── reviewer-agent       → score + feedback
        └── test-writer-agent    → pytest result
```

View live traces at [smith.langchain.com](https://smith.langchain.com) after running any eval.

---

## 💡 Key Engineering Decisions

**Why Qdrant over ChromaDB?**
ChromaDB's sentence-transformers dependency pulls in PyTorch, causing DLL failures on Windows. Qdrant with pure-Python TF-IDF has zero native dependencies and works reliably cross-platform.

**Why TF-IDF over neural embeddings?**
For a knowledge base of 15 curated documents, TF-IDF retrieval is fast, deterministic, and requires no GPU. Neural embeddings add latency and dependency complexity without meaningful accuracy gains at this scale.

**Why MCP for tooling?**
MCP provides a standardized protocol for tool exposure, making it easy to add/swap tools without touching agent logic. The same tool server can serve multiple agents or be replaced with a remote server.

**Why Docker for test execution?**
Generated code is untrusted — running it directly on the host machine is a security risk. Docker provides complete isolation with a predictable Python + pytest environment.

---

## 📈 Sample Output

```
[1/4] Running: binary_search (medium)...

  ✅  Syntax Valid         100%
  ✅  Type Hints           100%
  ✅  Docstring            100%
  ✅  Error Handling       100%
  ✅  Tests Passed         100%

  TOTAL SCORE: 100.0 / 100   (98.4s)
  Iterations: 1
```

---

## 🗓️ Build Timeline

| Day | Focus | Key Deliverable |
|-----|-------|----------------|
| Day 1 | Foundation | LangGraph pipeline + 4 agents + MCP server |
| Day 2 | Tools & Testing | Docker sandbox + Tavily search + smoke tests |
| Day 3 | RAG + Evaluation | Qdrant RAG + 10-task benchmark + LangSmith |
| Day 4 | Polish | DSPy optimization + README + portfolio ready |

---

## 🧑‍💻 Author

**Mani Sharma**
Built as a portfolio project demonstrating multi-agent AI systems, LLM orchestration, RAG pipelines, and production-quality evaluation frameworks.

---

## 📄 License

MIT License — free to use, modify, and distribute.
