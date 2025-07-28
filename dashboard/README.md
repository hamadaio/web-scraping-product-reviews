# Review Analytics Dashboard

A comprehensive web-based dashboard for analyzing product reviews from multiple platforms including Google Play Store, Apple App Store, and Trustpilot.

## Features

### 📊 Multi-Platform Data Integration
- Aggregates reviews from Google Play, App Store, and Trustpilot
- Standardizes data format across different sources
- Handles various date formats and rating scales

### 🎯 Advanced Analytics
- **Sentiment Analysis**: Uses TextBlob and VADER for comprehensive sentiment scoring
- **Aspect-Based Analysis**: Categorizes reviews into themes like UX, Performance, Features, etc.
- **Topic Modeling**: LDA-based theme extraction
- **Review Clustering**: K-means clustering for pattern discovery

### 📈 Interactive Visualizations
- Real-time filtering by source, date range, and sentiment
- Sentiment distribution charts by platform
- Rating distribution histograms
- Sentiment trends over time
- Aspect-based sentiment analysis
- Word clouds for key terms
- Theme categorization charts

### 🔍 Key Insight Categories
- **User Experience & Interface**: App usability, design, navigation
- **Performance & Reliability**: Speed, crashes, bugs, stability
- **Features & Functionality**: Core features, tools, capabilities
- **Battery & Hardware**: Device-specific aspects
- **Comfort & Usability**: Physical comfort, ergonomics
- **Results & Effectiveness**: Product outcomes and benefits
- **Value & Pricing**: Cost-effectiveness, pricing feedback
- **Customer Support & Service**: Support quality, responsiveness
- **Shipping & Delivery**: Logistics and delivery experience

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download NLTK Data** (automatically handled on first run):
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

## Usage

### 1. Prepare Your Data

Place your review JSON files in the `../data/` directory. The system expects files with these naming patterns:
- `*google*` or `*play*` for Google Play reviews
- `*apple*` or `*app_store*` for App Store reviews  
- `*trustpilot*` for Trustpilot reviews

#### Expected JSON Format:
```json
[
  {
    "id": "review_id",
    "author": "reviewer_name",
    "rating": 5,
    "review": "Review text here...",
    "date": "2024-01-15",
    "helpful": 10
  }
]
```

### 2. Add Your Data

Place your JSON review files in the `data/` directory. The dashboard supports:
- Google Play reviews (files with 'google' or 'play' in the name)
- App Store reviews (files with 'apple' or 'app_store' in the name)  
- Trustpilot reviews (files with 'trustpilot' in the name)

### 3. Run the Dashboard

```bash
python app.py
```

Then open your browser to `http://127.0.0.1:8050`

## Dashboard Sections

### 🎛️ Control Panel
- **Source Filter**: Select which platforms to include
- **Date Range**: Filter by review date
- **Sentiment Filter**: Focus on positive, negative, or neutral reviews
- **Refresh Button**: Reload data from files

### 📊 Summary Cards
- Total review count
- Average rating across all platforms
- Overall sentiment score
- Number of data sources

### 📈 Visualization Panels

1. **Sentiment by Source**: Stacked bar chart showing sentiment distribution per platform
2. **Rating Distribution**: Histogram of star ratings by platform
3. **Sentiment Timeline**: Trend analysis over time
4. **Aspect Analysis**: Sentiment scores for different product aspects
5. **Theme Categories**: Review clustering and categorization
6. **Word Cloud**: Visual representation of most common terms
7. **Key Insights**: Automated summary of findings

## Technical Architecture

### Core Components

1. **ReviewDataAggregator** (`data_aggregator.py`)
   - Loads and standardizes data from multiple sources
   - Handles different date formats and rating scales
   - Provides data summary statistics

2. **ReviewAnalyzer** (`review_analyzer.py`)
   - Comprehensive sentiment analysis (TextBlob + VADER)
   - Aspect-based sentiment categorization
   - LDA topic modeling
   - K-means clustering
   - Key phrase extraction

3. **ReviewDashboard** (`app.py`)
   - Plotly Dash web application
   - Interactive visualizations
   - Real-time filtering and updates
   - Responsive Bootstrap UI

### Data Flow

```
Raw JSON Files → Data Aggregator → Sentiment Analysis → Dashboard Visualizations
                      ↓
               Standardized DataFrame → Aspect Analysis → Interactive Filters
                      ↓
               Theme Extraction → Clustering → Real-time Updates
```

## Customization

### Adding New Aspect Categories

Edit the `aspect_keywords` dictionary in `review_analyzer.py`:

```python
self.aspect_keywords = {
    "Your Custom Category": [
        "keyword1", "keyword2", "phrase with spaces"
    ]
}
```

### Modifying Visualizations

The dashboard uses Plotly for all charts. Customize by editing the callback functions in `app.py`.

### Changing Data Sources

To support additional review platforms:

1. Add a new standardization method in `ReviewDataAggregator`
2. Update the auto-detection logic
3. Add platform-specific handling if needed

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies
- Minimum 4GB RAM recommended for large datasets
- Modern web browser with JavaScript enabled

## Performance Notes

- Dashboard loads all data into memory for fast filtering
- For very large datasets (>100k reviews), consider implementing data pagination
- Word cloud generation may be slow with extensive text data
- LDA topic modeling performance depends on review count and complexity

## Troubleshooting

### Common Issues

1. **No data showing**: Ensure JSON files are in the correct directory with proper naming
2. **Import errors**: Install all requirements with `pip install -r requirements.txt`
3. **Memory issues**: Reduce dataset size or implement data sampling
4. **Slow performance**: Check data size and consider filtering options

### Data Format Issues

The system is robust to various date formats and rating scales, but ensure your JSON structure matches the expected format with required fields: `review`, `rating`, `date`, `author`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
