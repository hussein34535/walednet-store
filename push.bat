@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo  WaledNet AutoPublisher - Push to GitHub
echo ============================================

if not exist ".git" (
    git init -b main >nul
    echo [1/5] Repo initialized
)

set "URL="
if exist ".git\config" (git remote get-url origin >nul 2>1 && set "URL=found")
if "%URL%"=="" (
    set /p ORIGIN="Paste your GitHub repo URL (https://github.com/YOU/walednet-store): "
    git remote add origin "%ORIGIN%"
    echo [2/5] Remote added
) else (
    echo [2/5] Remote already set
)

echo [3/5] Staging files...
git add -A

echo [4/5] Committing...
git -c user.name="walednet" -c user.email="walednet@users.noreply.github.com" commit -m "feat: autopublisher + pinterest kit + landing page"

echo [5/5] Pushing...
git push -u origin main

echo.
echo Done! Check: https://github.com/YOU/walednet-store/actions
pause
