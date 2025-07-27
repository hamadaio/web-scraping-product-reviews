# Data Directory

This directory contains all data files organized by processing stage.

## Structure

- `raw/` - Original scraped data files (CSV, JSON)
- `processed/` - Cleaned and processed data files

## Raw Data

Contains output from scrapers:
- Google Play Store reviews (CSV format)
- Trustpilot reviews (JSON format)

## Processed Data

Contains cleaned and analyzed data:
- Sentiment-analyzed reviews
- Feature-extracted data
- Aggregated statistics

## Data Formats

### Google Play Reviews (CSV)
- Date, User Name, Score, Review Text, Helpful Count, Reply Date, Reply Text

### Trustpilot Reviews (JSON)
- Structured JSON with review metadata and text

## Note

Raw data files are included in version control for reproducibility, but consider adding `*.csv` and `*.json` to `.gitignore` for larger datasets.
