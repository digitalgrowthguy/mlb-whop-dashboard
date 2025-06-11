#!/usr/bin/env python3
"""
MLB YRFI/NRFI Predictor v4 - Unbiased Version

This version addresses the severe NRFI bias found in v3 (98% NRFI predictions)
while maintaining good accuracy and practical bet frequency.

Key improvements:
- Eliminates NRFI bias through balanced thresholds
- Uses improved confidence calibration
- Better data quality assessment
- Maintains reasonable bet frequency (15-30%)
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import warnings
import config

warnings.filterwarnings('ignore')

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MLBPredictor:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = config.DATABASE_PATH
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # Realistic confidence thresholds for betting recommendations
        self.confidence_thresholds = {
            'excellent': 0.15,  # High confidence threshold (15%)
            'good': 0.12,       # Medium-high threshold (12%)
            'fair': 0.10,       # Medium threshold (10%)
            'poor': 0.08        # Lower threshold for more bets (8%)
        }
        
        # Base rates for calibration (from actual data analysis)
        self.league_yrfi_rate = 0.486  # Slightly under 50% YRFI historically
        
        logger.info("MLB Predictor v4 (Unbiased) initialized")

    def get_pitcher_stats(self, pitcher_name, season=None, min_games=3):
        """Get pitcher statistics with proper null handling"""
        if season is None:
            season = config.CURRENT_SEASON
            
        try:
            query = """
            SELECT 
                COUNT(*) as games,
                AVG(CASE WHEN (COALESCE(away_first_runs, 0) > 0 OR COALESCE(home_first_runs, 0) > 0) 
                         THEN 1 ELSE 0 END) as yrfi_rate,
                SUM(COALESCE(away_first_runs, 0) + COALESCE(home_first_runs, 0)) / COUNT(*) as avg_first_inning_runs
            FROM games 
            WHERE (home_pitcher = ? OR away_pitcher = ?)
            AND season = ?
            AND status = 'Final'
            """
            
            result = pd.read_sql_query(query, self.conn, params=[pitcher_name, pitcher_name, season])
            
            if len(result) == 0 or result.iloc[0]['games'] < min_games:
                return None
                
            return {
                'games': int(result.iloc[0]['games']),
                'yrfi_rate': float(result.iloc[0]['yrfi_rate']),
                'avg_first_inning_runs': float(result.iloc[0]['avg_first_inning_runs'])
            }
            
        except Exception as e:
            logger.error(f"Error getting pitcher stats for {pitcher_name}: {e}")
            return None

    def get_team_stats(self, team_name, season=None, min_games=10):
        """Get team statistics with improved handling"""
        if season is None:
            season = config.CURRENT_SEASON
            
        try:
            query = """
            SELECT 
                COUNT(*) as games,
                AVG(CASE WHEN (COALESCE(away_first_runs, 0) > 0 OR COALESCE(home_first_runs, 0) > 0) 
                         THEN 1 ELSE 0 END) as yrfi_rate,
                SUM(COALESCE(away_first_runs, 0) + COALESCE(home_first_runs, 0)) / COUNT(*) as avg_first_inning_runs
            FROM games 
            WHERE (home_team_name = ? OR away_team_name = ?)
            AND season = ?
            AND status = 'Final'
            """
            
            result = pd.read_sql_query(query, self.conn, params=[team_name, team_name, season])
            
            if len(result) == 0 or result.iloc[0]['games'] < min_games:
                return None
                
            return {
                'games': int(result.iloc[0]['games']),
                'yrfi_rate': float(result.iloc[0]['yrfi_rate']),
                'avg_first_inning_runs': float(result.iloc[0]['avg_first_inning_runs'])
            }
            
        except Exception as e:
            logger.error(f"Error getting team stats for {team_name}: {e}")
            return None

    def assess_data_quality(self, home_pitcher_stats, away_pitcher_stats, home_team_stats, away_team_stats):
        """Assess data quality for the prediction"""
        quality_score = 0
        details = []
        
        # Pitcher data quality
        if home_pitcher_stats and home_pitcher_stats['games'] >= 5:
            quality_score += 25
            details.append(f"Home pitcher: {home_pitcher_stats['games']} games")
        elif home_pitcher_stats and home_pitcher_stats['games'] >= 3:
            quality_score += 15
            details.append(f"Home pitcher: {home_pitcher_stats['games']} games (limited)")
        else:
            details.append("Home pitcher: insufficient data")
            
        if away_pitcher_stats and away_pitcher_stats['games'] >= 5:
            quality_score += 25
            details.append(f"Away pitcher: {away_pitcher_stats['games']} games")
        elif away_pitcher_stats and away_pitcher_stats['games'] >= 3:
            quality_score += 15
            details.append(f"Away pitcher: {away_pitcher_stats['games']} games (limited)")
        else:
            details.append("Away pitcher: insufficient data")
        
        # Team data quality (teams typically have more games)
        if home_team_stats and home_team_stats['games'] >= 20:
            quality_score += 25
            details.append(f"Home team: {home_team_stats['games']} games")
        elif home_team_stats and home_team_stats['games'] >= 10:
            quality_score += 15
            details.append(f"Home team: {home_team_stats['games']} games (limited)")
        else:
            details.append("Home team: insufficient data")
            
        if away_team_stats and away_team_stats['games'] >= 20:
            quality_score += 25
            details.append(f"Away team: {away_team_stats['games']} games")
        elif away_team_stats and away_team_stats['games'] >= 10:
            quality_score += 15
            details.append(f"Away team: {away_team_stats['games']} games (limited)")
        else:
            details.append("Away team: insufficient data")
        
        # Classify quality
        if quality_score >= 85:
            quality = 'excellent'
        elif quality_score >= 65:
            quality = 'good'
        elif quality_score >= 45:
            quality = 'fair'
        else:
            quality = 'poor'
            
        return quality, quality_score, details

    def calculate_unbiased_prediction(self, home_pitcher_stats, away_pitcher_stats, 
                                    home_team_stats, away_team_stats, data_quality):
        """Calculate prediction with bias elimination"""
        
        # Start with league average as baseline
        base_yrfi_prob = self.league_yrfi_rate
        
        # Collect YRFI rates with fallback to league average
        rates = []
        weights = []
        
        # Home pitcher contribution
        if home_pitcher_stats:
            rates.append(home_pitcher_stats['yrfi_rate'])
            weights.append(0.3)  # Pitchers have significant impact
        else:
            rates.append(base_yrfi_prob)
            weights.append(0.15)  # Reduced weight for missing data
            
        # Away pitcher contribution  
        if away_pitcher_stats:
            rates.append(away_pitcher_stats['yrfi_rate'])
            weights.append(0.3)
        else:
            rates.append(base_yrfi_prob)
            weights.append(0.15)
            
        # Home team contribution
        if home_team_stats:
            rates.append(home_team_stats['yrfi_rate'])
            weights.append(0.2)
        else:
            rates.append(base_yrfi_prob)
            weights.append(0.1)
            
        # Away team contribution
        if away_team_stats:
            rates.append(away_team_stats['yrfi_rate'])
            weights.append(0.2)
        else:
            rates.append(base_yrfi_prob)
            weights.append(0.1)
        
        # Calculate weighted average
        if sum(weights) > 0:
            weighted_yrfi_prob = sum(r * w for r, w in zip(rates, weights)) / sum(weights)
        else:
            weighted_yrfi_prob = base_yrfi_prob
        
        # Apply calibration based on data quality
        quality_multipliers = {
            'excellent': 1.0,   # Full confidence in the calculation
            'good': 0.8,        # Slight regression to mean
            'fair': 0.6,        # More regression to mean
            'poor': 0.4         # Heavy regression to mean
        }
        
        multiplier = quality_multipliers.get(data_quality, 0.4)
        calibrated_prob = (weighted_yrfi_prob * multiplier) + (base_yrfi_prob * (1 - multiplier))
        
        # Ensure probability stays in reasonable bounds
        calibrated_prob = max(0.2, min(0.8, calibrated_prob))
        
        return calibrated_prob

    def make_prediction(self, home_team, away_team, home_pitcher, away_pitcher):
        """Make unbiased YRFI/NRFI prediction"""
        try:
            logger.info(f"\n=== Making prediction for {away_team} @ {home_team} ===")
            logger.info(f"Pitchers: {away_pitcher} vs {home_pitcher}")
            
            # Get statistics
            home_pitcher_stats = self.get_pitcher_stats(home_pitcher)
            away_pitcher_stats = self.get_pitcher_stats(away_pitcher)
            home_team_stats = self.get_team_stats(home_team)
            away_team_stats = self.get_team_stats(away_team)
            
            # Assess data quality
            data_quality, quality_score, quality_details = self.assess_data_quality(
                home_pitcher_stats, away_pitcher_stats, home_team_stats, away_team_stats
            )
            
            logger.info(f"Data quality: {data_quality} (score: {quality_score}/100)")
            for detail in quality_details:
                logger.info(f"  - {detail}")
            
            # Calculate unbiased prediction
            yrfi_probability = self.calculate_unbiased_prediction(
                home_pitcher_stats, away_pitcher_stats,
                home_team_stats, away_team_stats, data_quality
            )
            
            # Determine confidence and prediction with improved calculation
            base_confidence = abs(yrfi_probability - 0.5) * 2  # Scale to 0-1
            
            # Boost confidence based on data quality and how far from 50/50
            quality_multipliers = {
                'excellent': 2.5,
                'good': 2.0,
                'fair': 1.5,
                'poor': 1.0
            }
            
            # Additional confidence from extreme probabilities
            extreme_bonus = 0
            if yrfi_probability <= 0.3 or yrfi_probability >= 0.7:
                extreme_bonus = 0.15
            elif yrfi_probability <= 0.35 or yrfi_probability >= 0.65:
                extreme_bonus = 0.10
            elif yrfi_probability <= 0.4 or yrfi_probability >= 0.6:
                extreme_bonus = 0.05
            
            confidence = (base_confidence * quality_multipliers.get(data_quality, 1.0)) + extreme_bonus
            confidence = min(confidence, 0.95)  # Cap at 95%
            
            prediction = 'YRFI' if yrfi_probability > 0.5 else 'NRFI'
            
            # Check if we should make a bet based on data quality and confidence
            min_confidence = self.confidence_thresholds.get(data_quality, 0.52)
            should_bet = confidence >= min_confidence
            
            logger.info(f"YRFI probability: {yrfi_probability:.3f}")
            logger.info(f"Confidence: {confidence:.3f}")
            logger.info(f"Prediction: {prediction}")
            logger.info(f"Should bet: {should_bet} (min confidence: {min_confidence:.3f})")
            
            return {
                'prediction': prediction,
                'yrfi_probability': yrfi_probability,
                'nrfi_probability': 1 - yrfi_probability,
                'confidence': confidence,
                'should_bet': should_bet,
                'data_quality': data_quality,
                'quality_score': quality_score,
                'quality_details': quality_details,
                'min_confidence_required': min_confidence,
                'details': {
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_pitcher': home_pitcher,
                    'away_pitcher': away_pitcher
                }
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return {
                'prediction': 'NO_BET',
                'confidence': 0.0,
                'yrfi_probability': 0.5,
                'nrfi_probability': 0.5,
                'data_quality': 'poor',
                'should_bet': False,
                'error': str(e)
            }

    def get_daily_predictions(self, target_date=None):
        """Get predictions for a specific date"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # First try to find games for today's date in current season
            query = """
            SELECT DISTINCT
                game_date,
                home_team_name as home_team,
                away_team_name as away_team,
                home_pitcher,
                away_pitcher
            FROM games 
            WHERE DATE(game_date) = ?
            AND season = ?
            ORDER BY game_date
            """
            
            games = pd.read_sql_query(query, self.conn, params=[target_date, config.CURRENT_SEASON])
            
            if len(games) == 0:
                logger.info(f"No games found for {target_date} in {config.CURRENT_SEASON} season")
                
                # Check what dates are available in the database
                date_check_query = """
                SELECT DISTINCT game_date, season, COUNT(*) as game_count
                FROM games 
                ORDER BY season DESC, game_date DESC
                LIMIT 10
                """
                available_dates = pd.read_sql_query(date_check_query, self.conn)
                logger.info("Recent available dates in database:")
                for _, row in available_dates.iterrows():
                    logger.info(f"  {row['game_date']} (Season {row['season']}) - {row['game_count']} games")
                
                # Try most recent date with games
                if len(available_dates) > 0:
                    recent_date = available_dates.iloc[0]['game_date']
                    recent_season = available_dates.iloc[0]['season']
                    logger.info(f"Using most recent available date: {recent_date}")
                    
                    fallback_query = """
                    SELECT DISTINCT
                        game_date,
                        home_team_name as home_team,
                        away_team_name as away_team,
                        home_pitcher,
                        away_pitcher
                    FROM games 
                    WHERE DATE(game_date) = ?
                    AND season = ?
                    ORDER BY game_date
                    """
                    games = pd.read_sql_query(fallback_query, self.conn, params=[recent_date, recent_season])
                    target_date = recent_date
                    
            if len(games) == 0:
                logger.info(f"No games found for any available date")
                return []
            
            predictions = []
            for _, game in games.iterrows():
                prediction = self.make_prediction(
                    game['home_team'], game['away_team'],
                    game['home_pitcher'], game['away_pitcher']
                )
                
                if prediction:
                    prediction.update({
                        'game_date': game['game_date'],
                        'home_team': game['home_team'],
                        'away_team': game['away_team'],
                        'home_pitcher': game['home_pitcher'],
                        'away_pitcher': game['away_pitcher']
                    })
                    predictions.append(prediction)
            
            # Summary stats
            total_games = len(predictions)
            betting_games = sum(1 for p in predictions if p['should_bet'])
            yrfi_predictions = sum(1 for p in predictions if p['prediction'] == 'YRFI' and p['should_bet'])
            nrfi_predictions = sum(1 for p in predictions if p['prediction'] == 'NRFI' and p['should_bet'])
            
            logger.info(f"\n=== DAILY SUMMARY for {target_date} ===")
            logger.info(f"Total games analyzed: {total_games}")
            logger.info(f"Games with betting recommendations: {betting_games} ({betting_games/total_games*100:.1f}%)")
            logger.info(f"YRFI predictions: {yrfi_predictions}")
            logger.info(f"NRFI predictions: {nrfi_predictions}")
            if betting_games > 0:
                logger.info(f"YRFI/NRFI split: {yrfi_predictions/betting_games*100:.1f}% / {nrfi_predictions/betting_games*100:.1f}%")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error getting daily predictions: {e}")
            return []

    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
