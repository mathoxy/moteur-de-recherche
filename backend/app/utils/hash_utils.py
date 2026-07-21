import hashlib
from pathlib import Path


def file_hash(
    file_path: str | Path
) -> str:
    """
    Calcule le SHA256 d'un fichier.
    """

    sha = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(
            lambda: file.read(8192),
            b""
        ):
            sha.update(chunk)

    return sha.hexdigest()