# MIF Adapters

Adapters convert between external memory formats and MIF v2.0. The reference implementation lives in [shodh-memory](https://github.com/varun29ankuS/shodh-memory/tree/main/src/mif/adapters) (Rust).

## How Adapters Work

Each adapter implements the `MifAdapter` trait:

```rust
pub trait MifAdapter: Send + Sync {
    fn name(&self) -> &str;              // Human-readable name
    fn format_id(&self) -> &str;         // Unique format identifier
    fn detect(&self, data: &[u8]) -> bool;  // Auto-detect format
    fn to_mif(&self, data: &[u8]) -> Result<MifDocument>;   // External -> MIF
    fn from_mif(&self, doc: &MifDocument) -> Result<Vec<u8>>; // MIF -> External
}
```

The `AdapterRegistry` tries adapters in order of specificity until one matches:

1. **Shodh** (MIF v1/v2) — most specific
2. **mem0** — JSON array with `"memory"` field
3. **Generic JSON** — JSON array with `"content"` field
4. **Markdown** — YAML frontmatter blocks

Or you can specify the format explicitly via the `format` parameter.

## Available Adapters

### mem0

**Detects:** JSON array where objects have a `"memory"` field (not `"content"`).

**Input format:**
```json
[
  {
    "memory": "User prefers dark mode",
    "metadata": { "category": "preference" },
    "user_id": "user-1",
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

**Mapping:**
| mem0 field | MIF field |
|-----------|-----------|
| `memory` | `content` |
| `metadata.category` | `memory_type` |
| `id` | `id` (UUID generated if absent) |
| `created_at` | `created_at` |
| `user_id` | `source.session_id` |
| All other metadata | `metadata` |

### Markdown (YAML Frontmatter)

**Detects:** Content starting with `---` delimiter. Supports Letta/Obsidian-style memory files.

**Input format:**
```markdown
---
type: observation
tags: [rust, performance]
created_at: 2026-01-15
---
User prefers Rust for backend services because of memory safety.
---
type: decision
tags: [database]
---
Using RocksDB for persistent storage with column families.
```

**Mapping:**
| YAML field | MIF field |
|-----------|-----------|
| `type` | `memory_type` |
| `tags` | `tags` (supports `[a, b]` or `a, b`) |
| `created_at` / `date` | `created_at` |
| `id` | `id` (UUID generated if absent) |
| Body text | `content` |
| All other YAML fields | `metadata` |

### Generic JSON

**Detects:** JSON array where objects have a `"content"` field.

**Input format:**
```json
[
  {
    "content": "User prefers dark mode",
    "type": "decision",
    "timestamp": "2026-01-15T10:30:00Z",
    "tags": ["ui", "preferences"]
  }
]
```

**Mapping:**
| Generic field | MIF field |
|--------------|-----------|
| `content` | `content` |
| `type` / `memory_type` | `memory_type` |
| `timestamp` / `created_at` / `date` | `created_at` |
| `id` | `id` (UUID generated if absent) |
| `tags` | `tags` |
| All other fields | `metadata` |

### Shodh (Native)

**Detects:** JSON with `"mif_version"` or `"shodh-memory"` key.

Handles both MIF v2 (direct deserialization) and MIF v1 (automatic conversion). v1->v2 conversion strips legacy ID prefixes, normalizes PascalCase types to lowercase snake_case, and restructures the graph format.

## HTTP API

```bash
# Export with auto-format (defaults to MIF v2)
curl -X POST http://localhost:3030/api/mif/export \
  -H "X-API-Key: $KEY" \
  -d '{"user_id": "user-1", "include_graph": true}'

# Import with auto-detection
curl -X POST http://localhost:3030/api/mif/import \
  -H "X-API-Key: $KEY" \
  -d '{"user_id": "user-1", "data": "<json or markdown string>"}'

# Import with explicit format
curl -X POST http://localhost:3030/api/mif/import \
  -H "X-API-Key: $KEY" \
  -d '{"user_id": "user-1", "format": "mem0", "data": "[{\"memory\": \"...\"}]"}'
```

## Writing a New Adapter

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. The key requirements:

1. Implement detection logic that doesn't false-positive on other formats
2. Map all available fields to MIF core fields
3. Put system-specific data in `vendor_extensions`
4. Preserve UUIDs when present in the source
5. Generate stable UUIDs (from content hash) when source has no IDs
