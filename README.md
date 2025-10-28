# Agent SDK – Shared Components & Utilities

**Mission**: Provide shared schemas, data models, clients, and utilities for all Mnemosyne agents.

## Core Components

- **JSON Schemas**: Standardized data formats for inter-agent communication
- **Python Clients**: Reusable client libraries for agent APIs
- **Data Models**: Pydantic models for validation and serialization
- **Logging Utilities**: Consistent logging and observability
- **Event Envelope**: Standard event format for all agents

## Key Schemas

### Standard Event Envelope

```json
{
  "type": "idea.created|outline.ready|draft.cleaned|publish.scheduled",
  "id": "uuid",
  "time": "timestamp",
  "actor": "agent-name",
  "data_ref": "s3://bucket/key",
  "meta": {}
}
```

### Agent-Specific Schemas

- `idea.json` - Content ideas from Aletheia
- `outline.json` - Structured outlines from IRIS
- `draft.json` - Generated drafts from IRIS
- `voiceprint.json` - Voice parameters for IRIS
- `cleaned.json` - Refined content from Erebus
- `publish.json` - Scheduled posts from Kairos
- `mnemosyne_corpus.json` - Memory and context data

## Python Package Structure

```
agent-sdk/
├── schemas/          # JSON schemas
├── models/           # Pydantic data models
├── clients/          # Agent API clients
├── utils/            # Shared utilities
│   ├── logging.py
│   ├── auth.py
│   └── storage.py
└── tests/            # Test suite
```

## Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Install in development mode
pip install -e .

# Run tests
pytest tests/

# Install additional dependencies
pip install <package>
pip freeze > requirements.txt
```

## Usage in Agent Projects

```python
from agent_sdk.models import IdeaModel, DraftModel
from agent_sdk.clients import MnemosyneClient
from agent_sdk.utils.logging import setup_logger

# Use shared models
idea = IdeaModel(
    id="uuid",
    title="Content Title",
    score=0.85
)

# Use shared clients
mnemosyne = MnemosyneClient(base_url="http://localhost:8005")
context = mnemosyne.get_context(topic="AI")

# Use shared logging
logger = setup_logger("agent-aletheia")
logger.info("Processing idea", extra={"idea_id": idea.id})
```

## Testing

The SDK includes comprehensive test coverage:
- Schema validation tests
- Model serialization tests
- Client integration tests
- Utility function tests

## Versioning

The SDK follows semantic versioning:
- **Major**: Breaking changes to schemas or APIs
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes and improvements

All agents should specify their SDK version dependency in `requirements.txt`.

## Related Repositories

All agent repositories depend on this SDK:
- [agent-aletheia](https://github.com/stephenpeters/agent-aletheia)
- [agent-iris](https://github.com/stephenpeters/agent-iris)
- [agent-erebus](https://github.com/stephenpeters/agent-erebus)
- [agent-kairos](https://github.com/stephenpeters/agent-kairos)
- [agent-mnemosyne](https://github.com/stephenpeters/agent-mnemosyne)
