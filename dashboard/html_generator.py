"""
HTML template generation module for the Review Analytics Dashboard.
Handles CSS styles and HTML template generation.
"""

from typing import Dict, List, Any
from config import COLORS
from chart_generator import ChartGenerator


class HTMLGenerator:
    """Generates HTML templates and CSS styles for the dashboard."""
    
    def __init__(self):
        self.colors = COLORS
        self.chart_generator = ChartGenerator()
    
    def get_css_styles(self) -> str:
        """Generate CSS styles with the configured color scheme."""
        return f"""
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@300;400;600;700&display=swap');
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: {self.colors['background_primary']};
            min-height: 100vh;
            color: {self.colors['text_primary']};
            font-size: 14px;
            line-height: 1.5;
        }}
        .container {{ 
            max-width: 1600px; 
            margin: 0 auto; 
            background: {self.colors['background_primary']}; 
            min-height: 100vh;
        }}
        .header {{ 
            background: {self.colors['background_secondary']}; 
            color: white; 
            padding: 25px 30px; 
            border-bottom: 1px solid {self.colors['border_primary']};
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
            background: {self.colors['background_secondary']}; 
            border-bottom: 1px solid {self.colors['border_primary']};
            padding: 0 30px;
        }}
        .tab {{ 
            padding: 15px 20px; 
            cursor: pointer; 
            border: none; 
            background: transparent; 
            color: {self.colors['text_secondary']}; 
            font-size: 14px;
            font-weight: 400;
            transition: all 0.2s ease;
            border-bottom: 3px solid transparent;
        }}
        .tab:hover {{ 
            color: {self.colors['text_primary']}; 
            background: rgba(59, 130, 246, 0.05);
        }}
        .tab.active {{ 
            color: {self.colors['text_primary']}; 
            border-bottom-color: {self.colors['primary']};
            background: rgba(59, 130, 246, 0.1);
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
            background: {self.colors['background_secondary']}; 
            padding: 25px; 
            border-radius: 12px; 
            border: 1px solid {self.colors['border_primary']};
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        .stat-card:hover {{
            border-color: {self.colors['primary']};
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12);
            transform: translateY(-2px);
        }}
        .stat-value {{ 
            font-size: 32px; 
            font-weight: 600; 
            margin-bottom: 8px; 
            line-height: 1;
        }}
        .stat-label {{ 
            color: {self.colors['text_secondary']}; 
            text-transform: none; 
            font-size: 14px; 
            font-weight: 400;
            letter-spacing: normal;
        }}
        .positive {{ color: {self.colors['positive']}; }}
        .negative {{ color: {self.colors['negative']}; }}
        .neutral {{ color: {self.colors['neutral']}; }}
        .primary {{ color: {self.colors['primary']}; }}
        
        .chart-box {{ 
            background: {self.colors['background_secondary']}; 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 20px;
            border: 1px solid {self.colors['border_primary']};
            backdrop-filter: blur(10px);
        }}
        .chart-box h3 {{
            color: {self.colors['text_primary']};
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid {self.colors['border_primary']};
        }}
        
        /* Ratings Tab */
        .source-rating-card {{ 
            background: {self.colors['background_secondary']}; 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 25px;
            border: 1px solid {self.colors['border_primary']};
            backdrop-filter: blur(10px);
        }}
        .source-rating-card h3 {{ 
            color: {self.colors['text_primary']}; 
            margin-bottom: 20px; 
            font-size: 20px;
            font-weight: 500;
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
            background: rgba(59, 130, 246, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(59, 130, 246, 0.1);
        }}
        .rating-distribution h4 {{ 
            margin-bottom: 20px; 
            color: {self.colors['text_secondary']};
            font-size: 16px;
            font-weight: 400;
        }}
        .rating-distribution {{ margin-top: 25px; }}
        
        /* Reviews Tab */
        .source-reviews {{ 
            background: {self.colors['background_secondary']}; 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 25px;
            border: 1px solid {self.colors['border_primary']};
            backdrop-filter: blur(10px);
        }}
        .source-reviews h3 {{ 
            color: {self.colors['text_primary']}; 
            margin-bottom: 20px; 
            font-size: 20px; 
            font-weight: 500;
        }}
        .reviews-list {{ 
            max-height: 600px; 
            overflow-y: auto; 
            padding-right: 10px;
            position: relative;
        }}
        .reviews-list::before {{
            content: '';
            position: sticky;
            top: 0;
            left: 0;
            right: 0;
            height: 20px;
            background: linear-gradient(to bottom, {self.colors['background_secondary']}, transparent);
            z-index: 10;
            pointer-events: none;
        }}
        .reviews-list::after {{
            content: '';
            position: sticky;
            bottom: 0;
            left: 0;
            right: 0;
            height: 20px;
            background: linear-gradient(to top, {self.colors['background_secondary']}, transparent);
            z-index: 10;
            pointer-events: none;
        }}
        .reviews-list::-webkit-scrollbar {{
            width: 4px;
        }}
        .reviews-list::-webkit-scrollbar-track {{
            background: transparent;
            border-radius: 2px;
        }}
        .reviews-list::-webkit-scrollbar-thumb {{
            background: rgba(148, 163, 184, 0.3);
            border-radius: 2px;
        }}
        .reviews-list::-webkit-scrollbar-thumb:hover {{
            background: rgba(148, 163, 184, 0.5);
        }}
        .review-item {{ 
            background: {self.colors['background_secondary']}; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 15px;
            border: 1px solid {self.colors['border_primary']};
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        .review-item:hover {{
            border-color: {self.colors['primary']};
            box-shadow: 0 4px 24px rgba(59, 130, 246, 0.08);
            transform: translateY(-1px);
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
            color: {self.colors['primary']}; 
            font-size: 14px;
        }}
        .review-rating {{ 
            color: {self.colors['neutral']}; 
            font-size: 14px;
        }}
        .review-date {{ 
            color: {self.colors['text_secondary']}; 
            font-size: 13px;
        }}
        .sentiment-badge {{ 
            padding: 4px 10px; 
            border-radius: 12px; 
            font-size: 12px; 
            font-weight: 500;
        }}
        .sentiment-badge.positive {{ background: rgba(16, 185, 129, 0.15); color: {self.colors['positive']}; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .sentiment-badge.negative {{ background: rgba(239, 68, 68, 0.15); color: {self.colors['negative']}; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .sentiment-badge.neutral {{ background: rgba(245, 158, 11, 0.15); color: {self.colors['neutral']}; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .review-text {{ 
            color: {self.colors['text_muted']}; 
            line-height: 1.6; 
            margin-top: 12px;
            font-size: 14px;
        }}
        
        .refresh-btn {{ 
            position: fixed; 
            bottom: 30px; 
            right: 30px; 
            background: {self.colors['gradient_primary']}; 
            color: white; 
            border: none; 
            padding: 12px 20px; 
            border-radius: 12px; 
            font-size: 14px; 
            font-weight: 500;
            cursor: pointer; 
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        .refresh-btn:hover {{ 
            background: {self.colors['gradient_hover']}; 
            transform: translateY(-2px); 
            box-shadow: 0 12px 40px rgba(59, 130, 246, 0.4);
        }}
        
        /* Sources Tab */
        .source-item {{ 
            background: #0B0E1A; 
            border: 1px solid #475569; 
            border-radius: 8px; 
            padding: 20px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .source-item:hover {{
            border-color: {self.colors['primary']};
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.12);
            transform: translateY(-2px);
        }}
        
        @media (max-width: 768px) {{
            .tabs {{ 
                flex-direction: column; 
                padding: 0;
            }}
            .tab {{
                padding: 12px 20px;
                border-bottom: 1px solid {self.colors['border_primary']};
                border-right: none;
            }}
            .tab.active {{
                border-bottom-color: {self.colors['primary']};
                border-left: 3px solid {self.colors['primary']};
            }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .source-stats {{ grid-template-columns: 1fr; }}
            .review-header {{ flex-direction: column; align-items: flex-start; }}
            .tab-content {{ padding: 20px; }}
        }}
        """
    
    def generate_ratings_cards_html(self, ratings_by_source: Dict[str, Dict[str, Any]]) -> str:
        """Generate HTML for rating cards."""
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
        
        return ratings_cards_html
    
    def generate_reviews_html(self, reviews_by_source: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate HTML for reviews section."""
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
            """ for review in reviews])
            
            reviews_html += f"""
            <div class="source-reviews">
                <h3>{source} Reviews ({len(reviews)} total)</h3>
                <div class="reviews-list">
                    {reviews_list}
                </div>
            </div>
            """
        
        return reviews_html
    
    def generate_complete_html(self, stats: Dict[str, Any], 
                              ratings_by_source: Dict[str, Dict[str, Any]], 
                              reviews_by_source: Dict[str, List[Dict[str, Any]]]) -> str:
        """Generate the complete HTML dashboard."""
        
        # Prepare data for display
        sentiment_class = 'positive' if stats['avg_sentiment'] > 0.1 else 'negative' if stats['avg_sentiment'] < -0.1 else 'neutral'
        sentiment_label = 'Good' if stats['avg_sentiment'] > 0.1 else 'Bad' if stats['avg_sentiment'] < -0.1 else 'Neutral'
        
        source_data = stats['sources']
        
        # Generate sections
        ratings_cards_html = self.generate_ratings_cards_html(ratings_by_source)
        reviews_html = self.generate_reviews_html(reviews_by_source)
        chart_js = self.chart_generator.generate_chart_javascript(ratings_by_source, source_data)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Reviews Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        {self.get_css_styles()}
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
            <button class="tab" onclick="showTab('analysis')">Analysis & Insights</button>
            <button class="tab" onclick="showTab('query')">Query</button>
            <button class="tab" onclick="showTab('zendesk')">Zendesk</button>
            <button class="tab" onclick="showTab('sources')">Sources</button>
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
                <h3>Platforms</h3>
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
        
        <!-- Analysis & Insights Tab -->
        <div id="analysis" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value primary">Work in progress...</div>
                    <div class="stat-label">thematic analysis</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">Work in progress...</div>
                    <div class="stat-label">Sentiment analysis</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">Work in progress...</div>
                    <div class="stat-label">topic modeling</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value primary">Work in progress...</div>
                    <div class="stat-label">comp analysis</div>
                </div>
            </div>
        </div>
        
        <!-- Query Tab -->
        <div id="query" class="tab-content">
            <div style="padding: 40px 20px;">
                <h2 style="color: #3B82F6; margin-bottom: 30px; text-align: center;">Work in progress...</h2>
                <div style="max-width: 800px; margin: 0 auto;">
                    <div style="background: #1A1F2E; border: 1px solid #334155; border-radius: 12px; padding: 30px; margin-bottom: 30px;">
                        <h3 style="color: #F8FAFC; margin-bottom: 20px;">Natural langauge queries</h3>
                        <div style="margin-bottom: 20px;">
                            <input type="text" placeholder="Ask questions about your reviews (e.g., 'What are users saying about the UI?')" 
                                   style="width: 100%; padding: 15px; background: #0B0E1A; border: 1px solid #475569; border-radius: 8px; color: #F8FAFC; font-size: 14px;" disabled>
                        </div>
                        <button style="background: #3B82F6; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: not-allowed; opacity: 0.6;" disabled>
                            Search Reviews
                        </button>
                    </div>
                    
                    <div style="text-align: center; padding: 40px 20px; color: #94A3B8;">
                        <p style="font-size: 16px; line-height: 1.6;">
                            Tab for natural language queries.
                        </p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Zendesk Tab -->
        <div id="zendesk" class="tab-content">
            <div style="text-align: center; padding: 60px 20px; color: #94A3B8;">
                <h2 style="color: #3B82F6; margin-bottom: 20px;">Work in progress...</h2>
            </div>
        </div>
        
        <!-- Sources Tab -->
        <div id="sources" class="tab-content">
            <div style="padding: 40px 20px;">
                <h2 style="color: #3B82F6; margin-bottom: 30px; text-align: center;">Data Sources Management</h2>
                <div style="max-width: 1000px; margin: 0 auto;">
                    
                    <!-- Current Sources -->
                    <div style="background: #1A1F2E; border: 1px solid #334155; border-radius: 12px; padding: 30px; margin-bottom: 30px;">
                        <h3 style="color: #F8FAFC; margin-bottom: 20px;">Active Data Sources</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div class="source-item">
                                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                    <div style="width: 12px; height: 12px; background: #10B981; border-radius: 50%; margin-right: 10px;"></div>
                                    <h4 style="color: #F8FAFC; margin: 0;">Google Play Store</h4>
                                </div>
                                <p style="color: #94A3B8; font-size: 14px; margin-bottom: 8px;">Status: Connected</p>
                                <p style="color: #94A3B8; font-size: 14px;">Last sync: 2 hours ago</p>
                            </div>
                            <div class="source-item">
                                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                    <div style="width: 12px; height: 12px; background: #10B981; border-radius: 50%; margin-right: 10px;"></div>
                                    <h4 style="color: #F8FAFC; margin: 0;">Apple App Store</h4>
                                </div>
                                <p style="color: #94A3B8; font-size: 14px; margin-bottom: 8px;">Status: Connected</p>
                                <p style="color: #94A3B8; font-size: 14px;">Last sync: 1 hour ago</p>
                            </div>
                            <div class="source-item">
                                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                                    <div style="width: 12px; height: 12px; background: #10B981; border-radius: 50%; margin-right: 10px;"></div>
                                    <h4 style="color: #F8FAFC; margin: 0;">Trustpilot</h4>
                                </div>
                                <p style="color: #94A3B8; font-size: 14px; margin-bottom: 8px;">Status: Connected</p>
                                <p style="color: #94A3B8; font-size: 14px;">Last sync: 30 minutes ago</p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; padding: 40px 20px; color: #94A3B8;">
                        <p style="font-size: 16px; line-height: 1.6;">
                            Add explainer text...
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">Go baaaaaaaaack</button>
    
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
        
        {chart_js}
    </script>
</body>
</html>"""
        
        return html_content
