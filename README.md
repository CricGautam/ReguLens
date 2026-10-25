# ReguLens
### Enterprise AI-Powered Regulatory Compliance Intelligence System

ReguLens is an AI-powered regulatory compliance intelligence system designed to help organizations process regulatory documents, retrieve relevant internal policies, map compliance obligations to organizational controls, and identify potential evidence gaps.

The project combines **Natural Language Processing (NLP), Retrieval-Augmented Generation (RAG), local Large Language Models (LLMs), and rule-based compliance assessment**, with multi-agent orchestration planned as the next development phase.

**Status:** Active Development | Functional Prototype

## 1. Problem Statement

Organizations manage large volumes of regulatory documents, internal policies, operational procedures, audit records, and compliance evidence.

Manually identifying regulatory obligations, locating relevant controls, and validating supporting evidence can be time-consuming and difficult to trace.

ReguLens explores how AI-assisted document processing and retrieval can support these workflows while preserving source traceability and human oversight.

## 2. Implemented Features

**Regulatory Document Processing**
- PDF ingestion and text extraction using FastAPI and PDFPlumber.
- Document classification using Python and Scikit-learn.
- SQLite-based document metadata and processing-status tracking.
- Structured regulatory requirement extraction and Pydantic validation.

**Regulatory Knowledge Management**
- Extracted and validated 7 requirements from Rule 6 of India's Digital Personal Data Protection Rules, 2025.
- Stored legal references, applicability, effective dates, and source metadata in SQLite.

**Retrieval-Augmented Generation**
- Semantic document retrieval using Sentence Transformers and ChromaDB.
- Persistent local vector storage for indexed policy content.
- Integration with Qwen3 4B through Ollama for locally generated, document-grounded answers.

**Compliance Evidence Assessment**
- Regulatory obligation-to-control mapping.
- Structured evidence assessment using synthetic enterprise records.
- Identification of missing evidence and potential compliance gaps.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.12 |
| Backend API | FastAPI, Uvicorn |
| Data validation | Pydantic |
| Document processing | PDFPlumber |
| Machine learning | Scikit-learn |
| Embeddings | Sentence Transformers |
| Vector database | ChromaDB |
| Local LLM | Qwen3 4B |
| LLM runtime | Ollama |
| Relational database | SQLite |

## 4. System Architecture

Current implementation:

```text
Regulatory Documents / Internal Policies
                  |
                  v
          Document Ingestion
             (FastAPI)
                  |
                  v
        PDF Text Extraction
            (PDFPlumber)
                  |
                  v
      Classification / Validation
        (Scikit-learn, Pydantic)
                  |
          +-------+--------+
          |                |
          v                v
   Regulatory Data    Policy Documents
      (SQLite)              |
                            v
                     Text Chunking
                            |
                            v
                  Sentence Transformers
                            |
                            v
                         ChromaDB
                            |
                     Semantic Search
                            |
                            v
                    Ollama / Qwen3
                            |
                            v
                   Grounded AI Answer

Separate evidence-assessment workflow:

Regulatory Requirement
         |
         v
     Control Mapping
         |
         v
    Evidence Records
         |
         v
    Gap Assessment
         |
         v
Potential Evidence Gap
```

The RAG question-answering and evidence-assessment workflows are currently implemented as separate services. Automated multi-agent orchestration is under development.

## 5. Verified Prototype Results

| Capability | Observed result |
|---|---|
| Regulatory requirement extraction | 7 structured Rule 6 requirements |
| Policy vector indexing | 7 document chunks |
| Local LLM integration | Qwen3 4B successfully tested |
| Evidence assessment | 3 quarterly review records evaluated |
| Gap identification | 1 missing quarterly access-review record identified |

These results demonstrate prototype functionality, not production-scale performance or model accuracy benchmarks.

## 6. Getting Started

### Prerequisites

- Python 3.12
- Git
- Ollama installed locally
- Sufficient memory to run the selected local LLM

### Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ReguLens
```

### Create a Virtual Environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```
Install the spaCy English language model:

```powershell
python -m spacy download en_core_web_sm
```


### Download the Local LLM

```powershell
ollama pull qwen3:4b
```

Ensure the Ollama service is running.

### Start the FastAPI Backend

```powershell
uvicorn app.main:app --reload
```

Open the interactive API documentation:

http://127.0.0.1:8000/docs

The API supports regulatory document ingestion and processing.

### Index the Sample Policy

Before running RAG queries, index the included synthetic NovaCart access-control policy.

From the project root, start Python:

```powershell
python
```

Run:

```python
from app.services.rag_service import index_documents

indexed_count = index_documents(
    "data/synthetic/novacart/policies/novacart's_access_control_policy.md"
)

print(f"Indexed chunks: {indexed_count}")
```

Expected output:

```text
Indexed chunks: 7
```

Exit Python:

```python
exit()
```

This process generates embeddings using `all-MiniLM-L6-v2` and stores them in the local ChromaDB database.

The embedding model may require an internet connection for its initial download. The local ChromaDB database is excluded from Git.

### Run a RAG Query

After indexing the included sample policy documents, the RAG service can be called from Python:

```python
from app.services.llm_service import ask_regulens

result = ask_regulens(
    "What does NovaCart require for quarterly access reviews?"
)

print(result["answer"])
print(result["sources"])
```

**Note:** Initial document indexing and local database setup are required before querying. Automated first-run setup is not yet available.

## 7. Example Compliance Scenario

ReguLens uses a fictional organization, **NovaCart**, to demonstrate compliance workflows.

Example:

- Regulatory context: DPDP Rule 6.
- Internal control: NC-AC-003 — quarterly access review.
- Evidence: quarterly access-review records.
- Observed result: Q1 and Q2 records completed; Q3 review evidence missing.

**Assessment:** Potential evidence gap requiring human review.

A missing record does not, by itself, establish a legal violation. Regulatory effective dates and applicability must be considered separately.

All NovaCart business data is synthetic.

## 8. Development Roadmap

- [x] FastAPI backend and document ingestion
- [x] PDF extraction and document classification
- [x] SQLite metadata and requirement storage
- [x] Structured regulatory requirement extraction
- [x] Local vector indexing and semantic retrieval
- [x] Ollama and Qwen3 integration
- [x] Initial rule-to-control evidence assessment
- [ ] LangGraph-based multi-agent orchestration
- [ ] Automated compliance reporting
- [ ] Streamlit user interface
- [ ] Evaluation and benchmarking
- [ ] Fine-tuning experiments
- [ ] Deployment and operational monitoring

## 9. Scope and Limitations

ReguLens is an independently developed prototype and is not a certified compliance assessment platform.

Its outputs are intended to assist compliance analysis, not replace legal interpretation, formal audits, or human approval.

The project currently uses a limited regulatory knowledge base and synthetic enterprise evidence. Broader regulatory coverage, systematic retrieval evaluation, and end-to-end agent orchestration remain future work.

## 10. Project Objective

To develop a reproducible, enterprise-oriented AI system that combines regulatory document intelligence, retrieval, evidence assessment, and eventually coordinated AI agents to support governance, risk, and compliance workflows.