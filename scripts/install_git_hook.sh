#!/bin/sh
# scripts/install_git_hook.sh
# Installs J-NIS enforcement hooks into .git/hooks/
# After installation, git commit requires a valid J-NIS trace.

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

# pre-commit: gate check before commit is created
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/sh
python3 enforcement/jnis_gate.py
if [ $? -ne 0 ]; then
    echo "JNIS_HOOK: commit blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
chmod +x "$HOOKS_DIR/pre-commit"

# commit-msg: secondary check to prevent message-based bypass
cat > "$HOOKS_DIR/commit-msg" << 'EOF'
#!/bin/sh
python3 enforcement/jnis_gate.py
if [ $? -ne 0 ]; then
    echo "JNIS_HOOK: commit-msg blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
chmod +x "$HOOKS_DIR/commit-msg"

echo "JNIS hooks installed:"
echo "  .git/hooks/pre-commit"
echo "  .git/hooks/commit-msg"
echo "git commit now requires a valid J-NIS trace in logs/trace.jsonl"
