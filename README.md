# Memory Interchange Format (MIF)

A vendor-neutral JSON schema for portable AI agent memories.

## The Problem

30+ AI memory systems exist — mem0, Zep, Cognee, Letta, basic-memory, shodh-memory, and more. Each stores fundamentally the same data (id, content, timestamp, type, metadata) in incompatible formats. There is no way to move memories between systems.

**MIF solves memory portability.** Like vCard for contacts or iCalendar for events — a minimal envelope so memories can move between providers.

## What MIF Is

- A JSON schema for exporting and importing AI agent memories
- A minimal core: `id`, `content`, `created_at` — that's it for a valid memory
- Optional knowledge graph support for systems that track entity relationships
- Vendor extensions so systems preserve proprietary metadata without polluting the core
- Privacy/PII redaction built into the export metadata

## What MIF Is Not

- Not a specification for how memory systems work internally
- Not a database format or storage engine
- Not opinionated about retrieval, embeddings, or ranking strategies

## Quick Example

A minimal conforming MIF document:

```json
{
  "mif_version": "2.0",
  "memories": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "content": "User prefers dark mode across all applications",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

A full document can include memory types, entities, embeddings, knowledge graph, vendor extensions, and privacy metadata. See [examples/](./examples/) for complete samples.

## Specification

The full specification is in [`spec/mif-v2.md`](./spec/mif-v2.md).

Key sections:
- **Memory Object** — required and optional fields
- **Knowledge Graph** — optional entity and relationship data
- **Vendor Extensions** — system-specific metadata preservation
- **Privacy** — PII detection and redaction
- **Import Behavior** — UUID preservation, deduplication, partial failure tolerance

## JSON Schema

Validate MIF documents against [`schema/mif-v2.schema.json`](./schema/mif-v2.schema.json).

## Adapters

Format adapters bridge existing memory systems to MIF:

| System | Status | Location |
|--------|--------|----------|
| [shodh-memory](https://github.com/varun29ankuS/shodh-memory) | Production | Built-in (`/api/export/mif`, `/api/import/mif`) |
| mem0 JSON | Production | [Rust adapter](https://github.com/varun29ankuS/shodh-memory/blob/main/src/mif/adapters/mem0.rs) |
| Markdown (YAML frontmatter) | Production | [Rust adapter](https://github.com/varun29ankuS/shodh-memory/blob/main/src/mif/adapters/markdown.rs) |
| Generic JSON | Production | [Rust adapter](https://github.com/varun29ankuS/shodh-memory/blob/main/src/mif/adapters/generic.rs) |
| CrewAI | Planned | — |
| LangChain | Planned | — |

## Design Principles

1. **Minimal** — Only memories + optional graph. No todos, projects, or other concerns.
2. **Extensible** — Unknown fields and vendor extensions MUST be preserved on round-trip.
3. **Vendor-neutral** — The schema doesn't favor any implementation.
4. **Forward-compatible** — Importers MUST ignore unknown fields.

## Contributing

We welcome adapter implementations for any memory system. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Related

- [MCP SEP #2342](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2342) — Original proposal to the Model Context Protocol
- [tower-mcp #531](https://github.com/joshrotenberg/tower-mcp/issues/531) — Tracking issue in tower-mcp
- [shodh-memory](https://github.com/varun29ankuS/shodh-memory) — Reference implementation

## Validation

```bash
pip install -r requirements.txt
python validate.py examples/*.mif.json
python tests/round_trip.py examples/*.mif.json
```

## Version Note

MIF v2.0 is the first public release. The "v2" numbering reflects internal iterations during development in shodh-memory. There is no public v1 specification.

## License

Apache 2.0
