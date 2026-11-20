# qFoldIT Repository Status

**Status:** ACTIVE / CANONICAL SCIENTIFIC ENGINE
**Role:** Substantive atomistic/materials scientific capability.

Expose capabilities through canonical contracts/adapters. Do not redefine scientific truth, provenance or mission-control semantics locally.


## QSIS qualification snapshot — 2026-11-11

- Legacy adapter manifest 0.2.0 / `qfoldit.scientific-adapter/1.0` remains in place for compatibility.
- QSIS 0.1 migration is not complete. One reference-only single-point energy/force capability candidate and schemas are maintained in [UAG-SOS](https://github.com/qfoldit/UAG-SOS/tree/main/SCHEMAS/QSIS/examples).
- Eight MCP operations require individual capability manifests and schemas; one blanket manifest is not acceptable.
- Path-based tool inputs require workspace isolation, traversal/symlink protection and opaque artifact IDs.
- Inspected MCP server config disables CUDA/JAX visibility; GPU execution is not qualified.
- See [QFOLDIT-QSIS-READINESS.md](QFOLDIT-QSIS-READINESS.md).

## 2026-11-20 — QSIS operation contract snapshot

- Eight separate operation-level QSIS Capability Manifest candidates and input/output schemas are now maintained in the canonical [UAG-SOS Atomic-MCP operation catalog](https://github.com/qfoldit/UAG-SOS/blob/main/SCHEMAS/QSIS/examples/atomic-mcp-operation-catalog.json).
- Five operations are mapped to atomistic materials; three are mapped to molecular dynamics.
- The existing `qfoldit.scientific-adapter/1.0` remains legacy compatibility only.
- **No qualification promotion:** the manifests are P1 contract candidates, not proof of a live QSIS Job Request/Result adapter, workspace containment, SHA-256 artifact registration, independent validation, or Evidence 1.2.
- CPU-only execution is the only currently declared profile. GPU execution and per-calculator commercial/model licences require separate review.
- Static CI was triggered in UAG-SOS but did not reach runner steps in the observed run; no CI PASS is claimed.
