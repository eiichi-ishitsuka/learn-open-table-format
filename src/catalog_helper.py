"""Local Iceberg catalog, storage path, and DuckDB helper utilities."""

from __future__ import annotations

import shutil
from pathlib import Path

import duckdb
from pyiceberg.catalog.sql import SqlCatalog


def find_repo_root(start: Path | None = None) -> Path:
    """Resolve the repository root containing pyproject.toml."""
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return cur


ROOT_DIR = find_repo_root()
STORAGE_DIR = ROOT_DIR / "storage"
LANDING_DIR = STORAGE_DIR / "data-landing"
LAKEHOUSE_DIR = STORAGE_DIR / "lakehouse-main"

LAYERS = ("bronze", "silver", "gold", "pii_vault")


def init_storage(clean: bool = False) -> dict[str, Path]:
    """Create the two-bucket local storage layout (data-landing & lakehouse-main)."""
    if clean and STORAGE_DIR.exists():
        shutil.rmtree(STORAGE_DIR)
    LANDING_DIR.mkdir(parents=True, exist_ok=True)
    for layer in LAYERS:
        (LAKEHOUSE_DIR / layer).mkdir(parents=True, exist_ok=True)
    return {
        "root": ROOT_DIR,
        "landing": LANDING_DIR,
        "lakehouse": LAKEHOUSE_DIR,
    }


def get_iceberg_catalog(name: str = "local", db_name: str = "iceberg_catalog.db") -> SqlCatalog:
    """Return a SQLite-backed PyIceberg catalog pointing to storage/lakehouse-main."""
    LAKEHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    catalog = SqlCatalog(
        name,
        **{
            "uri": f"sqlite:///{LAKEHOUSE_DIR / db_name}",
            "warehouse": f"file://{LAKEHOUSE_DIR}",
        },
    )
    for ns in LAYERS:
        catalog.create_namespace_if_not_exists(ns)
    return catalog


def get_duckdb_conn() -> duckdb.DuckDBPyConnection:
    """Return an in-memory DuckDB connection."""
    return duckdb.connect(database=":memory:")


def register_iceberg_table(
    conn: duckdb.DuckDBPyConnection,
    table,
    view_name: str,
    snapshot_id: int | None = None,
) -> duckdb.DuckDBPyConnection:
    """Register an Iceberg table (or specific snapshot) as a DuckDB view via Arrow."""
    scan = table.scan(snapshot_id=snapshot_id) if snapshot_id is not None else table.scan()
    conn.register(view_name, scan.to_arrow())
    return conn
