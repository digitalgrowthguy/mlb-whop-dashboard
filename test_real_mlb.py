#!/usr/bin/env python3
"""
Quick test to get real MLB data for today
"""
import requests
import json
from datetime import datetime

def test_mlb_api():
    """Test the MLB API to get real current data"""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"🔍 Checking MLB schedule for {today}...")
    
    # Get today's schedule
    schedule_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    try:
        response = requests.get(schedule_url)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ API Response successful")
        print(f"📊 Total games today: {data.get('totalGames', 0)}")
        
        if data.get('dates'):
            for date_info in data['dates']:
                games = date_info.get('games', [])
                print(f"📅 Date: {date_info['date']} - {len(games)} games")
                
                for i, game in enumerate(games[:5], 1):  # Show first 5 games
                    game_id = game['gamePk']
                    home_team = game['teams']['home']['team']['name']
                    away_team = game['teams']['away']['team']['name']
                    status = game['status']['detailedState']
                    
                    print(f"  🏟️  Game {i}: {away_team} @ {home_team}")
                    print(f"      ID: {game_id}, Status: {status}")
                    
                    # Try to get live feed for this game
                    live_url = f"https://statsapi.mlb.com/api/v1/game/{game_id}/feed/live"
                    try:
                        live_response = requests.get(live_url)
                        if live_response.status_code == 200:
                            print(f"      ✅ Live data available")
                        else:
                            print(f"      ❌ Live data not available: {live_response.status_code}")
                    except Exception as e:
                        print(f"      ❌ Error getting live data: {e}")
        else:
            print("❌ No games found for today")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mlb_api()
