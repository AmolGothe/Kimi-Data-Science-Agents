# Git Workflow — Pull & Push Guide

Standard git workflow for the **KIMI Data Science Agents** repository.  
Repo: [https://github.com/AmolGothe/Kimi-Data-Science-Agents](https://github.com/AmolGothe/Kimi-Data-Science-Agents)

---

## Before Every Work Session — Pull Latest

```bash
cd "c:\Users\gothe-1\OneDrive - Mettler Toledo LLC\Documents\KIMI Global Agent Team\Kimi-Data_Science_Agents"

# 1. Check your current branch
git branch

# 2. Pull latest from remote (always do this BEFORE making changes)
git pull origin main
```

---

## After Making Changes — Stage, Commit, Push

```bash
# 1. Check what changed
git status

# 2. Stage all changes (new + modified + deleted)
git add -A

# 3. Commit with a descriptive message
git commit -m "feat: describe what you changed"

# 4. Push to GitHub
git push origin main
```

---

## Commit Message Convention

Use prefixes to categorise your changes:

| Prefix | When to use | Example |
|--------|------------|---------|
| `feat:` | New feature or capability | `feat: add time series forecaster agent` |
| `fix:` | Bug fix | `fix: correct feature_schema.json path in analyst prompt` |
| `docs:` | Documentation only | `docs: update README with new agent table` |
| `refactor:` | Code restructure, no new features | `refactor: extract shared sandbox helper functions` |
| `chore:` | Config, install, infra changes | `chore: add MCP sandbox server and update install.sh` |

---

## Working on a Feature Branch (Recommended for Big Changes)

```bash
# 1. Create and switch to a new branch
git checkout -b feature/your-feature-name

# 2. Make your changes, then stage + commit
git add -A
git commit -m "feat: your feature description"

# 3. Push the branch to GitHub
git push origin feature/your-feature-name

# 4. Go to GitHub → Create a Pull Request → Merge after review

# 5. After merge, switch back to main and pull
git checkout main
git pull origin main

# 6. (Optional) Delete the local feature branch
git branch -d feature/your-feature-name
```

---

## Quick Reference — Common Commands

| Command | Purpose |
|---------|---------|
| `git status` | See what files changed |
| `git diff` | See exact line-by-line changes |
| `git add -A` | Stage everything |
| `git add <file>` | Stage a specific file |
| `git commit -m "msg"` | Commit staged changes |
| `git push origin main` | Push to GitHub main branch |
| `git pull origin main` | Pull latest from GitHub |
| `git log -n 5 --oneline` | Show last 5 commits |
| `git stash` | Temporarily save uncommitted changes |
| `git stash pop` | Restore stashed changes |
| `git checkout -- <file>` | Discard changes to a file |
| `git reset HEAD <file>` | Unstage a file |

---

## Resolving Merge Conflicts

If `git pull` shows conflicts:

```bash
# 1. Git marks conflicts in files — open them and look for:
#    <<<<<<< HEAD
#    (your local changes)
#    =======
#    (remote changes)
#    >>>>>>> origin/main

# 2. Edit the file to choose the correct version

# 3. Stage the resolved file
git add <resolved-file>

# 4. Complete the merge
git commit -m "fix: resolve merge conflict in <file>"

# 5. Push
git push origin main
```

---

## .gitignore Recommendations

Add to `.gitignore` to keep the repo clean:

```
__pycache__/
*.pyc
.DS_Store
*.egg-info/
dist/
build/
.env
```
