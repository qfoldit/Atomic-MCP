# qFoldIT QSIS Integration Readiness — Atomic-MCP

**Snapshot:** 2026-11-11  
**Status:** Legacy adapter active; QSIS operation manifests are not yet connected or qualified  
**Source:** `qfoldit/Atomic-MCP`

## 1. Current implementation inventory

Package: `mcp-atomictoolkit 0.1.0-dev`. The inspected FastMCP server exposes:

| Operation | Tool name |
|---|---|
| Structure construction | `build_structure_workflow` |
| Structure analysis | `analyze_structure_workflow` |
| Write structure artifact | `write_structure_workflow` |
| Geometry optimization | `optimize_structure_workflow` |
| Single-point energy/forces/stress | `single_point_workflow` |
| Molecular dynamics | `run_md_workflow` |
| Trajectory analysis | `analyze_trajectory_workflow` |
| Velocity autocorrelation analysis | `autocorrelation_workflow` |

The qFoldIT adapter manifest remains `qfoldit.scientific-adapter/1.0`, adapter 0.2.0. It still names Action Envelope 1.0 and validation.completed 1.1.

## 2. QSIS policy

Do not replace the old adapter spec string or treat this aggregate adapter as a current QSIS provider. Keep the legacy manifest for compatibility. Create one QSIS Capability Manifest 0.1 per operation and pin each operation's input/output schema, implementation version, provider identity and provenance.

A draft `atomic.energy.single_point` manifest and parameter/result schemas are maintained in [UAG-SOS](https://github.com/qfoldit/UAG-SOS/tree/main/SCHEMAS/QSIS/examples). That candidate is an authoring reference; this repository does not yet expose a qFoldIT mission-bound QSIS Job Request / Job Result adapter.

## 3. Blocking implementation requirements

1. **Workspace isolation:** replace user-controlled path strings with opaque artifact references bound to a server-side workspace. Canonicalize paths and reject traversal and symlink escapes.
2. **Artifact identity:** return opaque artifact IDs, media types, formats, sizes and SHA-256 digests. Do not expose host absolute paths.
3. **Operation schemas:** define explicit input and output schemas for all eight operations, including validation rules, error/partial-result semantics and units.
4. **Scientific provenance:** record input structure digest, atom ordering, elements, cell/PBC, ASE/pymatgen versions, exact calculator/MLIP identity and revision, parameters, convergence, seed, hardware and output artifact digests.
5. **Calculator fallback:** preserve requested and actual calculator names, surface fallback warnings and fail closed when a mission locks a specific calculator.
6. **CPU/GPU claims:** the inspected `mcp_server.py` sets JAX/CUDA device environment variables to CPU-only values. GPU capability is not established by this source snapshot. Qualify CPU and GPU profiles separately before advertising GPU execution.
7. **Scientific authority:** this service is compute-only. Energy, forces, stress, convergence, MD trajectories and structural diagnostics do not issue Evidence and do not independently validate scientific claims.
8. **Current action/evidence migration:** new consequential work must bind Action Envelope 1.1 and deliver a Job Result to the qFoldIT control plane. Evidence 1.2 is issued only by the separate approved trust-plane publisher.

## 4. Qualification gates

- P0: repository, source commit, package and licence inventory.
- P1: per-operation QSIS manifests and resolvable input/output schemas.
- P2: static schema + cross-contract conformance.
- P3: offline adapter tests, path isolation and failure/retry tests.
- P4: bounded live smoke and retained artifact digests.
- P5: calculator-specific parity/benchmark profile.
- P6: approved mission integration and independent validator handoff.
- P7: security/licence/operations review and production release approval.

The current repository is below P2 for QSIS qualification. Do not use the presence of the draft example or a green legacy adapter check as qualification evidence.

## 5. Canonical references

- [Provider Adapter Conformance Standard](https://github.com/qfoldit/UAG-SOS/blob/main/STANDARDS/MCP/SCIENTIFIC-MCP-PROVIDER-ADAPTER-CONFORMANCE-v0.1.md)
- [Action/Evidence Migration Plan](https://github.com/qfoldit/UAG-SOS/blob/main/STANDARDS/MCP/LEGACY-ACTION-EVIDENCE-MIGRATION-PLAN-2026-11-11.md)
- [Atomic-MCP QSIS Provider Assessment](https://github.com/qfoldit/UAG-SOS/blob/main/SCHEMAS/QSIS/ATOMIC-MCP-QSIS-PROVIDER-ASSESSMENT-2026-11-11.md)
- [Provider Adapter Migration Register](https://github.com/qfoldit/UAG-SOS/blob/main/SCHEMAS/QSIS/provider-adapter-migration-register.json)
