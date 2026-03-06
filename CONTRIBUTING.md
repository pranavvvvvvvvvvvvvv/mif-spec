# Contributing to MIF

## Adapter Contributions

The most impactful way to contribute is writing adapters for memory systems. An adapter converts a system's native format to/from MIF.

### Writing an Adapter

1. Create a directory under `adapters/` named after the system (e.g., `adapters/crewai/`)
2. Include:
   - Export function: system format -> MIF JSON
   - Import function: MIF JSON -> system format
   - README with usage examples
   - Test file with sample data
3. Validate output against `schema/mif-v2.schema.json`

### Adapter Guidelines

- Map system-specific fields to MIF core fields where possible
- Put system-specific metadata in `vendor_extensions`
- Preserve unknown fields on round-trip
- Handle partial data gracefully (not all systems have all fields)

## Spec Changes

For changes to the core specification:

1. Open an issue describing the problem and proposed solution
2. Discuss with maintainers before submitting a PR
3. Changes must be backward-compatible (additive only)
4. Include rationale for any new required fields

## Validation

All example files must validate against the JSON Schema:

```bash
# Using ajv-cli
npx ajv validate -s schema/mif-v2.schema.json -d examples/minimal.mif.json
npx ajv validate -s schema/mif-v2.schema.json -d examples/full.mif.json
```

## Code of Conduct

Be respectful. This is a collaborative effort to solve memory portability for everyone.
