#!/usr/bin/env python3
"""
HTML Dashboard Generator for MLB Predictions - Whop Store Ready

Generates a modern, responsive HTML dashboard optimized for embedding.
"""

import os
import webbrowser
from datetime import datetime
from predictor import MLBPredictor
import config

def generate_dashboard(save_path='mlb_dashboard.html', open_browser=False):
    """Generate HTML dashboard optimized for Whop store embedding"""
    
    try:
        # Initialize predictor
        predictor = MLBPredictor()
        predictions = predictor.get_daily_predictions()
        
        # Calculate summary stats
        total_games = len(predictions)
        betting_games = sum(1 for p in predictions if p.get('should_bet', False))
        yrfi_count = sum(1 for p in predictions if p.get('prediction') == 'YRFI' and p.get('should_bet', False))
        nrfi_count = sum(1 for p in predictions if p.get('prediction') == 'NRFI' and p.get('should_bet', False))
        
        strong_bets = [p for p in predictions if p.get('confidence', 0) >= 0.15 and p.get('should_bet', False)]
        moderate_bets = [p for p in predictions if 0.12 <= p.get('confidence', 0) < 0.15 and p.get('should_bet', False)]
        light_bets = [p for p in predictions if 0.08 <= p.get('confidence', 0) < 0.12 and p.get('should_bet', False)]
        
        avg_confidence = sum([p.get('confidence', 0) for p in predictions if p.get('should_bet', False)]) / betting_games if betting_games > 0 else 0
        
        # Generate HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.DASHBOARD_TITLE}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, {config.DASHBOARD_THEME['primary_color']} 0%, {config.DASHBOARD_THEME['secondary_color']} 100%);
            color: {config.DASHBOARD_THEME['text_color']};
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: {config.DASHBOARD_THEME['card_bg']};
            padding: 30px;
            border-radius: {config.DASHBOARD_THEME['border_radius']};
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, {config.DASHBOARD_THEME['accent_color']}, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: {config.DASHBOARD_THEME['card_bg']};
            padding: 25px;
            border-radius: {config.DASHBOARD_THEME['border_radius']};
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .stat-card h3 {{
            font-size: 1.2em;
            margin-bottom: 15px;
            color: {config.DASHBOARD_THEME['accent_color']};
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .predictions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .game-card {{
            background: {config.DASHBOARD_THEME['card_bg']};
            border-radius: {config.DASHBOARD_THEME['border_radius']};
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }}
        
        .game-card:hover {{
            transform: translateY(-5px);
        }}
        
        .game-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .teams {{
            font-size: 1.1em;
            font-weight: bold;
        }}
        
        .prediction {{
            font-size: 1.2em;
            font-weight: bold;
            padding: 5px 15px;
            border-radius: 20px;
            text-align: center;
            margin: 10px 0;
        }}
        
        .yrfi {{
            background: linear-gradient(45deg, #4CAF50, #45a049);
        }}
        
        .nrfi {{
            background: linear-gradient(45deg, #f44336, #da190b);
        }}
        
        .no-bet {{
            background: linear-gradient(45deg, #666, #555);
        }}
        
        .confidence-bar {{
            width: 100%;
            height: 20px;
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .confidence-fill {{
            height: 100%;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FFEAA7);
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .bet-recommendation {{
            padding: 8px 15px;
            border-radius: 20px;
            text-align: center;
            font-weight: bold;
            margin-top: 10px;
        }}
        
        .excellent-bet {{ background: linear-gradient(45deg, {config.DASHBOARD_THEME['accent_color']}, #FFA500); color: #000; }}
        .good-bet {{ background: linear-gradient(45deg, #4CAF50, #45a049); }}
        .fair-bet {{ background: linear-gradient(45deg, #2196F3, #1976D2); }}
        .poor-bet {{ background: linear-gradient(45deg, #FF9800, #F57C00); }}
        .pass {{ background: linear-gradient(45deg, #666, #555); }}
        
        .summary-section {{
            background: {config.DASHBOARD_THEME['card_bg']};
            padding: 25px;
            border-radius: {config.DASHBOARD_THEME['border_radius']};
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .summary-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: {config.DASHBOARD_THEME['card_bg']};
            border-radius: {config.DASHBOARD_THEME['border_radius']};
            backdrop-filter: blur(10px);
        }}
        
        .refresh-btn {{
            display: inline-block;
            padding: 12px 25px;
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin-top: 15px;
            transition: transform 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            transform: scale(1.05);
        }}
        
        /* Mobile responsive */
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }}
            
            .predictions-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{config.DASHBOARD_TITLE}</h1>
            <h2>📅 {datetime.now().strftime('%B %d, %Y')}</h2>
            <p>🤖 MLB Predictor v4 (Balanced) | 🎯 Professional Betting Recommendations</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>🎮 Total Games</h3>
                <div class="stat-number">{total_games}</div>
            </div>
            <div class="stat-card">
                <h3>💰 Betting Games</h3>
                <div class="stat-number">{betting_games}</div>
                <p>{betting_games/total_games*100:.1f}% of games</p>
            </div>
            <div class="stat-card">
                <h3>📈 Avg Confidence</h3>
                <div class="stat-number">{avg_confidence:.1%}</div>
            </div>
            <div class="stat-card">
                <h3>⭐ Strong Bets</h3>
                <div class="stat-number">{len(strong_bets)}</div>
            </div>
        </div>
        
        <div class="summary-section">
            <h2 style="text-align: center; margin-bottom: 20px;">📊 Today's Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h4>🔥 YRFI Predictions</h4>
                    <div style="font-size: 1.5em; font-weight: bold;">{yrfi_count}</div>
                </div>
                <div class="summary-item">
                    <h4>🔴 NRFI Predictions</h4>
                    <div style="font-size: 1.5em; font-weight: bold;">{nrfi_count}</div>
                </div>
                <div class="summary-item">
                    <h4>✅ Good Bets</h4>
                    <div style="font-size: 1.5em; font-weight: bold;">{len(moderate_bets)}</div>
                </div>
                <div class="summary-item">
                    <h4>📍 Fair Bets</h4>
                    <div style="font-size: 1.5em; font-weight: bold;">{len(light_bets)}</div>
                </div>
            </div>
        </div>
        
        <h2 style="text-align: center; margin-bottom: 20px;">🎮 Today's Games</h2>
        <div class="predictions-grid">
"""
        
        # Add individual game cards
        for i, game in enumerate(predictions, 1):
            details = game.get('details', {})
            away_team = details.get('away_team', 'TBD')
            home_team = details.get('home_team', 'TBD')
            prediction = game.get('prediction', 'NO_BET')
            confidence = game.get('confidence', 0)
            yrfi_prob = game.get('yrfi_probability', 0.5)
            should_bet = game.get('should_bet', False)
            data_quality = game.get('data_quality', 'poor')
            
            pred_class = 'yrfi' if prediction == 'YRFI' else 'nrfi' if prediction == 'NRFI' else 'no-bet'
            
            if should_bet:
                if confidence >= config.CONFIDENCE_THRESHOLDS['excellent']:
                    bet_class, bet_text = 'excellent-bet', '⭐ EXCELLENT BET'
                elif confidence >= config.CONFIDENCE_THRESHOLDS['good']:
                    bet_class, bet_text = 'good-bet', '✅ GOOD BET'
                elif confidence >= config.CONFIDENCE_THRESHOLDS['fair']:
                    bet_class, bet_text = 'fair-bet', '📍 FAIR BET'
                elif confidence >= config.CONFIDENCE_THRESHOLDS['poor']:
                    bet_class, bet_text = 'poor-bet', '⚠️ POOR BET'
                else:
                    bet_class, bet_text = 'pass', '❌ PASS'
            else:
                bet_class, bet_text = 'pass', '❌ PASS'
            
            html_content += f"""
            <div class="game-card">
                <div class="game-header">
                    <span style="font-size: 0.9em; color: {config.DASHBOARD_THEME['accent_color']};">Game {i}</span>
                    <span style="font-size: 0.8em; color: #ccc;">Quality: {data_quality.title()}</span>
                </div>
                <div class="teams">🛣️ {away_team}</div>
                <div style="text-align: center; margin: 5px 0;">@</div>
                <div class="teams">🏠 {home_team}</div>
                
                <div class="prediction {pred_class}">
                    {prediction}
                </div>
                
                <div style="margin: 15px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Confidence:</span>
                        <span style="font-weight: bold;">{confidence:.1%}</span>
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {min(confidence*100, 100):.1f}%;"></div>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin: 10px 0;">
                    <span>🔥 YRFI: {yrfi_prob:.1%}</span>
                    <span>🔴 NRFI: {1-yrfi_prob:.1%}</span>
                </div>
                
                <div class="bet-recommendation {bet_class}">
                    {bet_text}
                </div>
            </div>
            """
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>🤖 Model: MLB Predictor v4 (Balanced)</p>
            <p>📊 Professional betting recommendations with balanced predictions</p>
            <p>🕒 Generated at {datetime.now().strftime('%I:%M %p')}</p>
            <a href="#" onclick="location.reload();" class="refresh-btn">🔄 Refresh Data</a>
        </div>
    </div>
    
    <script>
        // Auto-refresh every {config.AUTO_REFRESH_SECONDS // 60} minutes
        setTimeout(function(){{
            location.reload();
        }}, {config.AUTO_REFRESH_SECONDS * 1000});
        
        // Add click interactivity
        document.querySelectorAll('.game-card').forEach(card => {{
            card.addEventListener('click', function() {{
                this.style.transform = this.style.transform === 'scale(1.02)' ? 'scale(1)' : 'scale(1.02)';
            }});
        }});
        
        // Smooth scroll animations
        document.querySelectorAll('.game-card').forEach((card, index) => {{
            card.style.animationDelay = (index * 0.1) + 's';
            card.style.animation = 'fadeInUp 0.6s ease forwards';
        }});
    </script>
    
    <style>
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
</body>
</html>
"""
        
        # Save HTML file
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Dashboard generated successfully!")
        print(f"📄 File: {save_path}")
        print(f"📊 Games: {total_games} total, {betting_games} bets ({yrfi_count} YRFI, {nrfi_count} NRFI)")
        
        if open_browser:
            print("🌐 Opening in browser...")
            webbrowser.open('file://' + os.path.abspath(save_path))
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        return False

def main():
    """Generate dashboard and open in browser"""
    generate_dashboard(open_browser=True)

if __name__ == "__main__":
    main()
