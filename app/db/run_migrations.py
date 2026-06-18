"""Run all SQL migration files against Supabase at startup.

Two execution paths:
1. Uses ``DATABASE_URL`` (direct Postgres connection) when available – ideal for Railway.
2. Falls back to Supabase's REST ``/sql`` endpoint with the service-role key.

All migration SQL must be idempotent (``IF NOT EXISTS`` / ``DO $$ … END $$``).
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_MIGRATION_DIRS = [
    Path(__file__).resolve().parent / "migrations",
    Path(__file__).resolve().parent.parent.parent / "supabase" / "migrations",
]


def _sort_key(path: Path) -> tuple[int, str]:
    stem = path.stem
    m = re.match(r"^(\d+)[_-]?(.*)", stem)
    return (int(m.group(1)) if m else 0, m.group(2) if m else stem)


def _collect_migrations() -> list[Path]:
    files: list[Path] = []
    for d in _MIGRATION_DIRS:
        if d.is_dir():
            files.extend(sorted(d.glob("*.sql"), key=_sort_key))
    return files


def _run_via_psycopg2(statements: list[str]) -> None:
    """Execute statements via a direct Postgres connection (DATABASE_URL)."""
    import psycopg2  # type: ignore[import-untyped]

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL not set")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                if stmt.upper().startswith("NOTIFY"):
                    continue
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def _run_via_supabase_sql(statements: list[str]) -> None:
    """Execute statements via the Supabase REST SQL endpoint.

    Calls ``POST {supabase_url}/sql`` with the service-role key.
    """
    settings = get_settings()
    headers = {
        "apikey": settings.supabase_secret_key,
        "Authorization": f"Bearer {settings.supabase_secret_key}",
        "Content-Type": "application/json",
    }
    with httpx.Client() as client:
        for stmt in statements:
            if stmt.upper().startswith("NOTIFY"):
                continue
            resp = client.post(
                f"{settings.supabase_url}/sql",
                json={"query": stmt},
                headers=headers,
            )
            if resp.status_code >= 400:
                body = resp.text[:500]
                logger.warning("SQL statement failed (%d): %s — %s", resp.status_code, stmt[:120], body)


def run_migrations() -> list[str]:
    """Execute all pending migration files.

    Returns names of successfully applied migrations.
    """
    files = _collect_migrations()
    if not files:
        logger.info("No migration files found in %s", [str(d) for d in _MIGRATION_DIRS])
        return []

    settings = get_settings()
    if not settings.supabase_secret_key:
        logger.warning("SUPABASE_SECRET_KEY not set — skipping auto-migration")
        return []

    has_direct_db = bool(os.environ.get("DATABASE_URL"))

    applied: list[str] = []
    for path in files:
        name = f"{path.parent.name}/{path.name}"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        statements = [s.strip() for s in content.split(";") if s.strip()]

        try:
            if has_direct_db:
                _run_via_psycopg2(statements)
            else:
                _run_via_supabase_sql(statements)
            logger.info("Migration applied: %s", name)
            applied.append(name)
        except Exception:
            logger.exception("Migration FAILED: %s — continuing", name)

    return applied


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
