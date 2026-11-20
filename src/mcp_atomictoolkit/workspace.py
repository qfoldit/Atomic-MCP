"""Opt-in, workspace-rooted file handling for Atomic-MCP.

Set QFOLDIT_WORKSPACE_ROOT to an existing absolute directory to enable strict
path handling. When unset, legacy path behavior is preserved for compatibility.
This module is not an authentication or tenant-isolation layer.
"""
from __future__ import annotations

import os
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, Optional

WORKSPACE_ENV = "QFOLDIT_WORKSPACE_ROOT"

_TOOL_PATH_ROLES = {
    "build_structure_workflow": {"output_filepath": "output"},
    "analyze_structure_workflow": {"filepath": "input", "output_dir": "directory"},
    "write_structure_workflow": {"filepath": "output"},
    "optimize_structure_workflow": {"input_filepath": "input", "output_filepath": "output"},
    "single_point_workflow": {"input_filepath": "input"},
    "run_md_workflow": {
        "input_filepath": "input",
        "output_trajectory_filepath": "output",
        "log_filepath": "output",
        "summary_filepath": "output",
    },
    "analyze_trajectory_workflow": {"filepath": "input", "output_dir": "directory"},
    "autocorrelation_workflow": {"filepath": "input", "output_dir": "directory"},
    "create_download_artifact": {"filepath": "input"},
}

_PATH_PARAMETER_KEYS = {
    "filepath", "input_filepath", "output_filepath", "output_trajectory_filepath",
    "log_filepath", "summary_filepath", "output_dir",
}


def get_workspace_root() -> Optional[Path]:
    """Return the configured workspace root, or None for legacy mode."""
    raw = os.environ.get(WORKSPACE_ENV, "").strip()
    if not raw:
        return None
    configured = Path(raw).expanduser()
    if not configured.is_absolute():
        raise ValueError(f"{WORKSPACE_ENV} must be an absolute path")
    try:
        root = configured.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValueError(f"{WORKSPACE_ENV} must point to an existing directory") from exc
    if not root.is_dir():
        raise ValueError(f"{WORKSPACE_ENV} must point to a directory")
    return root


def _assert_contained(path: Path, root: Path) -> Path:
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise PermissionError("Path resolves outside the configured workspace") from exc
    return resolved


def resolve_workspace_path(value: str | Path, root: Path, *, role: str) -> Path:
    """Resolve an input/output path under root; reject absolute paths and traversal."""
    raw = str(value)
    if not raw or "\x00" in raw:
        raise ValueError("Workspace path must be non-empty and contain no NUL bytes")

    candidate = Path(raw)
    windows_candidate = PureWindowsPath(raw)
    if candidate.is_absolute() or windows_candidate.is_absolute() or windows_candidate.drive:
        raise PermissionError("Absolute paths are not allowed in workspace mode")
    if ".." in candidate.parts:
        raise PermissionError("Parent-directory traversal is not allowed in workspace mode")

    resolved = _assert_contained(root / candidate, root)

    if role == "input":
        if not resolved.exists() or not resolved.is_file():
            raise FileNotFoundError("Workspace input artifact does not exist or is not a file")
        return resolved
    if role == "directory":
        resolved.mkdir(parents=True, exist_ok=True)
        resolved = _assert_contained(resolved, root)
        if not resolved.is_dir():
            raise ValueError("Workspace output directory target is not a directory")
        return resolved
    if role == "output":
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved = _assert_contained(resolved, root)
        if resolved.exists() and not resolved.is_file():
            raise ValueError("Workspace output file target is not a regular file")
        return resolved
    raise ValueError(f"Unsupported workspace path role: {role}")


def ensure_file_in_workspace(value: str | Path, root: Path) -> Path:
    """Validate an internally generated absolute file path against workspace root."""
    path = Path(value).resolve(strict=True)
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise PermissionError("Artifact is outside the configured workspace") from exc
    if not path.is_file():
        raise FileNotFoundError("Workspace artifact is not a regular file")
    return path


def normalize_tool_paths(tool_name: str, kwargs: Dict[str, Any]) -> tuple[Dict[str, Any], Optional[Path]]:
    """Return implementation arguments with workspace-safe absolute paths."""
    root = get_workspace_root()
    if root is None:
        return dict(kwargs), None

    normalized = dict(kwargs)
    for key, role in _TOOL_PATH_ROLES.get(tool_name, {}).items():
        value = normalized.get(key)
        if value is None:
            continue
        if not isinstance(value, (str, Path)):
            raise TypeError(f"{key} must be a string path")
        normalized[key] = str(resolve_workspace_path(value, root, role=role))
    return normalized, root


def redact_path_parameters(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Remove caller-supplied path values from error reports in workspace mode."""
    redacted = dict(kwargs)
    for key in _PATH_PARAMETER_KEYS:
        if key in redacted and redacted[key] is not None:
            redacted[key] = "<workspace-path-redacted>"
    return redacted


def sanitize_workspace_output(value: Any, root: Path) -> Any:
    """Remove host filesystem paths and link generated files by opaque artifact ID."""
    artifact_ids: Dict[str, str] = {}

    def collect(node: Any) -> None:
        if isinstance(node, dict):
            artifact_id = node.get("id")
            filepath = node.get("filepath")
            if isinstance(artifact_id, str) and artifact_id.startswith("art_") and isinstance(filepath, str):
                try:
                    canonical = str(ensure_file_in_workspace(filepath, root))
                    artifact_ids[canonical] = f"artifact://{artifact_id}"
                except (OSError, ValueError, PermissionError):
                    pass
            for child in node.values():
                collect(child)
        elif isinstance(node, list):
            for child in node:
                collect(child)

    collect(value)

    def scrub(node: Any) -> Any:
        if isinstance(node, dict):
            cleaned: Dict[str, Any] = {}
            for child_key, child_value in node.items():
                if (
                    child_key == "filepath"
                    or child_key.endswith("_filepath")
                    or child_key in {"output_dir", "error_report_filepath"}
                ):
                    continue
                cleaned[child_key] = scrub(child_value)
            return cleaned
        if isinstance(node, list):
            return [scrub(item) for item in node]
        if isinstance(node, str) and Path(node).is_absolute():
            try:
                canonical = str(Path(node).resolve(strict=False))
                Path(canonical).relative_to(root)
                return artifact_ids.get(canonical, "<workspace-path-redacted>")
            except (OSError, ValueError):
                return node
        return node

    return scrub(value)
