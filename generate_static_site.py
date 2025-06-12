#!/usr/bin/env python3
"""
Static Site Generator for MLB Predictor Dashboard - Clean Version with A-F Grading
Generates static HTML files for GitHub Pages hosting
"""

import os
import json
import shutil
from datetime import datetime, timedelta
from predictor import MLBPredictor
import config

def get_grade_info(confidence, should_bet):
    """Convert confidence to letter grade with description"""
    if not should_bet:
        return 'N/A', 'No Bet', '#666', 'Insufficient confidence'
    
    conf_pct = confidence * 100
    
    if conf_pct >= 70:
        return 'A+', 'Elite', '#00C851', 'Highest confidence - Premium bet'
    elif conf_pct >= 60:
        return 'A', 'Excellent', '#2E7D32', 'Very high confidence'
    elif conf_pct >= 50:
        return 'B+', 'Strong', '#388E3C', 'High confidence'
    elif conf_pct >= 40:
        return 'B', 'Good', '#FFA726', 'Good confidence'
    elif conf_pct >= 30:
        return 'C+', 'Fair', '#FB8C00', 'Moderate confidence'
    elif conf_pct >= 20:
        return 'C', 'Decent', '#F57C00', 'Lower confidence'
    elif conf_pct >= 15:
        return 'D', 'Risky', '#FF5722', 'Low confidence - risky'
    else:
        return 'F', 'Avoid', '#D32F2F', 'Very low confidence'

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
        
        .header .updated {{
            font-size: 0.9rem;
            opacity: 0.7;
            margin-top: 5px;
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
            margin-bottom: 30px;
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
            border-left-color: #FF9800;
        }}
        
        .prediction-card.no-bet {{
            border-left-color: #666;
            opacity: 0.7;
        }}
        
        .game-info {{
            margin-bottom: 15px;
        }}
        
        .teams {{
            font-size: 1.2rem;
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
            margin-bottom: 15px;
        }}
        
        .prediction {{
            font-size: 1.4rem;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 5px;
        }}
        
        .prediction.yrfi {{
            background: #4CAF50;
            color: white;
        }}
        
        .prediction.nrfi {{
            background: #FF9800;
            color: white;
        }}
        
        .prediction.no-bet {{
            background: #666;
            color: white;
        }}
        
        .grade-info {{
            text-align: center;
        }}
        
        .grade {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 2px;
        }}
        
        .grade-desc {{
            font-size: 0.9rem;
            margin-bottom: 2px;
        }}
        
        .grade-detail {{
            font-size: 0.8rem;
            opacity: 0.8;
        }}
        
        .details {{
            font-size: 0.8rem;
            opacity: 0.7;
            text-align: center;
        }}
        
        .grading-legend {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .grading-legend h3 {{
            text-align: center;
            margin-bottom: 15px;
            color: #FFD700;
        }}
        
        .legend-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }}
        
        .legend-item {{
            text-align: center;
            padding: 10px;
            border-radius: 5px;
            font-size: 0.9rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
        }}
        
        .footer p {{
            margin: 5px 0;
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .predictions-grid {{
                grid-template-columns: 1fr;
            }}
            
            .prediction-info {{
                flex-direction: column;
                gap: 10px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
        
        /* Auto-refresh during game hours */
        @media screen {{
            body {{
                animation: fadeIn 0.5s ease-in;
            }}
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
    </style>
    
    <script>
        // Auto-refresh during game hours (1 PM - 11 PM EST)
        function autoRefresh() {{
            const now = new Date();
            const hour = now.getHours();
            
            // Refresh every 15 minutes during game hours
            if (hour >= 13 && hour <= 23) {{
                setTimeout(() => {{
                    window.location.reload();
                }}, 15 * 60 * 1000); // 15 minutes
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', autoRefresh);
    </script>
</head>
<body>
    <div class="header">
        <h1>⚾ MLB YRFI/NRFI Predictions</h1>
        <div class="date">{current_date}</div>
        <div class="updated">Last updated: {current_time}</div>
    </div>
    
    <div class="grading-legend">
        <h3>📊 Confidence Grading System</h3>
        <div class="legend-grid">
            <div class="legend-item" style="background: #00C851;">
                <div style="font-weight: bold;">A+</div>
                <div>Elite (70%+)</div>
            </div>
            <div class="legend-item" style="background: #2E7D32;">
                <div style="font-weight: bold;">A</div>
                <div>Excellent (60%+)</div>
            </div>
            <div class="legend-item" style="background: #388E3C;">
                <div style="font-weight: bold;">B+</div>
                <div>Strong (50%+)</div>
            </div>
            <div class="legend-item" style="background: #FFA726;">
                <div style="font-weight: bold;">B</div>
                <div>Good (40%+)</div>
            </div>
            <div class="legend-item" style="background: #FB8C00;">
                <div style="font-weight: bold;">C+</div>
                <div>Fair (30%+)</div>
            </div>
            <div class="legend-item" style="background: #F57C00;">
                <div style="font-weight: bold;">C</div>
                <div>Decent (20%+)</div>
            </div>
            <div class="legend-item" style="background: #FF5722;">
                <div style="font-weight: bold;">D</div>
                <div>Risky (15%+)</div>
            </div>
            <div class="legend-item" style="background: #D32F2F;">
                <div style="font-weight: bold;">F</div>
                <div>Avoid (&lt;15%)</div>
            </div>
        </div>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>{total_games}</h3>
            <p>Total Games</p>
        </div>
        <div class="summary-card">
            <h3>{betting_games}</h3>
            <p>Recommended Bets</p>
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
        confidence = pred.get('confidence', 0)
        should_bet = pred.get('should_bet', False)
        
        home_team = pred.get('home_team', 'Unknown')
        away_team = pred.get('away_team', 'Unknown')
        home_pitcher = pred.get('home_pitcher', 'Unknown')
        away_pitcher = pred.get('away_pitcher', 'Unknown')
        data_quality = pred.get('data_quality', 'unknown')
        
        # Get grade information
        grade, grade_desc, grade_color, grade_detail = get_grade_info(confidence, should_bet)
        
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
                <div class="grade-info">
                    <div class="grade" style="color: {grade_color};">{grade}</div>
                    <div class="grade-desc">{grade_desc}</div>
                    <div class="grade-detail">{grade_detail}</div>
                </div>
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
        <p>🔄 Dashboard refreshes automatically during game hours (1-11 PM EST)</p>
    </div>
</body>
</html>"""
    
    return html_content

def generate_data_json(predictions):
    """Generate JSON data for API access"""
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S EST')
    
    # Add grade info to predictions
    enhanced_predictions = []
    for pred in predictions:
        enhanced_pred = pred.copy()
        grade, grade_desc, grade_color, grade_detail = get_grade_info(
            pred.get('confidence', 0), 
            pred.get('should_bet', False)
        )
        enhanced_pred['grade'] = grade
        enhanced_pred['grade_description'] = grade_desc
        enhanced_pred['grade_color'] = grade_color
        enhanced_pred['grade_detail'] = grade_detail
        enhanced_predictions.append(enhanced_pred)
    
    data = {
        'date': current_date,
        'last_updated': current_time,
        'total_games': len(predictions),
        'betting_games': sum(1 for p in predictions if p.get('should_bet', False)),
        'yrfi_count': sum(1 for p in predictions if p.get('prediction') == 'YRFI' and p.get('should_bet', False)),
        'nrfi_count': sum(1 for p in predictions if p.get('prediction') == 'NRFI' and p.get('should_bet', False)),
        'predictions': enhanced_predictions
    }
    
    return json.dumps(data, indent=2)

def generate_historical_json():
    """Generate historical performance JSON"""
    data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S EST'),
        'note': 'Historical performance tracking will be implemented as data accumulates',
        'grading_system': {
            'A+': 'Elite (70%+ confidence)',
            'A': 'Excellent (60%+ confidence)',
            'B+': 'Strong (50%+ confidence)',
            'B': 'Good (40%+ confidence)',
            'C+': 'Fair (30%+ confidence)',
            'C': 'Decent (20%+ confidence)',
            'D': 'Risky (15%+ confidence)',
            'F': 'Avoid (<15% confidence)'
        }
    }
    
    return json.dumps(data, indent=2)

def main():
    """Main function to generate static site"""
    print("Generating MLB YRFI/NRFI Dashboard...")
    
    # Create docs directory
    docs_dir = 'docs'
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"Created {docs_dir}/ directory")
    
    # Initialize predictor and get predictions
    predictor = MLBPredictor()
    predictions = predictor.get_daily_predictions()
    
    # Generate HTML content
    html_content = generate_html_content(predictions)
    
    # Write HTML file
    html_path = os.path.join(docs_dir, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {html_path}")
    
    # Generate data JSON
    data_json = generate_data_json(predictions)
    data_path = os.path.join(docs_dir, 'data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_json)
    print(f"Generated {data_path}")
    
    # Generate historical JSON
    historical_json = generate_historical_json()
    historical_path = os.path.join(docs_dir, 'historical.json')
    with open(historical_path, 'w', encoding='utf-8') as f:
        f.write(historical_json)
    print(f"Generated {historical_path}")
    
    # Create README for docs folder
    readme_content = f"""# MLB YRFI/NRFI Predictions Dashboard

This folder contains the static files for the GitHub Pages deployment.

## Files

- `index.html` - Main dashboard page
- `data.json` - Current predictions in JSON format
- `historical.json` - Historical performance data

## Last Updated

{datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}

## Access

The live dashboard is available at: https://digitalgrowthguy.github.io/mlb-whop-dashboard

## Grading System

- **A+** - Elite (70%+ confidence)
- **A** - Excellent (60%+ confidence)  
- **B+** - Strong (50%+ confidence)
- **B** - Good (40%+ confidence)
- **C+** - Fair (30%+ confidence)
- **C** - Decent (20%+ confidence)
- **D** - Risky (15%+ confidence)
- **F** - Avoid (<15% confidence)
"""
    
    readme_path = os.path.join(docs_dir, 'README.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"Generated {readme_path}")
    
    print("Static site generated in 'docs/' folder")
    print(f"Generated data for {len(predictions)} games")
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
