import os
from pathlib import Path

def find_repo_root() -> Path:
    """
    Traverses up from the current file's directory to find the repository root.
    The root is identified by the presence of 'packages' or 'apps' directories.
    """
    current = Path(__file__).resolve().parent
    # Safety limit to avoid infinite loops if directories are missing
    for _ in range(10):
        if (current / "packages").exists() or (current / "apps").exists():
            return current
        if current.parent == current:
             break
        current = current.parent

    # Fallback to current working directory if root can't be found by traversal
    return Path(os.getcwd()).resolve()

def get_default_database_url() -> str:
    root = find_repo_root()
    db_path = root / "data" / "ticket_analyzer.db"
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"

def get_default_storage_path() -> str:
    root = find_repo_root()
    storage_path = root / "data" / "images"
    storage_path.mkdir(parents=True, exist_ok=True)
    return str(storage_path)
