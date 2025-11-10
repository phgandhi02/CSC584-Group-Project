# PowerShell script to download models for comparison testing
# Run this before running comparison tests

Write-Host "=" -NoNewline
Write-Host ("=" * 69)
Write-Host "Installing Fast Models for Comparison Testing"
Write-Host "=" -NoNewline
Write-Host ("=" * 69)

$models = @(
    "gemma2:2b",
    "llama3.2:3b"
)

Write-Host "`nModels to install (fast models only):"
for ($i = 0; $i -lt $models.Count; $i++) {
    Write-Host "  $($i + 1). $($models[$i])"
}

Write-Host "`nNote: This may take several minutes depending on your internet speed."
Write-Host "Model sizes:"
Write-Host "  - gemma2:2b       : ~1.6 GB"
Write-Host "  - llama3.2:3b     : ~2.0 GB"
Write-Host "  - Total           : ~3.6 GB"
Write-Host ""
Write-Host "Note: Reasoning models (deepseek-r1, etc.) are excluded by default due to"
Write-Host "      20x slower generation speed. Install manually if needed: ollama pull deepseek-r1:8b"
Write-Host ""

$response = Read-Host "Download all models? (y/n)"

if ($response -ne "y") {
    Write-Host "Cancelled."
    exit
}

foreach ($model in $models) {
    Write-Host "`n" -NoNewline
    Write-Host ("=" * 70)
    Write-Host "Installing: $model"
    Write-Host ("=" * 70)
    
    # Check if already installed
    $existing = ollama list | Select-String $model
    if ($existing) {
        Write-Host "[SKIP] $model is already installed"
    } else {
        Write-Host "[DOWNLOADING] $model..."
        ollama pull $model
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] $model installed successfully"
        } else {
            Write-Host "[ERROR] Failed to install $model"
        }
    }
}

Write-Host "`n" -NoNewline
Write-Host ("=" * 70)
Write-Host "Setup Complete!"
Write-Host ("=" * 70)
Write-Host "`nYou can now run the fast model comparison:"
Write-Host "  python run_tests.py --compare"
Write-Host ""
Write-Host "To include slow model (deepseek-r1:8b) in comparison:"
Write-Host "  python run_tests.py --compare --include-slow"
Write-Host ""
Write-Host "Or test individual models:"
Write-Host "  python run_tests.py gemma2:2b"
Write-Host "  python run_tests.py llama3.2:3b"

