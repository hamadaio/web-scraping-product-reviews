"""
Configuration file for the Review Analytics Dashboard.
Contains all constants, color schemes, and default settings.
"""

import os

# Default settings
DEFAULT_PORT = 8050
# DEFAULT_DATA_DIR = "./data" # --- relative path for data directory
# --- use absolute path to ensure correct data directory location
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Color scheme - Modern dark theme inspired by design
COLORS = {
    # Backgrounds
    'background_primary': '#0B0E1A',
    'background_secondary': '#1A1F2E',
    
    # Text colors
    'text_primary': '#F8FAFC',
    'text_secondary': '#94A3B8',
    'text_muted': '#CBD5E1',
    
    # Borders and lines
    'border_primary': '#334155',
    'border_secondary': '#64748B',
    
    # Status colors
    'positive': '#10B981',
    'negative': '#EF4444',
    'neutral': '#F59E0B',
    'primary': '#3B82F6',
    
    # Chart colors
    'chart_colors': ['#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#F97316'],
    
    # Gradients
    'gradient_primary': 'linear-gradient(135deg, #3B82F6, #6366F1)',
    'gradient_hover': 'linear-gradient(135deg, #2563EB, #4F46E5)',
}

# Aspect keywords for sentiment analysis
ASPECT_KEYWORDS = {
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

# Sentiment analysis thresholds
SENTIMENT_THRESHOLDS = {
    'positive_min': 0.1,
    'negative_max': -0.1
}

# Stop words for keyword extraction
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
    'of', 'with', 'by', 'is', 'it', 'that', 'this', 'are', 'was', 'were',
    'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'must', 'can', 'shall'
}

# Source detection patterns
SOURCE_PATTERNS = {
    'Google Play': ['google', 'play'],
    'App Store': ['apple', 'app_store'],
    'Trustpilot': ['trustpilot']
}

# Chart configuration
CHART_CONFIG = {
    'plotly_config': {
        'displayModeBar': False,
        'responsive': True
    },
    'default_height': 350,
    'rating_chart_height': 280
}
