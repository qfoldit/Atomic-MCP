from pathlib import Path

import pytest

from mcp_atomictoolkit.workspace import (
    normalize_tool_paths,
    resolve_workspace_path,
    sanitize_workspace_output,
)


def test_resolve_relative_input_inside_workspace(tmp_path: Path) -> None:
    sample = tmp_path / "input.xyz"
    sample.write_text("1\nH\nH 0 0 0\n", encoding="utf-8")
    resolved = resolve_workspace_path("input.xyz", tmp_path.resolve(), role="input")
    assert resolved == sample.resolve()


@pytest.mark.parametrize("value", [
    "/etc/passwd",
    "../outside.xyz",
    "nested/../../outside.xyz",
    r"C:\Windows\win.ini",
])
def test_rejects_absolute_and_traversal_paths(tmp_path: Path, value: str) -> None:
    with pytest.raises(PermissionError):
        resolve_workspace_path(value, tmp_path.resolve(), role="input")


def test_rejects_symlink_escape(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.xyz"
    outside.write_text("1\nH\nH 0 0 0\n", encoding="utf-8")
    link = workspace / "escape.xyz"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are unavailable in this environment")
    with pytest.raises(PermissionError):
        resolve_workspace_path("escape.xyz", workspace.resolve(), role="input")


def test_normalize_tool_paths_is_opt_in(tmp_path: Path, monkeypatch) -> None:
    sample = tmp_path / "input.xyz"
    sample.write_text("1\nH\nH 0 0 0\n", encoding="utf-8")
    monkeypatch.delenv("QFOLDIT_WORKSPACE_ROOT", raising=False)
    legacy, root = normalize_tool_paths("single_point_workflow", {"input_filepath": str(sample)})
    assert root is None
    assert legacy["input_filepath"] == str(sample)

    monkeypatch.setenv("QFOLDIT_WORKSPACE_ROOT", str(tmp_path))
    secure, root = normalize_tool_paths("single_point_workflow", {"input_filepath": "input.xyz"})
    assert root == tmp_path.resolve()
    assert secure["input_filepath"] == str(sample.resolve())


def test_output_path_parent_is_created_inside_workspace(tmp_path: Path) -> None:
    target = resolve_workspace_path("results/run/output.extxyz", tmp_path.resolve(), role="output")
    assert target.parent.is_dir()
    assert target == (tmp_path / "results/run/output.extxyz").resolve()


def test_workspace_output_redacts_paths_and_preserves_artifact_reference(tmp_path: Path) -> None:
    artifact = tmp_path / "out.extxyz"
    artifact.write_text("data", encoding="utf-8")
    result = {
        "output_filepath": str(artifact.resolve()),
        "outputs": {"trajectory": str(artifact.resolve()), "output_dir": str(tmp_path.resolve())},
        "artifacts": [{
            "id": "art_0123456789abcdef0123456789abcdef",
            "filepath": str(artifact.resolve()),
            "sha256": "sha256:" + "a" * 64,
        }],
    }

    safe = sanitize_workspace_output(result, tmp_path.resolve())
    assert "output_filepath" not in safe
    assert "filepath" not in safe["artifacts"][0]
    assert safe["outputs"]["trajectory"] == "artifact://art_0123456789abcdef0123456789abcdef"
    assert "output_dir" not in safe["outputs"]
