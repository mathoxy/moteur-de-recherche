from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

INGESTED_FILE = DATA_DIR / "ingested.json"

PERSIST_DIRECTORY = DATA_DIR / "vectorstore"