from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_FILENAME_PATTERN = re.compile(
    r"^(?P<prefix>[A-Za-z]+)_(?P<number>[0-9]+(?:-bis)?)_(?P<language>[A-Za-z]{2})$"
)
_ARTICLE_PATTERN = re.compile(
    r"\b(?:ARTICLE|ART\.)\s*(?P<article>PREMIER|[0-9]+(?:-[0-9]+)?)\b",
    re.IGNORECASE,
)


def _sidecar_path(file_path: Path) -> Path:
    return file_path.with_suffix(".json")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def infer_file_metadata(file_path: Path) -> dict[str, Any]:
    match = _FILENAME_PATTERN.match(file_path.stem)
    if not match:
        return {
            "title": file_path.stem,
            "document_type": None,
            "document_number": None,
            "publication_date": None,
            "source_url": None,
            "language": None,
        }

    prefix = match.group("prefix").replace("_", " ").strip()
    number = match.group("number")
    language = match.group("language").lower()
    document_type = "Bulletin officiel" if prefix.lower().startswith("bo") or prefix.lower().startswith("bulletin") else prefix
    return {
        "title": f"{prefix} n° {number}",
        "document_type": document_type,
        "document_number": number,
        "publication_date": None,
        "source_url": None,
        "language": language,
    }


def load_file_metadata(file_path: Path) -> dict[str, Any]:
    metadata = infer_file_metadata(file_path)
    sidecar = _load_json(_sidecar_path(file_path))
    if sidecar:
        metadata.update({key: value for key, value in sidecar.items() if value not in (None, "")})
    else:
        save_file_metadata(file_path, metadata)
    return metadata


def save_file_metadata(file_path: Path, metadata: dict[str, Any]) -> None:
    _sidecar_path(file_path).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )


def extract_article_number(text: str) -> str | None:
    match = _ARTICLE_PATTERN.search(text)
    if not match:
        return None
    return match.group("article").upper()


def normalize_publication_date(value: Any) -> str | None:
    if value in (None, ""):
        return None

    if isinstance(value, str):
        date_match = re.search(r"/Date\((?P<ms>\d+)\)/", value)
        if date_match:
            timestamp_ms = int(date_match.group("ms"))
            return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).date().isoformat()
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            return value

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value) / 1000, tz=UTC).date().isoformat()

    return None