"""
Modular Review Analytics Dashboard
Main application file - orchestrates all components.
"""

import os
import sys
import webbrowser
import http.server
import socketserver
from typing import Optional

from config import DEFAULT_PORT, DEFAULT_DATA_DIR
from data_processor import DataProcessor
from html_generator import HTMLGenerator


class SimpleDashboard:
    """
    Main dashboard class that orchestrates all components.
    """
    
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR, port: int = DEFAULT_PORT):
        self.data_dir = data_dir
        self.port = port
        self.data_processor = DataProcessor(data_dir)
        self.html_generator = HTMLGenerator()
    
    def load_data(self) -> bool:
        """Load and process review data."""
        return self.data_processor.load_data()
    
    def generate_html(self) -> str:
        """Generate the HTML dashboard."""
        if not self.data_processor.is_data_loaded():
            return self._generate_no_data_html()
        
        # Get all required data
        stats = self.data_processor.get_summary_stats()
        ratings_by_source = self.data_processor.get_ratings_by_source()
        reviews_by_source = self.data_processor.get_reviews_by_source()
        
        # Generate complete HTML
        return self.html_generator.generate_complete_html(
            stats, ratings_by_source, reviews_by_source
        )
    
    def _generate_no_data_html(self) -> str:
        """Generate HTML for when no data is available."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Reviews Dashboard - No Data</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            background: #0B0E1A; 
            color: #F8FAFC; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0;
        }
        .no-data { 
            text-align: center; 
            padding: 40px; 
            background: #1A1F2E; 
            border-radius: 12px; 
            border: 1px solid #334155;
        }
        .no-data h1 { color: #3B82F6; margin-bottom: 20px; }
        .no-data p { color: #94A3B8; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="no-data">
        <h1>No Data Found</h1>
        <p>Please add JSON review files to the data directory:<br><strong>{data_dir}</strong></p>
        <p>Supported formats: Google Play, App Store, and Trustpilot reviews</p>
    </div>
</body>
</html>""".format(data_dir=self.data_dir)
    
    def _try_generate_sample_data(self) -> bool:
        """Try to generate sample data if available."""
        print("No real data found.")
        print(f"Please add JSON review files to: {self.data_dir}")
        print("Supported formats: Google Play, App Store, and Trustpilot reviews")
        return False
    
    def run(self) -> None:
        """Run the dashboard server."""
        print("Starting Review Analytics Dashboard...")
        print(f"Data directory: {self.data_dir}")
        print(f"Port: {self.port}")
        
        # Load data
        data_loaded = self.load_data()
        
        # Try to generate sample data if no data found
        if not data_loaded:
            if self._try_generate_sample_data():
                data_loaded = self.load_data()
        
        # Generate HTML
        html_content = self.generate_html()
        
        # Save HTML file
        html_file = 'dashboard.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Generated dashboard HTML: {html_file}")
        
        # Start HTTP server
        self._start_server(html_file)
    
    def _start_server(self, html_file: str) -> None:
        """Start the HTTP server."""
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = f'/{html_file}'
                return super().do_GET()
        
        try:
            with socketserver.TCPServer(("", self.port), DashboardHandler) as httpd:
                url = f"http://localhost:{self.port}"
                print(f"\n🚀 Dashboard running at: {url}")
                
                if self.data_processor.is_data_loaded():
                    data_info = self.data_processor.get_data_info()
                    print(f"📊 Loaded {data_info['total_reviews']} reviews from {len(data_info['sources'])} sources")
                    print("✨ Dashboard features:")
                    print("   • Multi-platform review aggregation")
                    print("   • Sentiment analysis & categorization") 
                    print("   • Aspect-based insights")
                    print("   • Interactive visualizations")
                    print("   • Real-time keyword analysis")
                else:
                    print("⚠️  No data loaded - showing placeholder dashboard")
                
                print(f"\n🔄 Refresh the page to reload data")
                print("⛔ Press Ctrl+C to stop the server")
                
                # Open browser
                webbrowser.open(url)
                
                # Serve forever
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            print("\n👋 Dashboard stopped!")
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"❌ Port {self.port} is already in use.")
                print(f"💡 Try a different port: python3 dashboard_app.py --port 8051")
            else:
                print(f"❌ Error starting server: {e}")
    
    def get_data_info(self) -> dict:
        """Get information about loaded data."""
        return self.data_processor.get_data_info()


def main():
    """Main entry point with CLI argument parsing."""
    port = DEFAULT_PORT
    data_dir = DEFAULT_DATA_DIR
    
    # Simple argument parsing
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--port' and i + 1 < len(args):
            try:
                port = int(args[i + 1])
                i += 2
            except ValueError:
                print(f"invalid port number: {args[i + 1]}")
                sys.exit(1)
        elif args[i] == '--data-dir' and i + 1 < len(args):
            data_dir = args[i + 1]
            i += 2
        elif args[i] in ['--help', '-h']:
            print("Review Analytics Dashboard")
            print("Usage: python dashboard_app.py [options]")
            print("")
            print("Options:")
            print(f"  --port PORT        Server port (default: {DEFAULT_PORT})")
            print(f"  --data-dir DIR     Data directory (default: {DEFAULT_DATA_DIR})")
            print("  --help, -h         Show this help message")
            sys.exit(0)
        else:
            print(f"unknown argument: {args[i]}")
            print("Use --help for usage information")
            sys.exit(1)
    
    # Create and run dashboard
    dashboard = SimpleDashboard(data_dir=data_dir, port=port)
    dashboard.run()


if __name__ == "__main__":
    main()
