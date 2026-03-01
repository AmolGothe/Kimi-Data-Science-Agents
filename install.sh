#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Installing KIMI Data Science Multi-Agent System..."

TARGET_DIR="$HOME/.ds-agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/prompts"
mkdir -p "$TARGET_DIR/mcp_server"

echo "📋 Copying agent YAML configs..."
cp "$SCRIPT_DIR"/*.yaml "$TARGET_DIR/"

echo "📝 Copying system prompts..."
cp "$SCRIPT_DIR/prompts"/*.md "$TARGET_DIR/prompts/"

echo "🔌 Copying MCP sandbox server..."
cp "$SCRIPT_DIR/mcp_server/server.py"       "$TARGET_DIR/mcp_server/"
cp "$SCRIPT_DIR/mcp_server/requirements.txt" "$TARGET_DIR/mcp_server/"
cp "$SCRIPT_DIR/mcp_server/README.md"        "$TARGET_DIR/mcp_server/"

echo "📦 Installing MCP server dependencies..."
if command -v pip &>/dev/null; then
    pip install -q -r "$TARGET_DIR/mcp_server/requirements.txt"
    echo "   ✅ mcp[cli] and pydantic installed"
else
    echo "   ⚠️  pip not found — install manually:"
    echo "       pip install -r ~/.ds-agents/mcp_server/requirements.txt"
fi

echo "🔍 Verifying MCP server syntax..."
if command -v python &>/dev/null; then
    python -m py_compile "$TARGET_DIR/mcp_server/server.py" && \
        echo "   ✅ server.py passed syntax check" || \
        echo "   ⚠️  server.py syntax error — check the file manually"
else
    echo "   ⚠️  python not found on PATH — skipping syntax check"
fi

echo "⚙️ Adding shell alias (kimi-ds-team)..."

if ! grep -q "kimi-ds-team" "$HOME/.bashrc" 2>/dev/null; then
    echo "alias kimi-ds-team='kimi --agent-file ~/.ds-agents/root.yaml'" >> "$HOME/.bashrc"
fi

if ! grep -q "kimi-ds-team" "$HOME/.zshrc" 2>/dev/null; then
    echo "alias kimi-ds-team='kimi --agent-file ~/.ds-agents/root.yaml'" >> "$HOME/.zshrc"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Reload your shell:   source ~/.bashrc  (or ~/.zshrc)"
echo "  2. Start the DS team:   kimi-ds-team"
echo ""
echo "Sandbox:"
echo "  Session workspaces:   ~/.ds-agents/workspaces/<session_id>/files/"
echo "  MCP server:           ~/.ds-agents/mcp_server/server.py"
echo "  (Optional) Inspect:   npx @modelcontextprotocol/inspector python ~/.ds-agents/mcp_server/server.py"
echo ""
echo "Example usage:"
echo "  kimi-ds-team"
echo "  > 'Analyze the file ./data/sales.csv and predict monthly revenue'"
echo "  > 'Forecast the next 12 months of sales from ./data/monthly_sales.csv'"
echo ""
echo "Agents available:"
echo "  📊 Analyst    — EDA, cleaning, feature engineering"
echo "  🧠 Modeler    — Model training and hyperparameter tuning"
echo "  🔮 Forecaster — ARIMA, Prophet, XGBoost time series forecasting"
echo "  ⚖️  Evaluator  — Model validation and quality gate"
echo "  📈 Reporter   — Visualizations and final report"
echo "  ⚙️  MLOps     — FastAPI deployment and packaging"
