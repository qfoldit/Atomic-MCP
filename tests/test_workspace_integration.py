from pathlib import Path

from mcp_atomictoolkit.mcp_server import _run_tool


def test_workspace_mode_returns_artifact_identity_without_absolute_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("QFOLDIT_WORKSPACE_ROOT", str(tmp_path))

    def _write(output_filepath: str) -> dict:
        output = Path(output_filepath)
        output.write_text("atomic artifact", encoding="utf-8")
        return {"output_filepath": str(output)}

    result = _run_tool(
        "build_structure_workflow",
        _write,
        output_filepath="results/output.extxyz",
    )

    assert result["artifacts"]
    artifact = result["artifacts"][0]
    assert artifact["sha256"].startswith("sha256:")
    assert artifact["size_bytes"] == len(b"atomic artifact")
    assert "filepath" not in artifact
    assert str(tmp_path.resolve()) not in repr(result)


def test_workspace_path_rejection_redacts_error_details(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("QFOLDIT_WORKSPACE_ROOT", str(tmp_path))
    result = _run_tool(
        "single_point_workflow",
        lambda **kwargs: {"unexpected": True},
        input_filepath="../outside.xyz",
    )

    assert result["status"] == "error"
    assert "error_report_filepath" not in result
    assert result["error"]["traceback"] == "<redacted in workspace mode>"
    assert str(tmp_path.resolve()) not in repr(result)
