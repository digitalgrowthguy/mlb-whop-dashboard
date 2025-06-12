# PowerShell Commands for MLB Dashboard

# === DAILY OPERATIONS ===

# Update data and regenerate dashboard
Write-Host "🔄 Updating MLB data..." -ForegroundColor Yellow
python fetch_mlb_data.py

Write-Host "🏗️ Generating dashboard..." -ForegroundColor Yellow  
python generate_static_site.py

# === GIT OPERATIONS (PowerShell-compatible) ===

# Add all changes
Write-Host "📝 Adding files..." -ForegroundColor Green
git add .

# Commit changes
Write-Host "💾 Committing changes..." -ForegroundColor Green
git commit -m "Update predictions and data"

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Green
git push

# === FULL UPDATE AND DEPLOY ===
function Update-Dashboard {
    Write-Host "🔄 Starting full dashboard update..." -ForegroundColor Cyan
    
    # Fetch new data
    python fetch_mlb_data.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Data fetch failed!" -ForegroundColor Red
        return
    }
    
    # Generate site
    python generate_static_site.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Site generation failed!" -ForegroundColor Red
        return
    }
    
    # Deploy to GitHub
    git add .
    git commit -m "Update predictions for $(Get-Date -Format 'yyyy-MM-dd')"
    git push
    
    Write-Host "✅ Dashboard updated and deployed!" -ForegroundColor Green
    Write-Host "🌐 Check your GitHub Pages site in a few minutes" -ForegroundColor Cyan
}

# === SETUP COMMANDS ===

# Install dependencies
function Install-Dependencies {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

# Initialize database
function Initialize-Database {
    Write-Host "🗄️ Setting up database..." -ForegroundColor Yellow
    python setup_database.py
}

# === TESTING COMMANDS ===

# Test MLB API connection
function Test-MLBApi {
    Write-Host "🧪 Testing MLB API..." -ForegroundColor Yellow
    python test_real_mlb.py
}

# Test predictions
function Test-Predictions {
    Write-Host "🎯 Testing prediction model..." -ForegroundColor Yellow
    python -c "from predictor import MLBPredictor; p = MLBPredictor(); print('Predictor initialized successfully')"
}

Write-Host @"
🎯 MLB Dashboard PowerShell Commands Loaded!

Quick Commands:
• Update-Dashboard     - Full update and deploy
• Install-Dependencies - Install Python packages  
• Initialize-Database  - Setup database
• Test-MLBApi         - Test API connection
• Test-Predictions    - Test prediction model

Daily Workflow:
1. python fetch_mlb_data.py
2. python generate_static_site.py  
3. git add . ; git commit -m 'Update' ; git push

"@ -ForegroundColor Green
