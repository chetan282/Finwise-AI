# FinWise AI

A personal financial planning application for salaried individuals in India. Enter your income, spending, assets, loans, and insurance once — the app computes your tax under both regimes, net worth, retirement corpus target, and a 0-100 financial health score, then an LLM writes a prioritized action plan grounded in a curated knowledge base.

## Architecture

```
Streamlit form  ->  Financial engine  ->  RAG (FAISS)  ->  Claude API  ->  Dashboard
   (inputs)        (pure-Python math)    (knowledge)      (advice)       (output)
```

**Core design principle: deterministic math is separated from LLM reasoning.**

Every number — tax, retirement corpus, required SIP, net worth, health score — is computed by pure, tested Python functions. The LLM never does arithmetic. Its job is confined to language and prioritization, and a RAG layer grounds it in curated financial knowledge so it cannot invent tax rules or figures.

This separation matters: financial correctness can't be left to a language model.

## What it computes

| Module | Output |
|---|---|
| `tax.py` | Tax under old vs new regime (FY 2025-26), picks the lower, returns take-home |
| `networth.py` | Assets minus liabilities, monthly surplus, savings rate |
| `retirement.py` | Corpus target, required monthly SIP, and an SWP simulation checking whether the money outlasts you |
| `health.py` | A transparent 0-100 score across six weighted components |

### The health score (0-100)

| Component | Points | Full marks at |
|---|---|---|
| Savings rate | 25 | >= 30% of take-home saved |
| Emergency fund | 15 | >= 6 months of expenses in liquid savings |
| Debt burden | 15 | EMIs <= 20% of take-home |
| Life insurance | 15 | Cover >= 10x annual salary |
| Health insurance | 10 | >= Rs 5 lakh cover |
| Retirement readiness | 20 | Projected corpus >= target corpus |

Each component returns its own points, maximum, and a one-line reason, so the user sees exactly why the score is what it is.

## RAG layer

Four curated knowledge documents (tax, investment, insurance, retirement) are chunked by paragraph, embedded locally with `all-MiniLM-L6-v2` (no API cost), and indexed in FAISS using inner-product search over normalized vectors. At query time the retriever fetches the top-k relevant chunks, which are passed to the LLM as grounding context.

## Tech stack

Python, Streamlit, FAISS (`faiss-cpu`), sentence-transformers, Anthropic Claude API, python-dotenv.

## Running it

```bash
pip install -r requirements.txt

cp .env.example .env          # add your ANTHROPIC_API_KEY
python -m rag.build_index     # one time: builds the FAISS index (downloads ~80MB model)
python -m tests.test_engine   # verify the math
streamlit run app.py
```

## Docker

```bash
docker build -t finwise-ai .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=your_key finwise-ai
```

The FAISS index is built during the image build, so the container starts fast and needs no network access for embeddings at runtime.

## Tests

`tests/test_engine.py` verifies the tax calculator against hand-checked FY 2025-26 figures and runs the full engine against a realistic salaried profile:

- Rs 12.75L salary -> new regime -> Rs 0 tax (standard deduction + 87A rebate)
- Rs 20L salary -> new regime -> Rs 1,92,400 tax
- Rs 6L salary with Rs 1.5L 80C -> old regime -> Rs 0 tax

## Disclaimer

Educational tool, not SEBI-registered investment advice. Tax rules reflect FY 2025-26.
