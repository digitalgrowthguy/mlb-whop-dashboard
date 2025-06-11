#!/usr/bin/env python3
"""
Database Setup for MLB Predictor - Whop Store

Sets up the database with sample data for the Whop store integration.
"""

import sqlite3
import shutil
import os

def setup_database():
    """Setup database for MLB predictions"""
    
    source_db = '../mlb-apps/mlb_yrfi_data.db'
    target_db = 'mlb_data.db'
    
    # Check if source database exists
    if os.path.exists(source_db):
        print("📊 Copying database from main project...")
        shutil.copy2(source_db, target_db)
        print(f"✅ Database copied to {target_db}")
        return True
    else:
        print("⚠️ Source database not found, creating minimal database...")
        create_minimal_database(target_db)
        return True

def create_minimal_database(db_path):
    """Create a minimal database with sample data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create games table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_date TEXT,
        season INTEGER,
        home_team_name TEXT,
        away_team_name TEXT,
        home_pitcher TEXT,
        away_pitcher TEXT,
        home_first_runs INTEGER DEFAULT 0,
        away_first_runs INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Final'
    )
    ''')
    
    # Insert sample data for demonstration
    sample_games = [
        ('2025-06-11', 2025, 'Yankees', 'Red Sox', 'Gerrit Cole', 'Chris Sale', 1, 0, 'Final'),
        ('2025-06-11', 2025, 'Dodgers', 'Giants', 'Walker Buehler', 'Logan Webb', 0, 2, 'Final'),
        ('2025-06-11', 2025, 'Astros', 'Rangers', 'Framber Valdez', 'Nathan Eovaldi', 1, 1, 'Final'),
        ('2025-06-11', 2025, 'Braves', 'Phillies', 'Spencer Strider', 'Zack Wheeler', 0, 0, 'Final'),
        ('2025-06-11', 2025, 'Mets', 'Marlins', 'Jacob deGrom', 'Sandy Alcantara', 2, 0, 'Final'),
    ]
    
    cursor.executemany('''
    INSERT INTO games (game_date, season, home_team_name, away_team_name, 
                      home_pitcher, away_pitcher, home_first_runs, away_first_runs, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_games)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Created minimal database with {len(sample_games)} sample games")

def verify_database():
    """Verify database has the required structure"""
    try:
        conn = sqlite3.connect('mlb_data.db')
        cursor = conn.cursor()
        
        # Check if games table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='games'")
        if not cursor.fetchone():
            print("❌ Games table not found")
            return False
        
        # Check for recent games
        cursor.execute("SELECT COUNT(*) FROM games WHERE game_date >= '2025-01-01'")
        count = cursor.fetchone()[0]
        print(f"📊 Found {count} games in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 Setting up MLB Predictor Database")
    print("=" * 40)
    
    if setup_database():
        if verify_database():
            print("\n✅ Database setup complete!")
            print("🚀 Ready to run predictions")
        else:
            print("\n❌ Database verification failed")
    else:
        print("\n❌ Database setup failed")

if __name__ == "__main__":
    main()
