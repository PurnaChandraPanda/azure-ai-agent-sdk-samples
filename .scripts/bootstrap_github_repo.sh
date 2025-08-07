#!/usr/bin/env bash
# Creates a public GitHub repo from the current folder,
# pushes local sources, then locks the main branch so that
# only the OWNER can push; everyone else must use a PR.

set -euo pipefail

OWNER="PurnaChandraPanda"      # <- adapt
REPO="azure-ai-agent-sdk-samples"          # <- adapt
REPO_DESCRIPTION="Azure AI Agent client side end-to-end samples"
DEFAULT_BRANCH="main"

#####################################################################
# Prerequisites
#   gh auth login   test123-sampl# once, with a PAT that has `repo` scope
#   git config --global init.defaultBranch "${DEFAULT_BRANCH}"
#####################################################################

# # 1) create the repo (public)
# gh repo create "${OWNER}/${REPO}" --public --confirm
# 1) create the repo only if it does not already exist
if gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
    echo "🛈 Repository ${OWNER}/${REPO} already exists - skipping creation"
else
    gh repo create "${OWNER}/${REPO}" --public --description "${REPO_DESCRIPTION}" -y
    echo "✅ Repository ${OWNER}/${REPO} created"
fi


## Derive the project root where the script is run
SAFE_DIR="${PWD}"

echo "SAFE_DIR: $SAFE_DIR"

# Check if the directory is already marked as safe
if ! git config --global --get-all safe.directory | grep -Fxq "$SAFE_DIR"; then
    git config --global --add safe.directory "$SAFE_DIR"
    echo "Added $SAFE_DIR to git safe.directory"
else
    echo "$SAFE_DIR is already marked as safe"
fi

# 2) push current code
# initialize only once
if [ ! -d .git ]; then
    git init
fi
git add .
git commit -m "initial commit"
git branch -M "${DEFAULT_BRANCH}"
# add or update remote
if git remote get-url origin >/dev/null 2>&1; then
    git remote set-url origin "https://github.com/${OWNER}/${REPO}.git"
else
    git remote add origin "https://github.com/${OWNER}/${REPO}.git"
fi
git push -u origin "${DEFAULT_BRANCH}"

# 3) protect the default branch
# gh api -X PUT "repos/${OWNER}/${REPO}/branches/${DEFAULT_BRANCH}/protection" \
#   -H "Accept: application/vnd.github+json" \
#   -f enforce_admins=false \
#   -F required_status_checks='null' \
#   -F required_pull_request_reviews.dismiss_stale_reviews=false \
#   -F required_pull_request_reviews.required_approving_review_count=1 \
#   -F restrictions.users[]="${OWNER}" \
#   -F restrictions.teams:='[]'
gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  "repos/${OWNER}/${REPO}/branches/${DEFAULT_BRANCH}/protection" \
  --input - <<EOF
{
  "required_status_checks": null,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF

echo "✅ Repository ${OWNER}/${REPO} created:"
echo "   • ${OWNER} can push directly to ${DEFAULT_BRANCH}"
echo "   • everyone else must open a pull request"