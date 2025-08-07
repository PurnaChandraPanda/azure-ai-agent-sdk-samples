#!/usr/bin/env bash
# Adds all changes and pushes to origin/main.
# Usage: ./git_push.sh "your commit message"

set -euo pipefail

OWNER="PurnaChandraPanda"      # ← adapt
REPO="azure-ai-agent-sdk-samples"          # ← adapt
BRANCH="main"
MSG="${1:-}"

if [[ -z $MSG ]]; then
    read -rp "Commit message: " MSG
fi


git status
git add .
git commit -m "$MSG"
# add or update remote
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "https://github.com/${OWNER}/${REPO}.git"
else
    git remote add origin "https://github.com/${OWNER}/${REPO}.git"
fi
git push -u origin "$BRANCH"