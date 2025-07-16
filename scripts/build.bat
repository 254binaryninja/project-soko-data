@echo off
REM Simple build script for NSE Scraper (Windows)

echo 🐳 Building NSE Scraper Docker image...

docker-compose build

if %errorlevel% equ 0 (
    echo ✅ Build successful!
    echo.
    echo To run the scraper:
    echo   docker-compose up -d
    echo.
    echo To view logs:
    echo   docker-compose logs -f nse-scraper
) else (
    echo ❌ Build failed!
    exit /b 1
)

pause
