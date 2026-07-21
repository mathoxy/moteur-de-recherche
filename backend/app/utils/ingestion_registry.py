from __future__ import annotations

import json
from datetime import datetime, UTC
from pathlib import Path

from app.core.config import INGESTED_FILE



class IngestionRegistry:
    """
    Registre local des documents déjà ingérés.

    Structure du fichier JSON :

    {
        "<sha256>": {
            "filename": "code_travail.pdf",
            "ingested_at": "2026-07-16T20:15:30Z"
        }
    }
    """

    def __init__(
        self,
        registry_path: str | Path = INGESTED_FILE
    ) -> None:
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.registry_path.exists():
            self._save({})

    def is_ingested(
        self,
        file_hash: str
    ) -> bool:
        registry = self._load()
        return file_hash in registry

    def mark_ingested(
        self,
        file_hash: str,
        filename: str
    ) -> None:
        registry = self._load()

        registry[file_hash] = {
            "filename": filename,
            "ingested_at": datetime.now(
                UTC
            ).isoformat()
        }

        self._save(registry)

    def remove(
        self,
        file_hash: str
    ) -> None:
        registry = self._load()

        if file_hash in registry:
            del registry[file_hash]
            self._save(registry)

    def get_metadata(
        self,
        file_hash: str
    ) -> dict | None:
        registry = self._load()
        return registry.get(file_hash)

    def list_documents(self) -> dict:
        return self._load()

    def _load(self) -> dict:
        try:
            with open(
                self.registry_path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):
            return {}

    def _save(
        self,
        data: dict
    ) -> None:
        with open(
            self.registry_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )