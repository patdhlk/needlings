"""Base Sphinx configuration. Each exercise overlays on top of this."""
from __future__ import annotations

project = "needlings exercise"
author = "needlings"
extensions = ["sphinx_needs"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".pristine"]
master_doc = "index"

# sphinx-needs 8 natively reads ubproject.toml. The `[needs]` / `[needs.fields]`
# / `[needs.links]` / `[[needs.types]]` tables defined there override anything
# we could set from Python here, so keep this file minimal and let ubproject.toml
# be the single source of truth.
needs_from_toml = "ubproject.toml"
