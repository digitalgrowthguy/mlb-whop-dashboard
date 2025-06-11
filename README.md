# ⚾ MLB YRFI/NRFI Predictor Dashboard

A complete automated MLB betting predictor system with daily auto-updating GitHub Pages dashboard.

🔗 **Live Dashboard**: [https://yourusername.github.io/mlb-whop-dashboard](https://yourusername.github.io/mlb-whop-dashboard)

## 🚀 Features

- **🤖 Automated Daily Updates**: GitHub Actions fetches fresh MLB data and regenerates predictions at 6 AM EST
- **📱 Mobile-First Design**: Responsive dashboard optimized for all devices
- **⚡ Real-Time Data**: Live MLB game data from official MLB Stats API
- **🎯 Smart Predictions**: Unbiased YRFI/NRFI predictions with confidence scoring
- **📊 Historical Tracking**: Performance analytics and trend analysis
- **🔄 Zero Maintenance**: Fully automated - set it and forget it
- **🆓 Free Hosting**: Deployed on GitHub Pages at no cost

## 🎯 Live Dashboard

The dashboard automatically updates daily with:
- Today's MLB games and predictions
- Confidence-based betting recommendations
- Historical performance metrics
- Mobile-optimized interface

## 🔧 Setup Instructions

### 1. Fork/Clone Repository
```bash
git clone https://github.com/yourusername/mlb-whop-dashboard.git
cd mlb-whop-dashboard
```

### 2. Install Dependencies (for local development)
```bash
pip install -r requirements.txt
```

### 3. Enable GitHub Pages
1. Go to your repo's **Settings** → **Pages**
2. Set **Source** to "Deploy from a branch"
3. Set **Branch** to "main" and **Folder** to "/docs"
4. Click **Save**

### 4. Automatic Updates
The GitHub Actions workflow automatically:
- Runs daily at 6 AM EST
- Fetches fresh MLB data
- Generates new predictions
- Updates the live dashboard
- Commits changes to the repo

## 📊 Local Development

```bash
# Generate static site locally
python generate_static_site.py

# Fetch latest MLB data
python fetch_mlb_data.py

# Run predictions
python main.py
```

## 🎯 Betting Strategy

The system provides tiered confidence levels:
- **🔥 Excellent** (15%+): High confidence bets
- **✅ Good** (12-15%): Medium-high confidence  
- **⚠️ Fair** (10-12%): Medium confidence
- **❌ Poor** (8-10%): Lower confidence but still actionable

## ⚙️ Configuration

All settings can be configured in `config.py`:
- Database path and schema
- Confidence thresholds for betting recommendations
- API endpoints and data sources
- Dashboard styling and appearance

## 🚀 Deployment Status

Check your deployment:
- ✅ GitHub Actions workflow runs daily
- ✅ Static files generated in `/docs` folder
- ✅ Mobile-responsive design
- ✅ Auto-refresh capabilities
- ✅ Clean, professional dashboard

## 📈 API & Data

- **MLB Stats API**: Official MLB data source
- **SQLite Database**: Local data storage and caching
- **JSON Exports**: Structured data for dashboard consumption
- **Historical Tracking**: Performance analytics over time

## 🔄 How It Works

1. **Daily Trigger**: GitHub Actions runs at 6 AM EST
2. **Data Fetch**: Downloads latest MLB schedules and stats
3. **Predictions**: Generates YRFI/NRFI predictions for today's games
4. **Site Generation**: Creates updated HTML dashboard
5. **Deployment**: Pushes changes to GitHub Pages automatically

## 📱 Dashboard Features

- **Today's Games**: All MLB games with predictions
- **Confidence Scoring**: Visual indicators for bet quality
- **Historical Performance**: Track prediction accuracy
- **Mobile Optimized**: Perfect viewing on any device
- **Fast Loading**: Optimized for quick access

## 🛠️ Troubleshooting

### GitHub Pages Not Working?
1. Check repository Settings → Pages
2. Ensure source is set to "main" branch, "/docs" folder
3. Verify GitHub Actions are enabled in repository settings

### Predictions Not Updating?
1. Check GitHub Actions tab for workflow runs
2. Ensure workflow has proper permissions
3. Verify the workflow file is in `.github/workflows/`

### Local Development Issues?
```bash
# Reset database if needed
python setup_database.py

# Manual data fetch
python fetch_mlb_data.py

# Generate fresh site
python generate_static_site.py
```

## 📄 License

This project is open source and available under the MIT License.

---

**⚾ Ready to predict some runs? Your dashboard updates automatically every day!**
