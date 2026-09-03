# Push to GitHub Guide

Since git is not available in this environment, follow these steps to push using VS Code's built-in git.

## Option 1: VS Code Built-in Git (Recommended)

1. **Open the project folder in VS Code:**
   ```
   File → Open Folder → Select: video-rag-engine-main
   ```

2. **Initialize Git Repository:**
   - Open Source Control panel (Ctrl+Shift+G or click branch icon)
   - Click "Initialize Repository"

3. **Stage All Changes:**
   - Click the "+" icon next to "Changes" to stage all files
   - Or click each file individually

4. **Commit:**
   - Type message: `Fix: SigLIP integration, auto-editor, EDL export, tests, CI`
   - Click the checkmark (✓) or press Ctrl+Enter

5. **Add Remote:**
   - Open terminal in VS Code (Ctrl+`)
   - Run:
     ```bash
     git remote add origin https://github.com/brandsconnet-byte/video-rag-engine.git
     ```

6. **Push:**
   - Click "Publish Branch" or "Push"
   - Enter your GitHub credentials when prompted
   - If asked, select "main" as the branch name

## Option 2: GitHub Desktop

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. File → Add local repository → Select `video-rag-engine-main`
3. Repository → Repository settings → Remote → Add origin URL
4. Commit changes and push

## Option 3: Git Bash (if installed separately)

```bash
cd video-rag-engine-main
git init
git add .
git commit -m "Fix: SigLIP integration, auto-editor, EDL export, tests, CI"
git remote add origin https://github.com/brandsconnet-byte/video-rag-engine.git
git push -u origin main
```

## Summary of Changes to Commit

| Fix | Files Changed |
|-----|--------------|
| Replaced CLIP with actual SigLIP | `src/dual_brain_processor.py`, `src/vector_database.py` |
| Fixed query embedding caching | `src/vector_database.py`, `src/pipeline.py` |
| Implemented real auto-editor | `src/export_manager.py` |
| Added proper EDL/XML export | `src/export_manager.py` |
| Added pro_export route | `src/intelligent_router.py` |
| Added test suite | `tests/` directory (4 test files + conftest.py) |
| Added CI/CD | `.github/workflows/ci.yml` |
| Updated dependencies | `requirements.txt` |

## Troubleshooting

**"fatal: not a git repository"**
→ Run `git init` first

**"fatal: remote origin already exists"**
→ Run `git remote remove origin` then add again

**"rejected: non-fast-forward"**
→ Run `git pull origin main --rebase` first, then push

**Authentication failed**
→ Use GitHub token or sign in via VS Code's built-in authentication
