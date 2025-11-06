# Defect Detection System Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Defect Detection System Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend
Write-Host "[1/2] Starting Backend + Camera..." -ForegroundColor Yellow
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "python api_server_integrated.py" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "[2/2] Starting Frontend..." -ForegroundColor Yellow
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru -WindowStyle Normal
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " System Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend + Camera:  http://localhost:8000" -ForegroundColor White
Write-Host "  Web Interface:     http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  Press ESC to close all windows and exit" -ForegroundColor Red
Write-Host "  Press ENTER to open web interface" -ForegroundColor Green
Write-Host ""

# Wait for key press
do {
    $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    if ($key.VirtualKeyCode -eq 27) {
        # ESC key pressed
        Write-Host ""
        Write-Host "Closing all windows..." -ForegroundColor Yellow
        
        # Kill backend
        if ($backend -and !$backend.HasExited) {
            Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
        }
        
        # Kill frontend
        if ($frontend -and !$frontend.HasExited) {
            Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
        }
        
        # Kill any remaining Python and Node processes
        Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -match "api_server"} | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -match "vite"} | Stop-Process -Force -ErrorAction SilentlyContinue
        
        Write-Host "All windows closed." -ForegroundColor Green
        Start-Sleep -Seconds 2
        exit
    }
    elseif ($key.VirtualKeyCode -eq 13) {
        # ENTER key pressed
        Start-Process "http://localhost:3000"
        Write-Host "Browser opened. Press ESC to close all windows..." -ForegroundColor Yellow
    }
} while ($true)
