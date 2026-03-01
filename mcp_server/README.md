# KIMI DS Sandbox MCP Server

Provides sandboxed Python execution for the KIMI Data Science Agent team.
Each pipeline run gets an isolated Python **venv** and a dedicated workspace
directory — no Docker required.

---

## Quick Start

### 1. Install MCP server dependencies

```bash
pip install -r mcp_server/requirements.txt
```

### 2. Verify the server loads

```bash
python mcp_server/server.py --help        # should show FastMCP info
python -m py_compile mcp_server/server.py # zero output = no syntax errors
```

### 3. Inspect available tools (optional)

```bash
npx @modelcontextprotocol/inspector python mcp_server/server.py
```
Opens a browser UI listing all 6 sandbox tools.

---

## Connecting to Kimi CLI

Add the following `mcp_servers` block to each agent YAML (already done by `install.sh`):

```yaml
mcp_servers:
  - name: ds_sandbox
    transport: stdio
    command: python
    args:
      - ~/.ds-agents/mcp_server/server.py
```

If your Kimi CLI version does not support `mcp_servers:` in YAML, agents can
call the server via the Shell tool as a fallback:

```bash
# Fallback: call server as a CLI subprocess using the MCP JSON-RPC protocol
echo '{"tool":"sandbox_execute_python","params":{"code":"print(42)","session_id":"test"}}' | \
  python ~/.ds-agents/mcp_server/server.py
```

---

## How It Works

```
Kimi Agent
  │ calls MCP tool
  ▼
kimi_ds_sandbox_mcp (this server — stdio)
  │ subprocess.run(python_in_venv, code, timeout=180)
  ▼
~/.ds-agents/workspaces/<session_id>/
  ├── venv/          ← isolated Python environment (per session)
  └── files/         ← all agent output files (per session)
```

- **Per-session isolation**: different pipeline runs never share files.
- **Venv reuse**: calling the same `session_id` reuses the existing venv — packages need not be reinstalled.
- **Timeout protection**: all code executions have a configurable timeout (default 180 s).
- **Path-traversal guard**: all file paths are validated to stay inside the session workspace.

---

## 6 Available Tools

| Tool | Description |
|------|-------------|
| `sandbox_execute_python` | Run Python code in the session venv; returns stdout/stderr/exit_code |
| `sandbox_install_package` | pip install packages into the session venv |
| `sandbox_read_file` | Read a file from the session workspace |
| `sandbox_write_file` | Write a file to the session workspace |
| `sandbox_list_files` | List all files in the session workspace |
| `sandbox_reset` | Clear output files (optionally also wipe the venv) |

---

## Session ID Convention

Root generates a session ID at the start of each pipeline run:

```
ds_YYYYMMDD_HHMMSS   (e.g. ds_20260301_163000)
```

All agents in the same run share this ID, so files written by the Analyst
are visible to the Modeler without any extra copying.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` in sandbox | Package not installed in session venv | Call `sandbox_install_package` first |
| `TimeoutExpired` | Script takes > 180 s | Set `timeout=300` or break into smaller scripts |
| `Path traversal detected` | Agent tried to access files outside workspace | Use relative paths only |
| `venv.create` fails on Windows | Python not on PATH correctly | Ensure `python` resolves to Python 3.9+ |
