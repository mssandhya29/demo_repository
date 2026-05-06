#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
# Appian MCP Server — one-time setup script
# Run once, then register with Claude Code.
# ─────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"

echo "==> Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$SCRIPT_DIR/.venv/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "✅  Setup complete."
echo ""
echo "Next steps:"
echo ""
echo "  1. Set your Appian credentials:"
echo "       export APPIAN_BASE_URL='https://your-instance.appiancloud.com/suite'"
echo "       export APPIAN_API_KEY='your-service-account-api-key'"
echo ""
echo "  2. Register the MCP server with Claude Code:"
echo "       claude mcp add appian-server \\"
echo "         -e APPIAN_BASE_URL=\"\$APPIAN_BASE_URL\" \\"
echo "         -e APPIAN_API_KEY=\"\$APPIAN_API_KEY\" \\"
echo "         -- $SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/appian_mcp_server.py"
echo ""
echo "  3. Verify it's registered:"
echo "       claude mcp list"
echo ""
echo "  4. Start Claude Code and talk to Appian in natural language:"
echo "       claude"
