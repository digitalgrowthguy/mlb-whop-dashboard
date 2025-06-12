#!/usr/bin/env python3
"""
MLB Data Fetcher - Updates database with latest game data
Fetches data from MLB Stats API or other sources
"""

import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLBDataFetcher:
    def __init__(self, db_path='mlb_data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.base_url = "https://statsapi.mlb.com/api/v1"
        
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id TEXT PRIMARY KEY,
                game_date TEXT,
                season INTEGER,
                home_team_name TEXT,
                away_team_name TEXT,
                home_pitcher TEXT,
                away_pitcher TEXT,
                home_first_runs INTEGER,
                away_first_runs INTEGER,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("Database tables created/verified")
    
    def get_today_games(self):
        """Get TODAY'S actual MLB games"""
        today = datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Fetching TODAY'S games for {today}")
        
        url = f"{self.base_url}/schedule"
        params = {
            'sportId': 1,  # MLB
            'date': today,
            'hydrate': 'team,probablePitcher'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            games = []
            if data.get('dates'):
                for date_info in data['dates']:
                    for game in date_info.get('games', []):
                        game_id = str(game['gamePk'])
                        home_team = game['teams']['home']['team']['name']
                        away_team = game['teams']['away']['team']['name']
                        
                        # Get probable pitchers
                        home_pitcher = "Unknown"
                        away_pitcher = "Unknown"
                        
                        if 'probablePitcher' in game['teams']['home']:
                            home_pitcher = game['teams']['home']['probablePitcher']['fullName']
                        if 'probablePitcher' in game['teams']['away']:
                            away_pitcher = game['teams']['away']['probablePitcher']['fullName']
                        
                        games.append({
                            'game_id': game_id,
                            'game_date': today,
                            'season': 2025,
                            'home_team_name': home_team,
                            'away_team_name': away_team,
                            'home_pitcher': home_pitcher,
                            'away_pitcher': away_pitcher,
                            'status': game['status']['detailedState']
                        })
            
            logger.info(f"✅ Found {len(games)} games for today")
            for game in games:
                logger.info(f"   {game['away_team_name']} @ {game['home_team_name']} - {game['away_pitcher']} vs {game['home_pitcher']}")
            
            return games
            
        except Exception as e:
            logger.error(f"Error fetching today's games: {e}")
            return []
        """Get MLB schedule for date range"""
        url = f"{self.base_url}/schedule"
        params = {
            'startDate': start_date,
            'endDate': end_date,
            'sportId': 1,  # MLB
            'hydrate': 'game(content(editorial(recap))),decisions,person,probablePitcher,stats,homeRuns,previousPlay,flags,review,broadcasts(all),venue,linescore,boxscore'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching schedule: {e}")
            return None
    
    def get_game_details(self, game_id):
        """Get detailed game information"""
        url = f"{self.base_url}/game/{game_id}/feed/live"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching game {game_id}: {e}")
            return None
    
    def extract_first_inning_runs(self, game_data):
        """Extract first inning runs from game data"""
        try:
            linescore = game_data.get('liveData', {}).get('linescore', {})
            innings = linescore.get('innings', [])
            
            if len(innings) > 0:
                first_inning = innings[0]
                home_first = first_inning.get('home', {}).get('runs', 0)
                away_first = first_inning.get('away', {}).get('runs', 0)
                return home_first, away_first
            
            return 0, 0
        except Exception as e:
            logger.warning(f"Error extracting first inning runs: {e}")
            return 0, 0
    
    def get_probable_pitchers(self, game_data):
        """Extract probable pitchers from game data"""
        try:
            home_pitcher = "Unknown"
            away_pitcher = "Unknown"
            
            teams = game_data.get('gameData', {}).get('teams', {})
            
            # Try to get probable pitchers
            home_probable = teams.get('home', {}).get('probablePitcher', {})
            away_probable = teams.get('away', {}).get('probablePitcher', {})
            
            if home_probable:
                home_pitcher = home_probable.get('fullName', 'Unknown')
            
            if away_probable:
                away_pitcher = away_probable.get('fullName', 'Unknown')
            
            # If no probable pitcher, try to get starting pitcher from boxscore
            if home_pitcher == "Unknown" or away_pitcher == "Unknown":
                live_data = game_data.get('liveData', {})
                boxscore = live_data.get('boxscore', {})
                teams_box = boxscore.get('teams', {})
                
                if home_pitcher == "Unknown":
                    home_pitchers = teams_box.get('home', {}).get('pitchers', [])
                    if home_pitchers:
                        # Get first pitcher (starter)
                        pitcher_id = home_pitchers[0]
                        players = boxscore.get('teams', {}).get('home', {}).get('players', {})
                        pitcher_key = f"ID{pitcher_id}"
                        if pitcher_key in players:
                            home_pitcher = players[pitcher_key].get('person', {}).get('fullName', 'Unknown')
                
                if away_pitcher == "Unknown":
                    away_pitchers = teams_box.get('away', {}).get('pitchers', [])
                    if away_pitchers:
                        pitcher_id = away_pitchers[0]
                        players = boxscore.get('teams', {}).get('away', {}).get('players', {})
                        pitcher_key = f"ID{pitcher_id}"
                        if pitcher_key in players:
                            away_pitcher = players[pitcher_key].get('person', {}).get('fullName', 'Unknown')
            
            return home_pitcher, away_pitcher
            
        except Exception as e:
            logger.warning(f"Error extracting pitchers: {e}")
            return "Unknown", "Unknown"
    
    def update_games(self, days_back=7):
        """Update games for the last N days"""
        self.create_tables()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        logger.info(f"Fetching games from {start_str} to {end_str}")
        
        schedule_data = self.get_schedule(start_str, end_str)
        if not schedule_data:
            logger.error("Failed to fetch schedule")
            return
        
        games_updated = 0
        cursor = self.conn.cursor()
        
        for date_data in schedule_data.get('dates', []):
            game_date = date_data.get('date')
            
            for game in date_data.get('games', []):
                game_id = game.get('gamePk')
                
                # Check if game already exists and is final
                cursor.execute("SELECT status FROM games WHERE game_id = ?", (game_id,))
                existing = cursor.fetchone()
                
                if existing and existing[0] == 'Final':
                    continue  # Skip already completed games
                
                # Get detailed game data
                game_details = self.get_game_details(game_id)
                if not game_details:
                    continue
                
                # Extract game information
                game_data = game_details.get('gameData', {})
                live_data = game_details.get('liveData', {})
                
                teams = game_data.get('teams', {})
                home_team = teams.get('home', {}).get('name', 'Unknown')
                away_team = teams.get('away', {}).get('name', 'Unknown')
                
                status = game_details.get('gameData', {}).get('status', {}).get('detailedState', 'Unknown')
                season = game_data.get('game', {}).get('season', datetime.now().year)
                
                # Get pitchers
                home_pitcher, away_pitcher = self.get_probable_pitchers(game_details)
                
                # Get first inning runs (only for completed games)
                home_first_runs, away_first_runs = 0, 0
                home_score, away_score = 0, 0
                
                if status == 'Final':
                    home_first_runs, away_first_runs = self.extract_first_inning_runs(game_details)
                    
                    # Get final scores
                    linescore = live_data.get('linescore', {})
                    teams_score = linescore.get('teams', {})
                    home_score = teams_score.get('home', {}).get('runs', 0)
                    away_score = teams_score.get('away', {}).get('runs', 0)
                
                # Insert or update game
                cursor.execute("""
                    INSERT OR REPLACE INTO games 
                    (game_id, game_date, season, home_team_name, away_team_name, 
                     home_pitcher, away_pitcher, home_first_runs, away_first_runs,
                     home_score, away_score, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    game_id, game_date, season, home_team, away_team,
                    home_pitcher, away_pitcher, home_first_runs, away_first_runs,
                    home_score, away_score, status
                ))                
                games_updated += 1
                logger.info(f"Updated: {away_team} @ {home_team} ({game_date}) - Status: {status}")
                
                # Rate limiting
                time.sleep(0.1)
        
        self.conn.commit()
        logger.info(f"✅ Updated {games_updated} games")
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main function to fetch TODAY'S real MLB data"""
    print("Fetching TODAY'S Real MLB Games...")
    
    fetcher = MLBDataFetcher()
    fetcher.create_tables()
    
    # Get today's games
    games = fetcher.get_today_games()
    
    if games:
        # Store games in database
        cursor = fetcher.conn.cursor()
        
        for game in games:
            # Insert or update game data
            cursor.execute("""
                INSERT OR REPLACE INTO games (
                    game_id, game_date, season, home_team_name, away_team_name,
                    home_pitcher, away_pitcher, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game['game_id'], game['game_date'], game['season'],
                game['home_team_name'], game['away_team_name'],
                game['home_pitcher'], game['away_pitcher'], game['status']            ))
        
        fetcher.conn.commit()
        print(f"Stored {len(games)} real games in database")
        
        # Show what we got
        print("\nTODAY'S MLB GAMES:")
        for game in games:
            print(f"  {game['away_team_name']} @ {game['home_team_name']}")
            print(f"     Pitchers: {game['away_pitcher']} vs {game['home_pitcher']}")
            print(f"     Status: {game['status']}")
            print()
    else:
        print("No games found for today")
    
    fetcher.conn.close()
    print("Database updated with real MLB data!")

if __name__ == "__main__":
    main()
