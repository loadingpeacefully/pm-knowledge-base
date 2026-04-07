#!/bin/bash
# PM·Control — start the mission control dashboard
# Usage: cd /Users/suneetjagdev/pm-knowledge-base && ./control/run.sh

set -e
cd "$(dirname "$0")/.."

echo ""
echo "  PM·Control"
echo "  ─────────────────────────────"
echo ""
echo "  Generating dashboard data..."
python3 control/data.py

echo ""
echo "  Starting server on port 8081..."
echo "  Open: http://localhost:8081/control/"
echo ""
echo "  To update data while running:"
echo "  python3 control/data.py   (in another terminal)"
echo ""
echo "  Learning dashboard (port 8080) is NOT affected."
echo ""

python3 -m http.server 8081
