import os
from pathlib import Path


def _load_dotenv_file(path: Path) -> None:
    """
    Minimal `.env` loader (no external deps).
    Supports lines like: KEY=value
    Ignores blank lines and `#` comments.
    Does not override existing OS env vars.
    """
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue

        # Strip common quotes.
        if len(value) >= 2 and ((value[0] == value[-1]) and value[0] in ("'", '"')):
            value = value[1:-1]

        os.environ.setdefault(key, value)


# Repo root is `.../backend`
_load_dotenv_file(Path(__file__).resolve().parents[2] / ".env")


def _split_emails(raw: str) -> set[str]:
    # Accept comma/semicolon separated lists.
    raw = (raw or "").replace(";", ",")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


ALLOWED_EMAILS: set[str] = _split_emails(os.getenv("ALLOWED_EMAILS", ""))
AUTH_PASSWORD: str = os.getenv("AUTH_PASSWORD", "")

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h
