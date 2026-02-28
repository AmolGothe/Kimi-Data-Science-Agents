#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Installing KIMI Data Science Multi-Agent System..."

TARGET_DIR="$HOME/.ds-agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/prompts"

echo "📋 Copying agent YAML configs..."
cp "$SCRIPT_DIR"/*.yaml "$TARGET_DIR/"

echo "📝 Copying system prompts..."
cp "$SCRIPT_DIR/prompts"/*.md "$TARGET_DIR/prompts/"

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
echo "Example usage:"
echo "  kimi-ds-team"
echo "  > 'Analyze the file ./data/sales.csv and predict monthly revenue'"
echo ""
echo "Agents available:"
echo "  📊 Analyst   — EDA, cleaning, feature engineering"
echo "  🧠 Modeler   — Model training and hyperparameter tuning"
echo "  ⚖️  Evaluator — Model validation and metrics"
echo "  📈 Reporter  — Visualizations and final report"
echo "  ⚙️  MLOps    — FastAPI deployment and Docker packaging"
