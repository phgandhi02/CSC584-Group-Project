#!/bin/bash
# Bash script to download models for comparison testing
# Run this before running comparison tests

echo "======================================================================"
echo "Installing Fast Models for Comparison Testing"
echo "======================================================================"

models=(
    "gemma2:2b"
    "llama3.2:3b"
)

echo ""
echo "Models to install (fast models only):"
for i in "${!models[@]}"; do
    echo "  $((i+1)). ${models[$i]}"
done

echo ""
echo "Note: This may take several minutes depending on your internet speed."
echo "Model sizes:"
echo "  - gemma2:2b       : ~1.6 GB"
echo "  - llama3.2:3b     : ~2.0 GB"
echo "  - Total           : ~3.6 GB"
echo ""
echo "Note: Reasoning models (deepseek-r1, etc.) are excluded by default due to"
echo "      20x slower generation speed. Install manually if needed: ollama pull deepseek-r1:8b"
echo ""

read -p "Download all models? (y/n): " response

if [ "$response" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

for model in "${models[@]}"; do
    echo ""
    echo "======================================================================"
    echo "Installing: $model"
    echo "======================================================================"
    
    # Check if already installed
    if ollama list | grep -q "$model"; then
        echo "[SKIP] $model is already installed"
    else
        echo "[DOWNLOADING] $model..."
        ollama pull "$model"
        
        if [ $? -eq 0 ]; then
            echo "[SUCCESS] $model installed successfully"
        else
            echo "[ERROR] Failed to install $model"
        fi
    fi
done

echo ""
echo "======================================================================"
echo "Setup Complete!"
echo "======================================================================"
echo ""
echo "You can now run the fast model comparison:"
echo "  python run_tests.py --compare"
echo ""
echo "To include slow model (deepseek-r1:8b) in comparison:"
echo "  python run_tests.py --compare --include-slow"
echo ""
echo "Or test individual models:"
echo "  python run_tests.py gemma2:2b"
echo "  python run_tests.py llama3.2:3b"

