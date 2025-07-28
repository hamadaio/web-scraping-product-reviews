#!/bin/bash

# Zendesk Tickets Scraper Runner
# This script runs the Zendesk scraper and handles the data flow

echo "Starting Zendesk tickets scraper..."
echo "$(date)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Navigate to the scraper directory
cd "$(dirname "$0")"

# Check if configuration is set up
if grep -q "your-subdomain" zendesk_tickets_scraper.js; then
    echo "WARNING: Zendesk configuration not set up!"
    echo "Please edit zendesk_tickets_scraper.js and update the ZENDESK_CONFIG section"
    echo "See README_SETUP.md for instructions"
    echo ""
    echo "You need to update these values:"
    echo "  - subdomain: your Zendesk subdomain"
    echo "  - email: your Zendesk admin email"
    echo "  - apiToken: your Zendesk API token"
    exit 1
fi

echo "Running Zendesk scraper..."
node zendesk_tickets_scraper.js

if [ $? -eq 0 ]; then
    echo ""
    echo "Zendesk scraper completed successfully!"
    echo "Check the current directory for generated CSV and JSON files"
    echo "The zendesk_reviews.json file has been copied to ../../dashboard/data/"
    echo "You can now run the dashboard to see Zendesk data included in the analysis"
else
    echo ""
    echo "Zendesk scraper failed. Check the error messages above."
    echo "Common issues:"
    echo "  - Invalid API credentials"
    echo "  - Network connectivity problems"
    echo "  - Zendesk API rate limiting"
    echo "  - Insufficient permissions"
fi

echo ""
echo "Completed at: $(date)"
