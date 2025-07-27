# Scrapers

This directory contains web scrapers for different platforms.

## Google Play Store Scrapers
- `google_play/` - Scrapers for Google Play Store app reviews

## Trustpilot Scrapers  
- `trustpilot/` - Scrapers for Trustpilot company reviews

## Usage

### Google Play Store
```bash
npm run scrape:google-play
```

### Trustpilot
```bash
npm run scrape:trustpilot
```

## Adding New Scrapers

When adding new scrapers:
1. Create a new directory for the platform (e.g., `amazon/`, `yelp/`)
2. Follow the naming convention: `{platform}_{target}_scraper.{ext}`
3. Include proper error handling and rate limiting
4. Add documentation for configuration options
