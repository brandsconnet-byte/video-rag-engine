@echo off
chcp 65001 >nul
echo ==========================================
echo   Video RAG Engine - Git Push Helper
echo ==========================================
echo.

REM Check if git is available
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git not found in PATH!
    echo.
    echo Please install Git first:
    echo   https://git-scm.com/download/win
    echo.
    echo Or use VS Code's built-in Git:
    echo   1. Open this folder in VS Code
    echo   2. Press Ctrl+Shift+G (Source Control)
    echo   3. Click "Initialize Repository"
    echo   4. Stage, commit, and push
    echo.
    pause
    exit /b 1
)

echo ✅ Git found!
git --version
echo.

REM Check if this is a git repo
if not exist .git (
    echo 📁 Initializing git repository...
    git init
    echo.
)

REM Add remote if not exists
git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    echo 🔗 Adding remote origin...
    git remote add origin https://github.com/brandsconnet-byte/video-rag-engine.git
    echo.
)

echo 📦 Staging all changes...
git add .
echo.

echo 💾 Committing changes...
git commit -m "Fix: SigLIP integration, auto-editor, EDL export, tests, CI" -m "Changes:" -m "- Replaced CLIP with actual SigLIP models" -m "- Fixed query embedding caching" -m "- Implemented real auto-editor integration" -m "- Added proper FCPXML/Premiere/EDL export" -m "- Added pro_export route" -m "- Added comprehensive test suite" -m "- Added GitHub Actions CI workflow" -m "- Updated dependencies (lxml, pytest-cov)"
echo.

REM Check current branch
for /f "tokens=*" %%a in ('git branch --show-current') do set BRANCH=%%a
echo 🌿 Current branch: %BRANCH%
echo.

REM Push to GitHub
echo 🚀 Pushing to GitHub...
git push -u origin %BRANCH%

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo   ✅ Successfully pushed to GitHub!
    echo ==========================================
    echo.
    echo View your repo:
    echo   https://github.com/brandsconnet-byte/video-rag-engine
) else (
    echo.
    echo ==========================================
    echo   ❌ Push failed!
    echo ==========================================
    echo.
    echo Common fixes:
    echo   1. Check your internet connection
    echo   2. Make sure you're logged into GitHub
    echo   3. Try: git pull origin %BRANCH% --rebase
    echo   4. Then push again: git push -u origin %BRANCH%
)

echo.
pause
