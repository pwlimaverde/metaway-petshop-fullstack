from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"


def read_version() -> str:
    raw = VERSION_FILE.read_text(encoding="utf-8").strip()
    normalized = raw[1:] if raw.startswith("v") else raw
    if not re.fullmatch(r"\d+\.\d+\.\d+", normalized):
        raise ValueError(
            "VERSION deve estar no formato semver (ex: 1.0.0 ou v1.0.0)."
        )
    return normalized


def replace_first(path: Path, pattern: str, repl: str) -> None:
    content = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, repl, content, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Não foi possível atualizar {path}")
    path.write_text(updated, encoding="utf-8")


def sync_pyproject(version: str) -> None:
    path = ROOT / "apps/api/pyproject.toml"
    replace_first(path, r'^version = ".*"$', f'version = "{version}"')


def sync_package_json(version: str) -> None:
    path = ROOT / "apps/web/package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = version
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_package_lock(version: str) -> None:
    path = ROOT / "apps/web/package-lock.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = version
    if isinstance(data.get("packages"), dict) and isinstance(data["packages"].get(""), dict):
        data["packages"][""]["version"] = version
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sync_api_main(version: str) -> None:
    path = ROOT / "apps/api/src/metaway_api/main.py"
    replace_first(path, r'version=".*"', f'version="{version}"')


def main() -> None:
    version = read_version()
    sync_pyproject(version)
    sync_package_json(version)
    sync_package_lock(version)
    sync_api_main(version)
    print(f"Versão sincronizada para {version}")


if __name__ == "__main__":
    main()
