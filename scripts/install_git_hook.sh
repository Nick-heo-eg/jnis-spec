#!/bin/sh
# scripts/install_git_hook.sh
# Installs J-NIS enforcement hooks.
#
# Note: if core.hooksPath is set globally (e.g. ~/.git-hooks),
# local .git/hooks are bypassed. In that case, hooks are installed
# to the global hooks directory alongside existing hooks.

REPO_ROOT="$(git rev-parse --show-toplevel)"
GLOBAL_HOOKS="$(git config --global core.hooksPath 2>/dev/null)"

if [ -n "$GLOBAL_HOOKS" ]; then
    HOOKS_DIR="$GLOBAL_HOOKS"
    echo "Note: core.hooksPath is set globally — installing to $HOOKS_DIR"
else
    HOOKS_DIR="$REPO_ROOT/.git/hooks"
fi

GATE_CMD="python3 $REPO_ROOT/enforcement/jnis_gate.py"

# pre-commit
PRE_COMMIT="$HOOKS_DIR/pre-commit"
if [ -f "$PRE_COMMIT" ]; then
    # Append if not already present
    grep -q "jnis_gate" "$PRE_COMMIT" || cat >> "$PRE_COMMIT" << EOF

# J-NIS enforcement
$GATE_CMD
if [ \$? -ne 0 ]; then
    echo "JNIS_HOOK: commit blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
else
    cat > "$PRE_COMMIT" << EOF
#!/bin/sh
$GATE_CMD
if [ \$? -ne 0 ]; then
    echo "JNIS_HOOK: commit blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
    chmod +x "$PRE_COMMIT"
fi

# commit-msg
COMMIT_MSG="$HOOKS_DIR/commit-msg"
if [ -f "$COMMIT_MSG" ]; then
    grep -q "jnis_gate" "$COMMIT_MSG" || cat >> "$COMMIT_MSG" << EOF

# J-NIS enforcement
$GATE_CMD
if [ \$? -ne 0 ]; then
    echo "JNIS_HOOK: commit-msg blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
else
    cat > "$COMMIT_MSG" << EOF
#!/bin/sh
$GATE_CMD
if [ \$? -ne 0 ]; then
    echo "JNIS_HOOK: commit-msg blocked — no valid trace or gate invariants violated"
    exit 1
fi
EOF
    chmod +x "$COMMIT_MSG"
fi

echo "JNIS hooks installed to: $HOOKS_DIR"
echo "  pre-commit  — gate check before commit"
echo "  commit-msg  — gate check on message stage"
echo "git commit now requires a valid J-NIS trace in logs/trace.jsonl"
