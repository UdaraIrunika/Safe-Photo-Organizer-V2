from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    file_path = Path(path)
    digest = hashlib.sha256()
    with file_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_files(source: str | Path, destination: str | Path) -> dict[str, object]:
    source_path = Path(source)
    destination_path = Path(destination)

    if not destination_path.exists():
        return {"verified": False, "status": "MISSING_DESTINATION"}

    source_hash = sha256_file(source_path)
    destination_hash = sha256_file(destination_path)
    verified = source_hash == destination_hash

    return {
        "verified": verified,
        "source_hash": source_hash,
        "destination_hash": destination_hash,
        "status": "VERIFIED" if verified else "HASH_MISMATCH",
    }
