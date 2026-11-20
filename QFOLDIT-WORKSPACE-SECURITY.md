# qFoldIT Atomic-MCP Workspace Security Mode

## Enablement

Configure the service environment:

```bash
QFOLDIT_WORKSPACE_ROOT=/srv/qfoldit/atomic-workspaces
```

The directory must exist, be an absolute path and be writable only by the service identity. Mount or provision a separate workspace per trusted isolation boundary. The variable is opt-in; unset preserves legacy file-path behavior.

## Behavior

- MCP path parameters must be relative to the configured workspace.
- Absolute paths, drive-qualified paths and any `..` segment are rejected.
- Existing input paths must resolve to regular files under the root.
- Output parents and directories are created only under the root.
- Symlinks whose resolved target escapes the workspace are rejected.
- Registered artifacts are SHA-256 hashed and include byte size.
- Workspace-mode responses omit absolute `filepath` fields and use opaque artifact IDs/download URLs.
- Error responses omit the error-report file path and traceback, and redact caller-supplied path parameters.

## Important limits

This is a path-containment feature, not complete service security or a QSIS adapter. It does not provide:
- tenant or user authentication and authorization;
- per-tenant workspace provisioning or quotas;
- durable artifact/job registry;
- race-resistant descriptor-relative filesystem operations against a hostile concurrent local process;
- authenticated/expiring artifact download links;
- mission Inception/Contract and Action Envelope 1.1 binding;
- QSIS Job Request/Result transport or independent validation.

The server operator must protect the workspace and download endpoint at the deployment/network boundary. A path-containment test does not establish multi-tenant production isolation.
