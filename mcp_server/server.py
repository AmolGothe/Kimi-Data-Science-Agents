#!/usr/bin/env python3
"""
kimi_ds_sandbox_mcp — MCP Sandbox Server for KIMI Data Science Agents.

Provides sandboxed Python code execution using per-session Python virtual
environments (venv). No Docker required. Each pipeline run gets its own
isolated venv and workspace directory under ~/.ds-agents/workspaces/.

Transport: stdio (launched as a subprocess by Kimi CLI)
"""

import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# ── Server initialisation ─────────────────────────────────────────────────────

mcp = FastMCP("kimi_ds_sandbox_mcp")

WORKSPACE_ROOT: Path = Path.home() / ".ds-agents" / "workspaces"
WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _files_dir(session_id: str) -> Path:
    """Return (and create) the file workspace for a session."""
    d = WORKSPACE_ROOT / session_id / "files"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _venv_dir(session_id: str) -> Path:
    return WORKSPACE_ROOT / session_id / "venv"


def _python_bin(session_id: str) -> str:
    vd = _venv_dir(session_id)
    if sys.platform == "win32":
        return str(vd / "Scripts" / "python.exe")
    return str(vd / "bin" / "python")


def _ensure_venv(session_id: str) -> str:
    """Create the session venv if it does not exist; return python path."""
    python_bin = _python_bin(session_id)
    if not Path(python_bin).exists():
        venv.create(str(_venv_dir(session_id)), with_pip=True, clear=False)
    return python_bin


def _safe_path(workspace: Path, relative: str) -> Optional[Path]:
    """Resolve and verify the path stays inside the workspace."""
    resolved = (workspace / relative).resolve()
    if not str(resolved).startswith(str(workspace.resolve())):
        return None
    return resolved


# ── Pydantic input models ─────────────────────────────────────────────────────


class ExecutePythonInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(
        ...,
        description="Python source code to run in the sandbox (e.g. 'import pandas as pd; print(pd.__version__)')",
        min_length=1,
    )
    session_id: str = Field(
        ...,
        description="Unique session ID shared by all agents in one pipeline run (e.g. 'ds_20260301_163000')",
        min_length=1,
        max_length=64,
    )
    timeout: Optional[int] = Field(
        default=180,
        description="Execution timeout in seconds (default 180, max 600)",
        ge=10,
        le=600,
    )


class InstallPackageInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    packages: List[str] = Field(
        ...,
        description="pip package names to install (e.g. ['pandas', 'scikit-learn==1.4.0'])",
        min_length=1,
    )
    session_id: str = Field(..., description="Session identifier", min_length=1, max_length=64)


class FilePathInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        ...,
        description="File path relative to the session workspace (e.g. 'processed_data.csv' or 'reports/figures/roc.png')",
        min_length=1,
    )
    session_id: str = Field(..., description="Session identifier", min_length=1, max_length=64)


class WriteFileInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(..., description="Relative file path inside the session workspace", min_length=1)
    content: str = Field(..., description="Text content to write (UTF-8)")
    session_id: str = Field(..., description="Session identifier", min_length=1, max_length=64)


class ListFilesInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    session_id: str = Field(..., description="Session identifier", min_length=1, max_length=64)
    directory: Optional[str] = Field(
        default="",
        description="Sub-directory to list (default '' = workspace root)",
    )


class ResetSandboxInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    session_id: str = Field(..., description="Session identifier to reset", min_length=1, max_length=64)
    keep_venv: Optional[bool] = Field(
        default=True,
        description="Keep the venv (installed packages) and only wipe output files. Set False to do a full reset.",
    )


# ── Tools ─────────────────────────────────────────────────────────────────────


@mcp.tool(
    name="sandbox_execute_python",
    annotations={
        "title": "Execute Python in Sandbox",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def sandbox_execute_python(params: ExecutePythonInput) -> str:
    """Execute Python code in an isolated venv sandbox for the given session.

    The code runs with the current working directory set to the session
    workspace, so relative file paths work as expected. stdout, stderr,
    and the exit code are returned as JSON.

    Args:
        params (ExecutePythonInput):
            - code (str): Python source code to execute.
            - session_id (str): Pipeline session identifier.
            - timeout (int): Max seconds to wait (default 180).

    Returns:
        str: JSON — {"stdout": str, "stderr": str, "exit_code": int, "workspace": str}
             exit_code == 0  → success
             exit_code == -1 → timeout
             exit_code == -2 → internal MCP server error

    Examples:
        - "Run my EDA script" → code="import pandas as pd\ndf=pd.read_csv('data.csv')\nprint(df.info())"
        - "Check if XGBoost imported" → code="import xgboost; print(xgboost.__version__)"
    """
    workspace = _files_dir(params.session_id)
    try:
        python_bin = _ensure_venv(params.session_id)
        result = subprocess.run(
            [python_bin, "-c", params.code],
            capture_output=True,
            text=True,
            timeout=params.timeout,
            cwd=str(workspace),
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
        )
        return json.dumps(
            {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "workspace": str(workspace),
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return json.dumps(
            {
                "stdout": "",
                "stderr": f"Error: Execution timed out after {params.timeout}s. "
                          "Consider splitting into smaller scripts or increasing timeout.",
                "exit_code": -1,
                "workspace": str(workspace),
            }
        )
    except Exception as exc:
        return json.dumps(
            {"stdout": "", "stderr": f"Error: {type(exc).__name__}: {exc}", "exit_code": -2, "workspace": ""}
        )


@mcp.tool(
    name="sandbox_install_package",
    annotations={
        "title": "Install Python Packages in Sandbox",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def sandbox_install_package(params: InstallPackageInput) -> str:
    """Install Python packages with pip into the session's virtual environment.

    Packages are persisted in the venv; they do not need to be reinstalled
    on subsequent runs for the same session_id unless sandbox_reset is called
    with keep_venv=False.

    Args:
        params (InstallPackageInput):
            - packages (List[str]): Package names (e.g. ["pmdarima", "prophet"]).
            - session_id (str): Session identifier.

    Returns:
        str: JSON — {"installed": list, "stdout": str, "stderr": str, "exit_code": int}

    Error: Returns exit_code != 0 with details in stderr if installation fails.
    """
    try:
        python_bin = _ensure_venv(params.session_id)
        result = subprocess.run(
            [python_bin, "-m", "pip", "install", "--quiet"] + params.packages,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return json.dumps(
            {
                "installed": params.packages,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            },
            indent=2,
        )
    except subprocess.TimeoutExpired:
        return json.dumps(
            {"installed": [], "stdout": "", "stderr": "Error: pip install timed out (300s)", "exit_code": -1}
        )
    except Exception as exc:
        return json.dumps({"installed": [], "stdout": "", "stderr": f"Error: {exc}", "exit_code": -2})


@mcp.tool(
    name="sandbox_read_file",
    annotations={
        "title": "Read File from Sandbox Workspace",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sandbox_read_file(params: FilePathInput) -> str:
    """Read a text file from the session's sandbox workspace.

    Args:
        params (FilePathInput):
            - path (str): Relative path (e.g. 'eda_report.md', 'reports/figures/roc.png').
            - session_id (str): Session identifier.

    Returns:
        str: File contents as text, or "Error: ..." on failure.

    Error: "Error: File not found: <path>" if the file does not exist.
           "Error: Path traversal detected" if path escapes workspace.
    """
    workspace = _files_dir(params.session_id)
    file_path = _safe_path(workspace, params.path)
    if file_path is None:
        return "Error: Path traversal detected — access outside workspace is not allowed."
    if not file_path.exists():
        return f"Error: File not found: {params.path}"
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


@mcp.tool(
    name="sandbox_write_file",
    annotations={
        "title": "Write File to Sandbox Workspace",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sandbox_write_file(params: WriteFileInput) -> str:
    """Write UTF-8 text content to a file in the session's sandbox workspace.

    Creates any missing parent directories automatically.

    Args:
        params (WriteFileInput):
            - path (str): Relative path (e.g. 'feature_schema.json').
            - content (str): Text to write.
            - session_id (str): Session identifier.

    Returns:
        str: JSON — {"success": true, "path": str, "bytes_written": int}
             or "Error: ..." on failure.
    """
    workspace = _files_dir(params.session_id)
    file_path = _safe_path(workspace, params.path)
    if file_path is None:
        return "Error: Path traversal detected."
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(params.content, encoding="utf-8")
        return json.dumps(
            {
                "success": True,
                "path": str(file_path.relative_to(workspace)),
                "bytes_written": len(params.content.encode("utf-8")),
            }
        )
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


@mcp.tool(
    name="sandbox_list_files",
    annotations={
        "title": "List Files in Sandbox Workspace",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sandbox_list_files(params: ListFilesInput) -> str:
    """List all files in the session's sandbox workspace (recursive).

    Args:
        params (ListFilesInput):
            - session_id (str): Session identifier.
            - directory (str): Optional sub-directory (default '' = workspace root).

    Returns:
        str: JSON — {"workspace": str, "files": [{"path": str, "size_bytes": int}], "count": int}
    """
    workspace = _files_dir(params.session_id)
    base = _safe_path(workspace, params.directory) if params.directory else workspace.resolve()
    if base is None:
        return "Error: Path traversal detected."
    try:
        files = []
        if base.exists():
            for f in sorted(base.rglob("*")):
                if f.is_file():
                    files.append(
                        {"path": str(f.relative_to(workspace)), "size_bytes": f.stat().st_size}
                    )
        return json.dumps({"workspace": str(workspace), "files": files, "count": len(files)}, indent=2)
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


@mcp.tool(
    name="sandbox_reset",
    annotations={
        "title": "Reset Sandbox Session",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def sandbox_reset(params: ResetSandboxInput) -> str:
    """Reset the sandbox for a session — wipes all output files.

    By default (keep_venv=True) only the files/ directory is cleared;
    the venv (and all installed packages) is preserved for speed.

    Args:
        params (ResetSandboxInput):
            - session_id (str): Session to reset.
            - keep_venv (bool): Preserve installed packages (default True).

    Returns:
        str: JSON — {"reset": true, "kept_venv": bool, "session_id": str}
    """
    try:
        session_root = WORKSPACE_ROOT / params.session_id
        files_dir = session_root / "files"
        if files_dir.exists():
            shutil.rmtree(str(files_dir))
        files_dir.mkdir(parents=True, exist_ok=True)
        if not params.keep_venv:
            venv_d = session_root / "venv"
            if venv_d.exists():
                shutil.rmtree(str(venv_d))
        return json.dumps(
            {"reset": True, "kept_venv": params.keep_venv, "session_id": params.session_id}
        )
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()  # stdio transport — Kimi CLI launches this as a subprocess
