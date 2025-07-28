"""
Data processing module for the Review Analytics Dashboard.
Handles data loading, cleaning, sentiment analysis, and statistics generation.
"""

import os
import json
import pandas as pd
import re
from collections import Counter
from textblob import TextBlob
from typing import Dict, List, Any, Optional
from config import ASPECT_KEYWORDS, SENTIMENT_THRESHOLDS, STOP_WORDS, SOURCE_PATTERNS


class DataProcessor:
    """Handles all data processing operations for the dashboard."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.df = pd.DataFrame()
        self.aspect_df = pd.DataFrame()
    
    def load_data(self) -> bool:
        """Load and process review data from JSON files."""
        all_data = []
        
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} not found!")
            return False
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Determine source based on filename
                    source = self._detect_source(filename)
                    
                    # Standardize data
                    for review in data:
                        all_data.append({
                            'source': source,
                            'author': review.get('author', 'Anonymous'),
                            'rating': review.get('rating'),
                            'review_text': review.get('review', ''),
                            'date': review.get('date'),
                            'helpful': review.get('helpful', 0)
                        })
                
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        if all_data:
            self.df = pd.DataFrame(all_data)
            self.df = self.df[self.df['review_text'].str.strip() != '']
            self.df['date'] = pd.to_datetime(self.df['date'], errors='coerce')
            self._analyze_sentiment()
            self._analyze_aspects()
            print(f"Loaded {len(self.df)} reviews from {self.df['source'].nunique()} sources")
            return True
        else:
            print("No data found!")
            return False
    
    def _detect_source(self, filename: str) -> str:
        """Detect the source platform based on filename."""
        filename_lower = filename.lower()
        
        for source, patterns in SOURCE_PATTERNS.items():
            if any(pattern in filename_lower for pattern in patterns):
                return source
        
        return 'Unknown'
    
    def _analyze_sentiment(self) -> None:
        """Analyze sentiment using TextBlob."""
        def get_sentiment(text: str) -> float:
            if not text:
                return 0
            blob = TextBlob(str(text))
            return blob.sentiment.polarity
        
        self.df['sentiment_score'] = self.df['review_text'].apply(get_sentiment)
        
        def categorize_sentiment(score: float) -> str:
            if score > SENTIMENT_THRESHOLDS['positive_min']:
                return 'Positive'
            elif score < SENTIMENT_THRESHOLDS['negative_max']:
                return 'Negative'
            else:
                return 'Neutral'
        
        self.df['sentiment_category'] = self.df['sentiment_score'].apply(categorize_sentiment)
    
    def _analyze_aspects(self) -> None:
        """Perform aspect-based analysis."""
        aspect_data = []
        
        for idx, row in self.df.iterrows():
            text = str(row['review_text']).lower()
            for aspect, keywords in ASPECT_KEYWORDS.items():
                mentions = sum(1 for keyword in keywords if keyword in text)
                if mentions > 0:
                    aspect_data.append({
                        'aspect': aspect,
                        'sentiment': row['sentiment_score'],
                        'source': row['source']
                    })
        
        self.aspect_df = pd.DataFrame(aspect_data)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if self.df.empty:
            return {}
        
        return {
            'total_reviews': len(self.df),
            'avg_rating': self.df['rating'].mean() if self.df['rating'].notna().any() else 0,
            'avg_sentiment': self.df['sentiment_score'].mean(),
            'sources': self.df['source'].value_counts().to_dict(),
            'sentiment_dist': self.df['sentiment_category'].value_counts().to_dict(),
            'rating_dist': self.df['rating'].value_counts().to_dict() if self.df['rating'].notna().any() else {},
            'top_keywords': self.get_top_keywords()
        }
    
    def get_top_keywords(self, n: int = 20) -> List[tuple]:
        """Extract top keywords from reviews."""
        all_text = ' '.join(self.df['review_text'].astype(str))
        # Simple tokenization
        words = re.findall(r'\b\w+\b', all_text.lower())
        # Remove stop words and short words
        words = [w for w in words if len(w) > 2 and w not in STOP_WORDS]
        return Counter(words).most_common(n)
    
    def get_aspect_sentiment(self) -> Dict[str, float]:
        """Get aspect-based sentiment summary."""
        if hasattr(self, 'aspect_df') and not self.aspect_df.empty:
            return self.aspect_df.groupby('aspect')['sentiment'].mean().to_dict()
        return {}
    
    def get_ratings_by_source(self) -> Dict[str, Dict[str, Any]]:
        """Get rating statistics by source."""
        ratings_by_source = {}
        
        for source in self.df['source'].unique():
            source_data = self.df[self.df['source'] == source]
            ratings = source_data['rating'].dropna()
            
            if len(ratings) > 0:
                rating_dist = ratings.value_counts().sort_index().to_dict()
                # Ensure all ratings 1-5 are represented
                for i in range(1, 6):
                    if i not in rating_dist:
                        rating_dist[i] = 0
                
                ratings_by_source[source] = {
                    'avg_rating': ratings.mean(),
                    'total_ratings': len(ratings),
                    'distribution': rating_dist
                }
        
        return ratings_by_source
    
    def get_reviews_by_source(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all reviews organized by source and sorted by date."""
        reviews_by_source = {}
        
        for source in self.df['source'].unique():
            source_data = self.df[self.df['source'] == source].copy()
            # Sort by date (most recent first)
            source_data = source_data.sort_values('date', ascending=False, na_position='last')
            
            reviews_list = []
            for _, review in source_data.iterrows():
                reviews_list.append({
                    'author': review['author'],
                    'rating': review['rating'] if pd.notna(review['rating']) else 'N/A',
                    'date': review['date'].strftime('%Y-%m-%d') if pd.notna(review['date']) else 'N/A',
                    'text': review['review_text'],
                    'sentiment': review['sentiment_category']
                })
            
            reviews_by_source[source] = reviews_list
        
        return reviews_by_source
    
    def is_data_loaded(self) -> bool:
        """Check if data has been loaded."""
        return not self.df.empty
    
    def get_data_info(self) -> Dict[str, Any]:
        """Get basic information about the loaded data."""
        if self.df.empty:
            return {'status': 'No data loaded'}
        
        return {
            'status': 'Data loaded',
            'total_reviews': len(self.df),
            'sources': list(self.df['source'].unique()),
            'date_range': {
                'start': self.df['date'].min(),
                'end': self.df['date'].max()
            } if self.df['date'].notna().any() else None
        }
