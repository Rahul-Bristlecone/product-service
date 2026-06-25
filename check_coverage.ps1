# Coverage check script for local development (PowerShell)
# Usage: .\check_coverage.ps1 [-Html]

param(
    [Switch]$Html,
    [Switch]$Report
)

$PythonCmd = "C:/Users/rsshr/AppData/Local/Microsoft/WindowsApps/python3.12.exe"
$FailUnder = 85

Write-Host "🧪 Running unit tests with coverage..." -ForegroundColor Cyan
Write-Host ""

# Build pytest command
$PytestArgs = @(
    "-m", "pytest", "tests/unit",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=xml:coverage.xml",
    "--cov-fail-under=$FailUnder",
    "-v"
)

# Optional: Generate HTML report
if ($Html) {
    $PytestArgs += "--cov-report=html:htmlcov"
}

# Run tests
$output = & $PythonCmd @PytestArgs
$exitCode = $LASTEXITCODE

Write-Host $output

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ Coverage gate PASSED (>= $FailUnder%)" -ForegroundColor Green
    
    if ($Html) {
        Write-Host "📊 HTML report generated: htmlcov/index.html" -ForegroundColor Green
        # Optional: Open in default browser
        # Start htmlcov/index.html
    }
    
    exit 0
} else {
    Write-Host ""
    Write-Host "❌ Coverage gate FAILED (< $FailUnder%)" -ForegroundColor Red
    Write-Host "📊 See htmlcov/index.html for detailed report" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Run with -Html flag to generate HTML report:" -ForegroundColor Cyan
    Write-Host "   .\check_coverage.ps1 -Html" -ForegroundColor Cyan
    exit 1
}
