---
description: How to push changes to dev and merge to master
---

# SecureZen Git Workflow

This workflow ensures that all changes are reviewed in the `dev` branch before being merged into the `master` branch.

## 1. Work on Dev Branch
Always make sure you are on the `dev` branch before starting work:
```powershell
git checkout dev
```

## 2. Commit and Push to Dev
When you've made changes:
```powershell
git add .
git commit -m "Description of your changes"
git push origin dev
```

## 3. Merge to Master (After Review)
Once the changes in `dev` are validated and ready for production:
```powershell
# Switch to master
git checkout master

# Pull latest master just in case
git pull origin master

# Merge dev into master
git merge dev

# Push to master
git push origin master

# Switch back to dev for new work
git checkout dev
```
