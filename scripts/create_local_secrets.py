"""Create local random secrets without printing them or replacing an existing .env."""
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parents[1]


def main():
    keys = ("POSTGRES_PASSWORD", "APP_DATABASE_PASSWORD", "WAREHOUSE_PASSWORD",
            "WAREHOUSE_LOADER_PASSWORD", "JWT_SECRET_KEY")
    try:
        with (ROOT / ".env").open("x", encoding="utf-8") as handle:
            handle.write("".join(f"{key}={secrets.token_urlsafe(32)}\n" for key in keys))
    except FileExistsError:
        print("Existing .env preserved.")
    else:
        print("Created ignored .env with local secrets. API keys remain optional.")


if __name__ == "__main__":
    main()

