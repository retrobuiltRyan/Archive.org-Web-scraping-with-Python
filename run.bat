@echo off

echo --------------------------------------------------
echo WELCOME TO ARCHIVE.ORG DOWNLOADER
echo "<!-- __ _ _ _ __| |_ (_)__ _____"
echo "    / _` | '_/ _| ' \| |\ V / -_)"
echo "    \__,_|_| \__|_||_|_| \_/\___| -->"
echo --------------------------------------------------

set scriptPath=%~dp0
"%scriptPath%./app/.venv/Scripts/python.exe" "%scriptPath%./app/scrape-archive_download.py"

pause