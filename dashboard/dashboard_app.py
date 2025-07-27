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
    
    def generate_html(self):
        """Generate the HTML dashboard."""
        stats = self.get_summary_stats()
        aspect_sentiment = self.get_aspect_sentiment()
        
        # Prepare data for charts
        sentiment_class = 'positive' if stats['avg_sentiment'] > 0.1 else 'negative' if stats['avg_sentiment'] < -0.1 else 'neutral'
        
        # Keywords HTML
        keywords_html = ''.join([f'<span class="keyword-tag">{word} ({count})</span>' 
                                for word, count in stats['top_keywords'][:15]])
        
        # Chart data
        source_data = stats['sources']
        sentiment_data = stats['sentiment_dist']
        rating_data = stats['rating_dist']
        
        # Convert data for JavaScript
        source_values = list(source_data.values())
        source_labels = list(source_data.keys())
        sentiment_labels = list(sentiment_data.keys())
        sentiment_values = list(sentiment_data.values())
        rating_labels = list(rating_data.keys()) if rating_data else [1,2,3,4,5]
        rating_values = list(rating_data.values()) if rating_data else [0,0,0,0,0]
        aspect_labels = list(aspect_sentiment.keys())
        aspect_values = list(aspect_sentiment.values())
        aspect_colors = ['"#28a745"' if v > 0.1 else '"#dc3545"' if v < -0.1 else '"#ffc107"' 
                        for v in aspect_sentiment.values()]
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 15px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 30px; 
            text-align: center; 
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            padding: 30px; 
            background: #f8f9ff;
        }}
        .stat-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            text-align: center; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }}
        .stat-label {{ color: #666; text-transform: uppercase; font-size: 0.9em; letter-spacing: 1px; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        .neutral {{ color: #ffc107; }}
        .primary {{ color: #007bff; }}
        .charts-container {{ padding: 30px; }}
        .chart-row {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 30px; 
            margin-bottom: 30px; 
        }}
        .chart-single {{ margin-bottom: 30px; }}
        .chart-box {{ 
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        .chart-title {{ 
            font-size: 1.3em; 
            margin-bottom: 15px; 
            color: #333; 
            border-bottom: 2px solid #667eea; 
            padding-bottom: 10px;
        }}
        .refresh-btn {{ 
            position: fixed; 
            bottom: 30px; 
            right: 30px; 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 15px 25px; 
            border-radius: 50px; 
            font-size: 1em; 
            cursor: pointer; 
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        .refresh-btn:hover {{ 
            background: #764ba2; 
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }}
        .keyword-list {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 10px; 
            margin-top: 15px; 
        }}
        .keyword-tag {{ 
            background: #e3f2fd; 
            color: #1976d2; 
            padding: 8px 15px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            font-weight: 500;
        }}
        @media (max-width: 768px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Review Analytics Dashboard</h1>
            <p>Multi-Platform Review Analysis & Insights</p>
        </div>
        
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
                <div class="stat-value {sentiment_class}">{stats['avg_sentiment']:+.2f}</div>
                <div class="stat-label">Sentiment Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value primary">{len(source_data)}</div>
                <div class="stat-label">Data Sources</div>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-row">
                <div class="chart-box">
                    <div class="chart-title">Reviews by Platform</div>
                    <div id="sourceChart"></div>
                </div>
                <div class="chart-box">
                    <div class="chart-title">Sentiment Distribution</div>
                    <div id="sentimentChart"></div>
                </div>
            </div>
            
            <div class="chart-row">
                <div class="chart-box">
                    <div class="chart-title">Rating Distribution</div>
                    <div id="ratingChart"></div>
                </div>
                <div class="chart-box">
                    <div class="chart-title">Aspect Sentiment</div>
                    <div id="aspectChart"></div>
                </div>
            </div>
            
            <div class="chart-single">
                <div class="chart-box">
                    <div class="chart-title">Top Keywords</div>
                    <div class="keyword-list">
                        {keywords_html}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">Refresh</button>
    
    <script>
        // Source distribution chart
        var sourceData = [{{
            values: {source_values},
            labels: {source_labels},
            type: 'pie',
            marker: {{
                colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
            }}
        }}];
        Plotly.newPlot('sourceChart', sourceData, {{
            showlegend: true,
            height: 300
        }});
        
        // Sentiment distribution chart
        var sentimentData = [{{
            x: {sentiment_labels},
            y: {sentiment_values},
            type: 'bar',
            marker: {{
                color: ['#28a745', '#ffc107', '#dc3545']
            }}
        }}];
        Plotly.newPlot('sentimentChart', sentimentData, {{
            height: 300,
            xaxis: {{ title: 'Sentiment' }},
            yaxis: {{ title: 'Count' }}
        }});
        
        // Rating distribution chart
        var ratingData = [{{
            x: {rating_labels},
            y: {rating_values},
            type: 'bar',
            marker: {{
                color: '#667eea'
            }}
        }}];
        Plotly.newPlot('ratingChart', ratingData, {{
            height: 300,
            xaxis: {{ title: 'Rating' }},
            yaxis: {{ title: 'Count' }}
        }});
        
        // Aspect sentiment chart
        var aspectData = [{{
            x: {aspect_values},
            y: {aspect_labels},
            type: 'bar',
            orientation: 'h',
            marker: {{
                color: {aspect_colors}
            }}
        }}];
        Plotly.newPlot('aspectChart', aspectData, {{
            height: 400,
            xaxis: {{ title: 'Average Sentiment' }},
            yaxis: {{ title: 'Aspect' }}
        }});
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
