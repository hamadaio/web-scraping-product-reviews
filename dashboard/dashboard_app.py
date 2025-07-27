"""
Lightweight Review Analytics Dashboard
A simplified version that works with minimal dependencies.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
from collections import Counter
from textblob import TextBlob
from typing import Dict, List, Any
import webbrowser
import http.server
import socketserver
import threading
from urllib.parse import parse_qs, urlparse

class SimpleDashboard:
    """
    A lightweight dashboard using basic HTML/CSS/JavaScript and Python's built-in server.
    """
    
    def __init__(self, data_dir="./data", port=8050):
        self.data_dir = data_dir
        self.port = port
        self.df = pd.DataFrame()
        self.aspect_keywords = {
            "User Experience": ["app", "interface", "ui", "design", "navigation", "easy", "difficult", "intuitive"],
            "Performance": ["performance", "speed", "fast", "slow", "lag", "crash", "bug", "works", "broken"],
            "Features": ["feature", "function", "tool", "option", "tracking", "data", "analysis"],
            "Hardware": ["battery", "device", "headset", "bluetooth", "connection", "charge"],
            "Comfort": ["comfort", "fit", "wear", "ergonomic", "size", "adjustment"],
            "Results": ["result", "effective", "improvement", "helpful", "meditation", "focus"],
            "Value": ["price", "value", "expensive", "cheap", "worth", "money"],
            "Support": ["support", "service", "help", "customer", "warranty", "response"],
            "Delivery": ["shipping", "delivery", "package", "fast", "delayed"]
        }
    
    def load_data(self):
        """Load and process review data from JSON files."""
        all_data = []
        
        if not os.path.exists(self.data_dir):
            print(f"Data directory {self.data_dir} not found!")
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Determine source
                    if 'google' in filename.lower() or 'play' in filename.lower():
                        source = 'Google Play'
                    elif 'apple' in filename.lower() or 'app_store' in filename.lower():
                        source = 'App Store'
                    elif 'trustpilot' in filename.lower():
                        source = 'Trustpilot'
                    else:
                        source = 'Unknown'
                    
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
            self.analyze_sentiment()
            self.analyze_aspects()
            print(f"Loaded {len(self.df)} reviews from {self.df['source'].nunique()} sources")
        else:
            print("No data found!")
    
    def analyze_sentiment(self):
        """Analyze sentiment using TextBlob."""
        def get_sentiment(text):
            if not text:
                return 0
            blob = TextBlob(str(text))
            return blob.sentiment.polarity
        
        self.df['sentiment_score'] = self.df['review_text'].apply(get_sentiment)
        
        def categorize_sentiment(score):
            if score > 0.1:
                return 'Positive'
            elif score < -0.1:
                return 'Negative'
            else:
                return 'Neutral'
        
        self.df['sentiment_category'] = self.df['sentiment_score'].apply(categorize_sentiment)
    
    def analyze_aspects(self):
        """Perform aspect-based analysis."""
        aspect_data = []
        
        for idx, row in self.df.iterrows():
            text = str(row['review_text']).lower()
            for aspect, keywords in self.aspect_keywords.items():
                mentions = sum(1 for keyword in keywords if keyword in text)
                if mentions > 0:
                    aspect_data.append({
                        'aspect': aspect,
                        'sentiment': row['sentiment_score'],
                        'source': row['source']
                    })
        
        self.aspect_df = pd.DataFrame(aspect_data)
    
    def get_summary_stats(self):
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
    
    def get_top_keywords(self, n=20):
        """Extract top keywords."""
        all_text = ' '.join(self.df['review_text'].astype(str))
        # Simple tokenization
        words = re.findall(r'\b\w+\b', all_text.lower())
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'it', 'that', 'this'}
        words = [w for w in words if len(w) > 2 and w not in stop_words]
        return Counter(words).most_common(n)
    
    def get_aspect_sentiment(self):
        """Get aspect-based sentiment summary."""
        if hasattr(self, 'aspect_df') and not self.aspect_df.empty:
            return self.aspect_df.groupby('aspect')['sentiment'].mean().to_dict()
        return {}
    
    def get_ratings_by_source(self):
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
    
    def get_reviews_by_source(self):
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
                    'text': review['review_text'],  # Display full text without truncation
                    'sentiment': review['sentiment_category']
                })
            
            reviews_by_source[source] = reviews_list
        
        return reviews_by_source

    def generate_html(self):
        """Generate the HTML dashboard."""
        stats = self.get_summary_stats()
        ratings_by_source = self.get_ratings_by_source()
        reviews_by_source = self.get_reviews_by_source()
        
        # Prepare data for charts
        sentiment_class = 'positive' if stats['avg_sentiment'] > 0.1 else 'negative' if stats['avg_sentiment'] < -0.1 else 'neutral'
        sentiment_label = 'Good' if stats['avg_sentiment'] > 0.1 else 'Bad' if stats['avg_sentiment'] < -0.1 else 'Neutral'
        
        # Chart data
        source_data = stats['sources']
        
        # Convert data for JavaScript
        source_values = list(source_data.values())
        source_labels = list(source_data.keys())
        
        # Generate ratings cards HTML
        ratings_cards_html = ""
        chart_id = 0
        for source, data in ratings_by_source.items():
            chart_id += 1
            
            ratings_cards_html += f"""
            <div class="source-rating-card">
                <h3>{source}</h3>
                <div class="source-stats">
                    <div class="source-stat">
                        <div class="stat-value">{data['avg_rating']:.1f}/5</div>
                        <div class="stat-label">Average Rating</div>
                    </div>
                    <div class="source-stat">
                        <div class="stat-value">{data['total_ratings']}</div>
                        <div class="stat-label">Total Ratings</div>
                    </div>
                </div>
                <div class="rating-distribution">
                    <h4>Rating Distribution</h4>
                    <div id="ratingChart{chart_id}"></div>
                </div>
            </div>
            """
        
        # Generate reviews HTML
        reviews_html = ""
        for source, reviews in reviews_by_source.items():
            reviews_list = ''.join([f"""
            <div class="review-item">
                <div class="review-header">
                    <span class="review-author">{review['author']}</span>
                    <span class="review-rating">{'★' * int(float(review['rating'])) if review['rating'] != 'N/A' and review['rating'] is not None else 'N/A'}</span>
                    <span class="review-date">{review['date']}</span>
                    <span class="sentiment-badge {review['sentiment'].lower()}">{review['sentiment']}</span>
                </div>
                <div class="review-text">{review['text']}</div>
            </div>
            """ for review in reviews])  # Display all reviews
            
            reviews_html += f"""
            <div class="source-reviews">
                <h3>{source} Reviews ({len(reviews)} total)</h3>
                <div class="reviews-list">
                    {reviews_list}
                </div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Reviews Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: #111111;
            min-height: 100vh;
            color: #ffffff;
            font-size: 14px;
            line-height: 1.5;
        }}
        .container {{ 
            max-width: 1600px; 
            margin: 0 auto; 
            background: #111111; 
            min-height: 100vh;
        }}
        .header {{ 
            background: #1e1e1e; 
            color: white; 
            padding: 25px 30px; 
            border-bottom: 1px solid #333;
        }}
        .header h1 {{ 
            font-size: 28px; 
            font-weight: 300; 
            margin-bottom: 8px; 
            letter-spacing: 0.5px;
        }}
        .header p {{ 
            opacity: 0.8; 
            font-size: 16px; 
            font-weight: 300;
        }}
        
        /* Tabs */
        .tabs {{ 
            display: flex; 
            background: #1e1e1e; 
            border-bottom: 1px solid #333;
            padding: 0 30px;
        }}
        .tab {{ 
            padding: 15px 20px; 
            cursor: pointer; 
            border: none; 
            background: transparent; 
            color: #a0a0a0; 
            font-size: 14px;
            font-weight: 400;
            transition: all 0.2s ease;
            border-bottom: 3px solid transparent;
        }}
        .tab:hover {{ 
            color: #ffffff; 
            background: rgba(255,255,255,0.05);
        }}
        .tab.active {{ 
            color: #ffffff; 
            border-bottom-color: #1f77b4;
            background: rgba(31, 119, 180, 0.1);
        }}
        
        .tab-content {{ 
            display: none; 
            padding: 30px; 
        }}
        .tab-content.active {{ display: block; }}
        
        /* Overview Tab */
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px;
        }}
        .stat-card {{ 
            background: #1e1e1e; 
            padding: 25px; 
            border-radius: 8px; 
            border: 1px solid #333;
            transition: box-shadow 0.2s ease;
        }}
        .stat-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        .stat-value {{ 
            font-size: 32px; 
            font-weight: 300; 
            margin-bottom: 8px; 
            line-height: 1;
        }}
        .stat-label {{ 
            color: #a0a0a0; 
            text-transform: none; 
            font-size: 14px; 
            font-weight: 400;
            letter-spacing: normal;
        }}
        .positive {{ color: #2ca02c; }}
        .negative {{ color: #d62728; }}
        .neutral {{ color: #ff7f0e; }}
        .primary {{ color: #1f77b4; }}
        
        .chart-box {{ 
            background: #1e1e1e; 
            border-radius: 8px; 
            padding: 25px; 
            margin-bottom: 20px;
            border: 1px solid #333;
        }}
        .chart-box h3 {{
            color: #ffffff;
            font-size: 18px;
            font-weight: 400;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #333;
        }}
        
        /* Ratings Tab */
        .source-rating-card {{ 
            background: #1e1e1e; 
            border-radius: 8px; 
            padding: 25px; 
            margin-bottom: 25px;
            border: 1px solid #333;
        }}
        .source-rating-card h3 {{ 
            color: #ffffff; 
            margin-bottom: 20px; 
            font-size: 20px;
            font-weight: 400;
        }}
        .source-stats {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 25px; 
            margin-bottom: 25px;
        }}
        .source-stat {{ 
            text-align: center;
            padding: 15px;
            background: rgba(255,255,255,0.02);
            border-radius: 6px;
        }}
        .rating-distribution h4 {{ 
            margin-bottom: 20px; 
            color: #a0a0a0;
            font-size: 16px;
            font-weight: 400;
        }}
        .rating-distribution {{ margin-top: 25px; }}
        
        /* Reviews Tab */
        .source-reviews {{ margin-bottom: 40px; }}
        .source-reviews h3 {{ 
            color: #ffffff; 
            margin-bottom: 20px; 
            font-size: 20px; 
            font-weight: 400;
            border-bottom: 1px solid #333; 
            padding-bottom: 15px;
        }}
        .reviews-list {{ 
            max-height: 800px; 
            overflow-y: auto; 
            padding-right: 10px;
        }}
        .reviews-list::-webkit-scrollbar {{
            width: 6px;
        }}
        .reviews-list::-webkit-scrollbar-track {{
            background: #111111;
            border-radius: 3px;
        }}
        .reviews-list::-webkit-scrollbar-thumb {{
            background: #555;
            border-radius: 3px;
        }}
        .reviews-list::-webkit-scrollbar-thumb:hover {{
            background: #777;
        }}
        .review-item {{ 
            background: #1e1e1e; 
            border-radius: 6px; 
            padding: 20px; 
            margin-bottom: 15px;
            border: 1px solid #333;
            transition: border-color 0.2s ease;
        }}
        .review-item:hover {{
            border-color: #555;
        }}
        .review-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 12px; 
            flex-wrap: wrap; 
            gap: 12px;
        }}
        .review-author {{ 
            font-weight: 600; 
            color: #1f77b4; 
            font-size: 14px;
        }}
        .review-rating {{ 
            color: #ff7f0e; 
            font-size: 14px;
        }}
        .review-date {{ 
            color: #a0a0a0; 
            font-size: 13px;
        }}
        .sentiment-badge {{ 
            padding: 4px 10px; 
            border-radius: 12px; 
            font-size: 12px; 
            font-weight: 500;
        }}
        .sentiment-badge.positive {{ background: rgba(44, 160, 44, 0.2); color: #2ca02c; border: 1px solid rgba(44, 160, 44, 0.3); }}
        .sentiment-badge.negative {{ background: rgba(214, 39, 40, 0.2); color: #d62728; border: 1px solid rgba(214, 39, 40, 0.3); }}
        .sentiment-badge.neutral {{ background: rgba(255, 127, 14, 0.2); color: #ff7f0e; border: 1px solid rgba(255, 127, 14, 0.3); }}
        .review-text {{ 
            color: #d0d0d0; 
            line-height: 1.6; 
            margin-top: 12px;
            font-size: 14px;
        }}
        
        .refresh-btn {{ 
            position: fixed; 
            bottom: 30px; 
            right: 30px; 
            background: #1f77b4; 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 6px; 
            font-size: 14px; 
            font-weight: 500;
            cursor: pointer; 
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
            transition: all 0.2s ease;
        }}
        .refresh-btn:hover {{ 
            background: #1861a0; 
            transform: translateY(-1px); 
            box-shadow: 0 6px 16px rgba(31, 119, 180, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .tabs {{ 
                flex-direction: column; 
                padding: 0;
            }}
            .tab {{
                padding: 12px 20px;
                border-bottom: 1px solid #333;
                border-right: none;
            }}
            .tab.active {{
                border-bottom-color: #1f77b4;
                border-left: 3px solid #1f77b4;
            }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .source-stats {{ grid-template-columns: 1fr; }}
            .review-header {{ flex-direction: column; align-items: flex-start; }}
            .tab-content {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Product Reviews Dashboard</h1>
            <p>multi-platform review analysis & insights</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">Overview</button>
            <button class="tab" onclick="showTab('ratings')">Ratings</button>
            <button class="tab" onclick="showTab('reviews')">Reviews</button>
        </div>
        
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value primary">{stats['total_reviews']}</div>
                    <div class="stat-label">Total Reviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">{stats['avg_rating']:.1f}/5</div>
                    <div class="stat-label">Average Rating</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {sentiment_class}">{stats['avg_sentiment']:+.2f} ({sentiment_label})</div>
                    <div class="stat-label">Sentiment Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">{len(source_data)}</div>
                    <div class="stat-label">Data Sources</div>
                </div>
            </div>
            
            <div class="chart-box">
                <h3>Reviews by Platform</h3>
                <div id="sourceChart"></div>
            </div>
        </div>
        
        <!-- Ratings Tab -->
        <div id="ratings" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value primary">{stats['total_reviews']}</div>
                    <div class="stat-label">Total Reviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">{stats['avg_rating']:.1f}/5</div>
                    <div class="stat-label">Average Rating</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value {sentiment_class}">{stats['avg_sentiment']:+.2f} ({sentiment_label})</div>
                    <div class="stat-label">Sentiment Score</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">{len(source_data)}</div>
                    <div class="stat-label">Data Sources</div>
                </div>
            </div>
            
            {ratings_cards_html}
        </div>
        
        <!-- Reviews Tab -->
        <div id="reviews" class="tab-content">
            {reviews_html}
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">Refresh</button>
    
    <script>
        // Tab functionality
        function showTab(tabName) {{
            // Hide all tab contents
            var contents = document.querySelectorAll('.tab-content');
            contents.forEach(function(content) {{
                content.classList.remove('active');
            }});
            
            // Remove active class from all tabs
            var tabs = document.querySelectorAll('.tab');
            tabs.forEach(function(tab) {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }}
        
        // Plotly theme configuration matching medical dashboard
        var plotlyConfig = {{
            displayModeBar: false,
            responsive: true
        }};
        
        var plotlyLayout = {{
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#1e1e1e',
            font: {{ 
                family: 'Source Sans Pro, sans-serif',
                size: 12,
                color: '#ffffff' 
            }},
            showlegend: true,
            height: 350,
            margin: {{ t: 20, r: 20, b: 40, l: 40 }},
            grid: {{ color: '#333', width: 0.5 }}
        }};
        
        // Source distribution chart
        var sourceData = [{{
            values: {source_values},
            labels: {source_labels},
            type: 'pie',
            hole: 0.3,
            marker: {{
                colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
                line: {{ color: '#1e1e1e', width: 2 }}
            }},
            textfont: {{ 
                color: '#ffffff',
                family: 'Source Sans Pro, sans-serif',
                size: 12
            }},
            textinfo: 'label+percent',
            textposition: 'outside'
        }}];
        
        var sourceLayout = Object.assign({{}}, plotlyLayout, {{
            showlegend: false,
            annotations: [{{
                text: 'Reviews<br>by Platform',
                x: 0.5, y: 0.5,
                font: {{ size: 16, color: '#a0a0a0' }},
                showarrow: false
            }}]
        }});
        
        Plotly.newPlot('sourceChart', sourceData, sourceLayout, plotlyConfig);
        
        // Rating distribution charts for each source
        var ratings_data = {json.dumps(ratings_by_source)};
        var chart_id = 0;
        
        for (var source in ratings_data) {{
            chart_id++;
            var distribution = ratings_data[source].distribution;
            var rating_labels = Object.keys(distribution);
            var rating_values = Object.values(distribution);
            
            var ratingData = [{{
                x: rating_labels,
                y: rating_values,
                type: 'bar',
                marker: {{
                    color: '#1f77b4',
                    opacity: 0.8,
                    line: {{ color: '#1f77b4', width: 1 }}
                }},
                text: rating_values,
                textposition: 'outside',
                textfont: {{ color: '#ffffff', size: 11 }},
                showlegend: false
            }}];
            
            var ratingLayout = Object.assign({{}}, plotlyLayout, {{
                showlegend: false,
                xaxis: {{ 
                    title: {{ text: 'Rating Stars', font: {{ color: '#a0a0a0', size: 12 }} }},
                    tickfont: {{ color: '#ffffff', size: 11 }},
                    gridcolor: '#333',
                    linecolor: '#555',
                    showgrid: true
                }},
                yaxis: {{ 
                    title: {{ text: 'Count', font: {{ color: '#a0a0a0', size: 12 }} }},
                    tickfont: {{ color: '#ffffff', size: 11 }},
                    gridcolor: '#333',
                    linecolor: '#555',
                    showgrid: true
                }},
                height: 280,
                margin: {{ t: 20, r: 20, b: 50, l: 50 }}
            }});
            
            Plotly.newPlot('ratingChart' + chart_id, ratingData, ratingLayout, plotlyConfig);
        }}
    </script>
</body>
</html>"""
        
        return html_content
    
    def run(self):
        """Run the dashboard."""
        print("Starting Review Analytics Dashboard...")
        
        # Load data
        self.load_data()
        
        if self.df.empty:
            print("No data found! Generating sample data...")
            # Generate sample data
            from sample_data_generator import SampleDataGenerator
            generator = SampleDataGenerator()
            generator.save_sample_data(self.data_dir)
            self.load_data()
        
        # Generate HTML
        html_content = self.generate_html()
        
        # Save HTML file
        html_file = 'dashboard.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Start simple HTTP server
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/dashboard.html'
                return super().do_GET()
        
        try:
            with socketserver.TCPServer(("", self.port), DashboardHandler) as httpd:
                url = f"http://localhost:{self.port}"
                print(f"Dashboard running at: {url}")
                print("Dashboard features:")
                print("   • Multi-platform review aggregation")
                print("   • Sentiment analysis & categorization")
                print("   • Aspect-based insights")
                print("   • Interactive visualizations")
                print("   • Real-time keyword analysis")
                print("\nRefresh the page to reload data")
                print("Press Ctrl+C to stop the server")
                
                # Open browser
                webbrowser.open(url)
                
                # Serve forever
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\nDashboard stopped!")
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Port {self.port} is already in use. Try a different port:")
                print(f"   python3 dashboard_app.py --port 8051")
            else:
                print(f"Error starting server: {e}")

if __name__ == "__main__":
    import sys
    
    port = 8050
    if len(sys.argv) > 1 and sys.argv[1] == '--port' and len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    dashboard = SimpleDashboard(port=port)
    dashboard.run()
