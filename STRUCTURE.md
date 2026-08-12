# Groundly — repository structure

```
groundly/
├── assets/brand/              # Source logo PNGs
├── docs/                      # Product + phase docs + design system
├── backend/                   # FastAPI API + worker
│   ├── alembic/versions/      # DB migrations
│   ├── app/
│   │   ├── api/routes/        # HTTP endpoints
│   │   ├── core/              # config, security, deps
│   │   ├── db/                # engine, Base
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── schemas/           # Pydantic DTOs
│   │   ├── services/          # ingest, RAG, LLM, rate limit
│   │   ├── workers/           # background jobs
│   │   └── main.py
│   ├── tests/
│   ├── uploads/
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/                  # React admin dashboard (Vite)
│   ├── public/brand/          # Favicon / static brand
│   └── src/
│       ├── assets/brand/
│       ├── components/layout/
│       ├── components/ui/
│       ├── hooks/
│       ├── layouts/
│       ├── lib/
│       ├── pages/
│       ├── styles/            # tokens.css + global.css
│       ├── types/
│       ├── App.tsx
│       └── main.tsx
├── widget/                    # Vanilla JS embed (Shadow DOM)
│   ├── src/
│   └── dist/
├── scripts/                   # seed, isolation, eval runners
├── evals/                     # golden Q&A JSON
└── fixtures/riverside/        # sample PDFs / FAQ content
```

See [docs/phases/README.md](docs/phases/README.md) for build order.
