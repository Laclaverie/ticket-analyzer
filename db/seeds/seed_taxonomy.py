"""
Seed script: inserts base taxonomy categories from taxonomy-core into the database.

Usage (from repo root, after running migrations):
    uv run python db/seeds/seed_taxonomy.py

Or with a custom DATABASE_URL:
    DATABASE_URL=sqlite:///./data/my.db uv run python db/seeds/seed_taxonomy.py
"""
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
for _pkg in (
    "packages/taxonomy-core/src",
    "packages/persistence/src",
    "packages/domain-models/src",
):
    _path = str(_root / _pkg)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from persistence.base import Base
import persistence.models  # noqa: F401
from persistence.models.category import CategoryORM
from taxonomy_core.loader import TaxonomyLoader
from taxonomy_core.models import TaxonomyNode


def _insert_nodes(db, nodes: list[TaxonomyNode]) -> int:
    count = 0
    for node in nodes:
        cat = CategoryORM(
            id=node.id,
            name=node.name,
            slug=node.slug,
            parent_id=node.parent_id,
            is_food=node.is_food,
        )
        db.add(cat)
        count += 1
        count += _insert_nodes(db, node.children)
    return count


def seed(database_url: str) -> None:
    connect_args = {"check_same_thread": False} if "sqlite" in database_url else {}
    engine = create_engine(database_url, connect_args=connect_args)
    factory = sessionmaker(bind=engine)
    db = factory()

    existing = db.query(CategoryORM).count()
    if existing > 0:
        print(f"Categories already seeded ({existing} rows). Skipping.")
        db.close()
        return

    nodes = TaxonomyLoader.load_default()
    total = _insert_nodes(db, nodes)
    db.commit()
    print(f"Seeded {total} categories.")
    db.close()


if __name__ == "__main__":
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/ticket_analyzer.db")
    seed(db_url)
