# Groundly

AI support that only answers from your docs — white-label RAG chatbot with citations, human handoff, admin dashboard, and an embeddable widget.

**Tagline:** ChatGPT for your business — grounded in your content, never making things up.

## Docs

- [Product spec](ai-support-agent-platform-docs.md)
- [6-phase build plan](docs/phases/README.md)
- [Design system & logo](docs/design-system.md)
- [Repo structure](STRUCTURE.md)

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI, PostgreSQL + pgvector, Redis |
| Admin | React + Vite |
| Widget | Vanilla JS + Shadow DOM |
| LLM | Claude (answers) · OpenAI embeddings |

## Status

Scaffold + product docs. Implementation follows [docs/phases](docs/phases/README.md) starting with Phase 1.
