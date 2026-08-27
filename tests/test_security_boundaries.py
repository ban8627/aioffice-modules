from pathlib import Path


def test_modules_do_not_import_database_clients() -> None:
    source_root = Path("src/aioffice_modules")
    forbidden = ("supabase", "psycopg", "sqlalchemy", "asyncpg")
    for path in source_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        assert not any(name in lowered for name in forbidden), path
