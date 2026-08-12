"""Groundly API — FastAPI application entrypoint (Phase 1)."""

from fastapi import FastAPI

app = FastAPI(title="Groundly", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "groundly"}
