#!/bin/sh
# scripts/install_git_hook.sh
# Configures this repository to use .githooks/ as the local hooks directory.
# Affects only this repository. No global git configuration is modified.

REPO_ROOT="$(git rev-parse --show-toplevel)"

git config core.hooksPath .githooks
chmod +x "$REPO_ROOT/.githooks/pre-commit"
chmod +x "$REPO_ROOT/.githooks/commit-msg"

echo "JNIS hooks configured (repository-scoped only):"
echo "  core.hooksPath = .githooks"
echo "  .githooks/pre-commit"
echo "  .githooks/commit-msg"
echo ""
echo "Hooks are repository-scoped (no global hooks are used)"
echo "git commit in this repo now requires a valid J-NIS trace in logs/trace.jsonl"
