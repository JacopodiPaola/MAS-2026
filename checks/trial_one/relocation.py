"""Validate path-only relocation against the original executed-source hashes.

Historical run manifests are never rewritten. An alias is used only when the
current file exactly matches the audited post-relocation digest. Further edits
return the actual current digest, correctly invalidating an old experiment cache.
This module performs no model updates or scientific experiments.
"""

import hashlib
import json
from pathlib import Path


def executed_source_hashes(paths, model_dir):
    registry = json.loads((Path(__file__).parent / "data" / "relocation_provenance.json").read_text())
    aliases = {item["relocated_path"]: item for item in registry["sources"]}
    model_dir = Path(model_dir).resolve()
    result = {}
    for path in paths:
        path = Path(path).resolve()
        current_path = path.relative_to(model_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        alias = aliases.get(current_path)
        if alias is not None and digest == alias["relocated_sha256"]:
            result[alias["executed_path"]] = alias["executed_sha256"]
        else:
            result[current_path] = digest
    return result
