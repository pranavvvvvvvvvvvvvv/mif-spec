"""Adapter registry and top-level API."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from mif.adapters import (
    MifAdapter,
    ShodhAdapter,
    Mem0Adapter,
    GenericJsonAdapter,
    MarkdownAdapter,
)
from mif.models import MifDocument


class AdapterRegistry:
    """Registry of format adapters with auto-detection.

    Detection order (most specific first):
    1. Shodh (MIF v2/v1) — has mif_version or shodh-memory marker
    2. mem0 — JSON array with "memory" field
    3. Generic JSON — JSON array with "content" field
    4. Markdown — starts with "---"
    """

    def __init__(self) -> None:
        self.adapters: list[MifAdapter] = [
            ShodhAdapter(),
            Mem0Adapter(),
            GenericJsonAdapter(),
            MarkdownAdapter(),
        ]

    def auto_detect(self, data: str) -> MifAdapter | None:
        """Find the first adapter that detects the format."""
        for adapter in self.adapters:
            if adapter.detect(data):
                return adapter
        return None

    def get(self, format_id: str) -> MifAdapter | None:
        """Get adapter by format ID."""
        for adapter in self.adapters:
            if adapter.format_id() == format_id:
                return adapter
        return None

    def list_formats(self) -> list[dict[str, str]]:
        """List all available adapters."""
        return [{"name": a.name(), "format_id": a.format_id()} for a in self.adapters]


# Module-level registry
_registry = AdapterRegistry()


def load(data: str, *, format: str | None = None) -> MifDocument:
    """Load a MIF document from a string.

    Auto-detects format unless `format` is specified.

    Args:
        data: Input string (JSON, markdown, etc.)
        format: Optional format ID ("shodh", "mem0", "generic", "markdown")

    Returns:
        MifDocument with parsed memories.

    Raises:
        ValueError: If format cannot be detected or is unknown.
    """
    if format:
        adapter = _registry.get(format)
        if not adapter:
            available = ", ".join(a.format_id() for a in _registry.adapters)
            raise ValueError(f"Unknown format: '{format}'. Available: {available}")
        return adapter.to_mif(data)

    adapter = _registry.auto_detect(data)
    if not adapter:
        raise ValueError(
            "Could not auto-detect format. "
            "Supported: shodh (MIF JSON), mem0, generic JSON array, markdown."
        )
    return adapter.to_mif(data)


def dump(doc: MifDocument, *, format: str = "shodh") -> str:
    """Serialize a MifDocument to a string.

    Args:
        doc: The MIF document to serialize.
        format: Output format ID (default: "shodh" for MIF v2 JSON).

    Returns:
        Serialized string in the requested format.
    """
    adapter = _registry.get(format)
    if not adapter:
        available = ", ".join(a.format_id() for a in _registry.adapters)
        raise ValueError(f"Unknown format: '{format}'. Available: {available}")
    return adapter.from_mif(doc)


def convert(data: str, *, from_format: str | None = None, to_format: str = "shodh") -> str:
    """Convert between formats in one call.

    Args:
        data: Input data string.
        from_format: Source format (auto-detected if None).
        to_format: Target format (default: MIF v2 JSON).

    Returns:
        Converted string in the target format.
    """
    doc = load(data, format=from_format)
    return dump(doc, format=to_format)


def validate(data: str) -> tuple[bool, list[str]]:
    """Validate a MIF JSON document against the schema.

    Args:
        data: JSON string to validate.

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    schema_path = Path(__file__).parent.parent.parent / "schema" / "mif-v2.schema.json"
    if not schema_path.exists():
        # Try relative to package install
        schema_path = Path(__file__).parent / "schema" / "mif-v2.schema.json"
    if not schema_path.exists():
        return False, ["Schema file not found. Install jsonschema and ensure schema is available."]

    try:
        import jsonschema
    except ImportError:
        return False, ["jsonschema not installed. Run: pip install jsonschema"]

    try:
        document = json.loads(data)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]

    with open(schema_path) as f:
        schema = json.load(f)

    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(document))

    if not errors:
        return True, []

    messages = []
    for err in errors:
        path = " -> ".join(str(p) for p in err.absolute_path) or "(root)"
        messages.append(f"[{path}] {err.message}")
    return False, messages
