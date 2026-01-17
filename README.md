# LangGraph Chatbot with PaymentAgent

A production-grade chatbot system built with LangGraph, featuring specialized agents for conversation, payment processing, FAQ, and escalation handling. Integrated with LM Studio for local LLM inference.

## 🌟 Features

- **Multi-Agent Architecture**: 5 specialized agents working together
  - 🤖 ConversationAgent - General chat and orchestration
  - 🎯 IntentClassifierAgent - Intent detection and routing
  - 💳 PaymentAgent - Payment processing
  - ❓ FAQAgent - Frequently asked questions
  - 🆘 EscalationAgent - Complex case handling

- **LangGraph Workflows**: State-managed conversation flows
  - Main chat workflow with intent-based routing
  - Separate payment workflow with validation
  - Checkpoint-based state persistence

- **LM Studio Integration**: Local LLM inference
  - OpenAI-compatible API
  - Configurable models and parameters
  - Privacy-focused local processing

- **FastAPI Backend**: Production-ready REST API
  - Chat endpoints with session management
  - Payment processing endpoints
  - Swagger documentation
  - CORS support

## 📋 Prerequisites

- Python 3.10 or higher
- [LM Studio](https://lmstudio.ai/) installed and running
- A model loaded in LM Studio

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd projects/agentic-ai/langgraph-ecommerce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install-dev

# Setup project
make setup
```

### 2. Configure Environment

Edit `.env` file with your LM Studio settings:

```bash
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL_NAME=your-model-name
```

### 3. Start LM Studio

1. Open LM Studio
2. Load a model (e.g., Llama 2, Mistral, etc.)
3. Start the local server (default: http://localhost:1234)

### 4. Run the Application

```bash
# Start API server
make run

# Or manually
uvicorn src.api.main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 📖 Usage

### Chat API

```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I want to make a payment",
    "metadata": {}
  }'

# Get chat history
curl "http://localhost:8000/chat/{session_id}/history"

# Clear chat history
curl -X POST "http://localhost:8000/chat/{session_id}/clear"
```

### Payment API

```bash
# Process payment
curl -X POST "http://localhost:8000/payment/process" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "currency": "USD",
    "description": "Test payment"
  }'

# Check transaction status
curl "http://localhost:8000/payment/{transaction_id}"
```

### Test Workflow

```bash
# Test the chat workflow
python scripts/test_workflow.py
```

## 🏗️ Architecture

```
User Message
     ↓
IntentClassifier
     ↓
  Routing
     ↓
┌────┴────┬─────────┬──────────┐
│         │         │          │
Conversation  Payment  FAQ  Escalation
     │         │         │          │
     └─────────┴─────────┴──────────┘
                 ↓
            Response
```

## 📁 Project Structure

```
langgraph-test/
├── src/
│   ├── agents/          # Agent implementations
│   ├── graphs/          # LangGraph workflows
│   ├── tools/           # Agent tools
│   ├── memory/          # Memory & checkpoints
│   ├── prompts/         # Prompt templates
│   ├── state/           # State schemas
│   ├── models/          # Data models
│   ├── services/        # LLM service
│   ├── api/             # FastAPI app
│   ├── core/            # Core config
│   └── utils/           # Utilities
├── tests/               # Test suite
├── scripts/             # Helper scripts
├── data/                # Data storage
└── docs/                # Documentation
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific tests
pytest tests/unit/test_agents.py -v
pytest tests/integration/test_api.py -v
```

## 🛠️ Development

```bash
# Format code
make format

# Lint code
make lint

# Clean build artifacts
make clean
```

## 📚 Documentation

- [Architecture](docs/architecture.md) - System architecture and design
- [Graphs](docs/graphs.md) - Workflow diagrams and explanations
- [Agents](docs/agents.md) - Agent documentation and prompts

## 🔧 Configuration

Key configuration options in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LM_STUDIO_BASE_URL` | LM Studio API URL | `http://localhost:1234/v1` |
| `LM_STUDIO_MODEL_NAME` | Model name | `local-model` |
| `LLM_TEMPERATURE` | LLM temperature | `0.7` |
| `LLM_MAX_TOKENS` | Max tokens | `2048` |
| `MAX_CONVERSATION_HISTORY` | Max messages | `20` |
| `PAYMENT_MOCK_MODE` | Use mock payments | `true` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [LangChain](https://github.com/langchain-ai/langchain)
- API framework: [FastAPI](https://fastapi.tiangolo.com/)
- Local LLM: [LM Studio](https://lmstudio.ai/)

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review example scripts in `scripts/`

---

**Note**: This project uses mock payment processing by default. For production use, integrate with a real payment gateway.
