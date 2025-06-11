#!/usr/bin/env python3
"""
Static Site Generator for MLB Predictor Dashboard
Generates static HTML files for GitHub Pages hosting
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from predictor import MLBPredictor
import config

def generate_html_content(predictions):
    """Generate HTML content for the dashboard"""
    
    # Calculate summary stats
    total_games = len(predictions)
    betting_games = sum(1 for p in predictions if p.get('should_bet', False))
    yrfi_count = sum(1 for p in predictions if p.get('prediction') == 'YRFI' and p.get('should_bet', False))
    nrfi_count = sum(1 for p in predictions if p.get('prediction') == 'NRFI' and p.get('should_bet', False))
    
    current_date = datetime.now().strftime('%B %d, %Y')
    current_time = datetime.now().strftime('%I:%M %p EST')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚾ MLB YRFI/NRFI Predictions - {current_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .date {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .summary-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            backdrop-filter: blur(10px);
        }}
        
        .summary-card h3 {{
            font-size: 2rem;
            margin-bottom: 5px;
            color: #FFD700;
        }}
        
        .predictions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .prediction-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border-left: 5px solid;
        }}
        
        .prediction-card.yrfi {{
            border-left-color: #4CAF50;
        }}
        
        .prediction-card.nrfi {{
            border-left-color: #f44336;
        }}
        
        .prediction-card.no-bet {{
            border-left-color: #757575;
            opacity: 0.7;
        }}
        
        .game-info {{
            margin-bottom: 15px;
        }}
        
        .teams {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .pitchers {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .prediction-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .prediction {{
            font-size: 1.5rem;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
        }}
        
        .prediction.yrfi {{
            background: #4CAF50;
            color: white;
        }}
        
        .prediction.nrfi {{
            background: #f44336;
            color: white;
        }}
        
        .prediction.no-bet {{
            background: #757575;
            color: white;
        }}
        
        .confidence {{
            font-size: 1.1rem;
            font-weight: bold;
        }}
        
        .details {{
            font-size: 0.8rem;
            opacity: 0.7;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            opacity: 0.7;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .predictions-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚾ MLB YRFI/NRFI Predictions</h1>
        <div class="date">{current_date} • Updated: {current_time}</div>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>{total_games}</h3>
            <p>Total Games</p>
        </div>
        <div class="summary-card">
            <h3>{betting_games}</h3>
            <p>Betting Opportunities</p>
        </div>
        <div class="summary-card">
            <h3>{yrfi_count}</h3>
            <p>YRFI Predictions</p>
        </div>
        <div class="summary-card">
            <h3>{nrfi_count}</h3>
            <p>NRFI Predictions</p>
        </div>
    </div>
    
    <div class="predictions-grid">
"""
    
    # Add individual predictions
    for i, pred in enumerate(predictions, 1):
        prediction = pred.get('prediction', 'NO_BET')
        confidence = pred.get('confidence', 0) * 100
        should_bet = pred.get('should_bet', False)
        
        home_team = pred.get('home_team', 'Unknown')
        away_team = pred.get('away_team', 'Unknown')
        home_pitcher = pred.get('home_pitcher', 'Unknown')
        away_pitcher = pred.get('away_pitcher', 'Unknown')
        data_quality = pred.get('data_quality', 'unknown')
        
        card_class = prediction.lower() if should_bet else 'no-bet'
        pred_class = prediction.lower() if should_bet else 'no-bet'
        pred_text = prediction if should_bet else 'NO BET'
        
        html_content += f"""
        <div class="prediction-card {card_class}">
            <div class="game-info">
                <div class="teams">{away_team} @ {home_team}</div>
                <div class="pitchers">{away_pitcher} vs {home_pitcher}</div>
            </div>
            <div class="prediction-info">
                <div class="prediction {pred_class}">{pred_text}</div>
                <div class="confidence">{confidence:.1f}%</div>
            </div>
            <div class="details">
                Data Quality: {data_quality.title()} | Game #{i}
            </div>
        </div>
"""
    
    html_content += """
    </div>
    
    <div class="footer">
        <p>🎯 Predictions generated using advanced MLB statistical analysis</p>
        <p>⚡ Auto-updated daily at 6:00 AM EST</p>
        <p>📊 For entertainment purposes only. Please gamble responsibly.</p>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes during game hours (1 PM - 11 PM EST)
        const now = new Date();
        const hour = now.getHours();
        if (hour >= 13 && hour <= 23) {
            setTimeout(() => {
                window.location.reload();
            }, 300000); // 5 minutes
        }
    </script>
</body>
</html>
"""
    
    return html_content

def generate_static_dashboard():
    """Generate static HTML dashboard for GitHub Pages"""
    
    # Create output directory
    output_dir = "docs"  # GitHub Pages looks for docs/ folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate predictions
    predictor = MLBPredictor()
    predictions = predictor.get_daily_predictions()
    
    # Generate main dashboard HTML
    dashboard_html = generate_html_content(predictions)
    
    # Save main dashboard
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    # Generate JSON data for API access
    json_data = {
        "last_updated": datetime.now().isoformat(),
        "predictions": predictions,
        "summary": {
            "total_games": len(predictions),
            "betting_opportunities": sum(1 for p in predictions if p.get('should_bet', False)),
            "yrfi_predictions": sum(1 for p in predictions if p.get('prediction') == 'YRFI' and p.get('should_bet', False)),
            "nrfi_predictions": sum(1 for p in predictions if p.get('prediction') == 'NRFI' and p.get('should_bet', False))
        }
    }
    
    with open(os.path.join(output_dir, "data.json"), "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, default=str)
    
    # Generate historical data (last 7 days)
    historical_data = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        try:
            day_predictions = predictor.get_daily_predictions(date)
            if day_predictions:
                historical_data.append({
                    "date": date,
                    "total_games": len(day_predictions),
                    "betting_opportunities": sum(1 for p in day_predictions if p.get('should_bet', False)),
                    "yrfi_predictions": sum(1 for p in day_predictions if p.get('prediction') == 'YRFI' and p.get('should_bet', False)),
                    "nrfi_predictions": sum(1 for p in day_predictions if p.get('prediction') == 'NRFI' and p.get('should_bet', False))
                })
        except:
            pass
    
    with open(os.path.join(output_dir, "historical.json"), "w", encoding="utf-8") as f:
        json.dump(historical_data, f, indent=2)
    
    # Copy any static assets
    static_files = ["README.md"]
    for file in static_files:
        if os.path.exists(file):
            shutil.copy2(file, output_dir)
    
    print(f"✅ Static site generated in '{output_dir}/' folder")
    print(f"📊 Generated data for {len(predictions)} games")
    print(f"🕒 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    generate_static_dashboard()
