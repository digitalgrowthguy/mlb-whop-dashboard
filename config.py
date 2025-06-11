"""
Configuration settings for MLB Predictor Dashboard
"""

# Database Configuration
DATABASE_PATH = 'mlb_data.db'

# Prediction Configuration
CONFIDENCE_THRESHOLDS = {
    'excellent': 0.15,  # High confidence threshold (15%)
    'good': 0.12,       # Medium-high threshold (12%)
    'fair': 0.10,       # Medium threshold (10%)
    'poor': 0.08        # Lower threshold for more bets (8%)
}

# Season Configuration
CURRENT_SEASON = 2025
MIN_PITCHER_GAMES = 3

# Dashboard Configuration
DASHBOARD_TITLE = "⚾ MLB YRFI/NRFI Predictions Dashboard"
AUTO_REFRESH_SECONDS = 300  # 5 minutes

# HTML Dashboard Styling
DASHBOARD_THEME = {
    'primary_color': '#1e3c72',
    'secondary_color': '#2a5298',
    'accent_color': '#FFD700',
    'text_color': '#ffffff',
    'card_bg': 'rgba(255,255,255,0.1)',
    'border_radius': '15px'
}

# Betting Strategy
BETTING_STRATEGY = {
    'min_confidence': 0.08,
    'max_daily_bets': 10,
    'bankroll_percent': 0.02  # 2% of bankroll per bet
}

# API Configuration (if using external data sources)
API_CONFIG = {
    'base_url': 'https://api.mlb.com',
    'timeout': 30,
    'retries': 3
}
