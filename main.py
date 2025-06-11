#!/usr/bin/env python3
"""
Main entry point for MLB Predictor Dashboard - Whop Store Ready

This is the primary script to run daily predictions and generate dashboard.
"""

import sys
import os
from datetime import datetime
from predictor import MLBPredictor
from dashboard import generate_dashboard
import config

def setup_database():
    """Create or verify database structure"""
    # For now, we'll copy from the main project
    # In production, you'd want to include data fetching logic here
    
    if not os.path.exists(config.DATABASE_PATH):
        print("⚠️ Database not found. Please ensure mlb_data.db is present.")
        print("   You can copy it from the main project or set up data collection.")
        return False
    
    return True

def run_daily_predictions():
    """Run predictions and generate dashboard"""
    print("🚀 Starting MLB Predictor Dashboard Generation")
    print(f"📅 Date: {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 50)
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed")
        return False
    
    try:
        # Initialize predictor
        predictor = MLBPredictor()
        
        # Get predictions
        print("🎯 Generating predictions...")
        predictions = predictor.get_daily_predictions()
        
        if not predictions:
            print("⚠️ No predictions available for today")
            return False
        
        # Calculate summary stats
        total_games = len(predictions)
        betting_games = sum(1 for p in predictions if p.get('should_bet', False))
        yrfi_count = sum(1 for p in predictions if p.get('prediction') == 'YRFI')
        nrfi_count = sum(1 for p in predictions if p.get('prediction') == 'NRFI')
        
        # Display summary
        print(f"\n📊 PREDICTION SUMMARY")
        print("-" * 30)
        print(f"🎮 Total Games: {total_games}")
        print(f"💰 Betting Opportunities: {betting_games}")
        print(f"🔥 YRFI Predictions: {yrfi_count}")
        print(f"🔴 NRFI Predictions: {nrfi_count}")
        
        # Show individual predictions
        print(f"\n🎯 DETAILED PREDICTIONS")
        print("-" * 30)
        
        bet_count = 0
        for pred in predictions:
            if pred['should_bet']:
                bet_count += 1
                details = pred['details']
                game = f"{details['away_team']} @ {details['home_team']}"
                prediction = pred['prediction']
                confidence = pred['confidence']
                data_quality = pred['data_quality']
                
                print(f"\n{bet_count}. {game}")
                print(f"   Prediction: {prediction}")
                print(f"   Confidence: {confidence:.1%}")
                print(f"   Data Quality: {data_quality}")
        
        # Generate HTML dashboard
        print(f"\n🌐 Generating HTML dashboard...")
        success = generate_dashboard('mlb_dashboard.html', open_browser=False)
        
        if success:
            print("✅ Dashboard generated successfully!")
            print("📄 File: mlb_dashboard.html")
            print("🔗 Ready for Whop store embedding")
        else:
            print("❌ Dashboard generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--dashboard-only':
            print("🌐 Generating dashboard only...")
            success = generate_dashboard('mlb_dashboard.html', open_browser=True)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--help':
            print("MLB Predictor Dashboard - Whop Store Ready")
            print("")
            print("Usage:")
            print("  python main.py                 # Run predictions and generate dashboard")
            print("  python main.py --dashboard-only # Generate dashboard and open in browser")
            print("  python main.py --help          # Show this help")
            sys.exit(0)
    
    # Run full prediction pipeline
    success = run_daily_predictions()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
