langgraph-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── __init__.py
│   ├── agents/                      # Agent definitions
│   │   ├── __init__.py
│   │   ├── base.py                 # Base agent class
│   │   ├── researcher.py           # Research agent
│   │   ├── writer.py               # Writer agent
│   │   └── reviewer.py             # Review agent
│   ├── graphs/                      # LangGraph workflows ⭐
│   │   ├── __init__.py
│   │   ├── research_workflow.py    # Main workflow
│   │   ├── chat_workflow.py        # Chat workflow
│   │   └── nodes.py                # Reusable node functions
│   ├── tools/                       # Agent tools
│   │   ├── __init__.py
│   │   ├── search.py               # Web search tool
│   │   ├── calculator.py           # Calculator tool
│   │   └── code_executor.py        # Code execution tool
│   ├── chains/                      # LangChain chains
│   │   ├── __init__.py
│   │   ├── rag_chain.py            # RAG chain
│   │   └── summarization.py        # Summarization
│   ├── memory/                      # Memory systems ⭐
│   │   ├── __init__.py
│   │   ├── conversation.py         # Conversation memory
│   │   └── checkpoints.py          # State checkpoints
│   ├── prompts/                     # Prompt templates ⭐
│   │   ├── __init__.py
│   │   ├── agent_prompts.py
│   │   └── system_prompts.py
│   ├── state/                       # State definitions ⭐
│   │   ├── __init__.py
│   │   ├── agent_state.py          # Agent state schemas
│   │   └── graph_state.py          # Graph state schemas
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── schemas.py              # Pydantic schemas
│   │   └── enums.py                # Enums
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── llm_service.py          # LLM management
│   │   ├── vector_store.py         # Vector store service
│   │   └── document_loader.py      # Document processing
│   ├── api/                         # API endpoints
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── agents.py
│   │   │   └── graphs.py
│   │   └── dependencies.py
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py               # Settings
│   │   ├── logging.py              # Logging setup
│   │   └── exceptions.py           # Custom exceptions
│   └── utils/                       # Utilities
│       ├── __init__.py
│       ├── helpers.py
│       └── validators.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_graphs.py
│   │   ├── test_tools.py
│   │   └── test_state.py
│   ├── integration/
│   │   ├── test_workflows.py
│   │   └── test_api.py
│   └── conftest.py
├── data/
│   ├── documents/                   # Source documents
│   ├── embeddings/                  # Vector embeddings
│   ├── checkpoints/                 # Graph checkpoints ⭐
│   └── logs/                        # Execution logs
├── notebooks/                       # Experiments
│   ├── agent_testing.ipynb
│   └── graph_visualization.ipynb
├── scripts/
│   ├── setup_vector_db.py
│   ├── load_documents.py
│   └── test_workflow.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── architecture.md
│   ├── graphs.md                    # Graph documentation ⭐
│   ├── agents.md
│   └── deployment.md
├── .env.example
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── Makefile
├── README.md
└── venv/