# qFoldIT Atomic MCP Platform Integration

`Atomic-MCP` is an atomistic-science capability provider in the qFoldIT Scientific Agent Mesh.

## Capability boundary

```text
Mission / Agent
    -> atomic structure workflow
    -> optimization / MD / analysis
    -> scientific artifact
    -> evidence / provenance
    -> mission result
```

The service provides scientific computation and artifact generation. Mission lifecycle, runtime presentation and reward policy remain outside the solver boundary.

## Contract family

When outputs cross into qFoldIT mission workflows they should map to:

- `qfoldit.scientific-state/1.0`
- `qfoldit.evidence/1.0`
- `qfoldit.event/1.0`

Spatial/3D exports may map into `qfoldit.uag/1.0`.

## Provenance

Scientific libraries, models, datasets and external services retain their original licenses and attribution. qFoldIT platform integration should retain a source/provenance reference for every artifact used in an evidence record.
