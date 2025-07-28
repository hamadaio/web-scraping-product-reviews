"""
Chart data generation module for the Review Analytics Dashboard.
Handles preparation of data for Plotly charts and visualizations.
"""

import json
from typing import Dict, List, Any
from config import COLORS, CHART_CONFIG


class ChartGenerator:
    """Generates chart data and configurations for the dashboard."""
    
    def __init__(self):
        self.colors = COLORS
        self.config = CHART_CONFIG
    
    def get_plotly_config(self) -> Dict[str, Any]:
        """Get Plotly configuration."""
        return self.config['plotly_config']
    
    def get_base_layout(self) -> Dict[str, Any]:
        """Get base Plotly layout with theme colors."""
        return {
            'paper_bgcolor': self.colors['background_secondary'],
            'plot_bgcolor': self.colors['background_secondary'],
            'font': {
                'family': 'Source Sans Pro, sans-serif',
                'size': 12,
                'color': self.colors['text_primary']
            },
            'showlegend': True,
            'height': self.config['default_height'],
            'margin': {'t': 20, 'r': 20, 'b': 40, 'l': 40},
            'grid': {'color': self.colors['border_primary'], 'width': 0.5}
        }
    
    def prepare_source_chart_data(self, source_data: Dict[str, int]) -> tuple:
        """Prepare data for the source distribution pie chart."""
        source_values = list(source_data.values())
        source_labels = list(source_data.keys())
        
        chart_data = [{
            'values': source_values,
            'labels': source_labels,
            'type': 'pie',
            'hole': 0.3,
            'marker': {
                'colors': self.colors['chart_colors'][:len(source_labels)],
                'line': {'color': self.colors['background_secondary'], 'width': 2}
            },
            'textfont': {
                'color': self.colors['text_primary'],
                'family': 'Source Sans Pro, sans-serif',
                'size': 12
            },
            'textinfo': 'label+percent',
            'textposition': 'outside'
        }]
        
        layout = self.get_base_layout()
        layout.update({
            'showlegend': False,
            'annotations': [{
                'text': 'Reviews<br>by Platform',
                'x': 0.5, 'y': 0.5,
                'font': {'size': 16, 'color': self.colors['text_secondary']},
                'showarrow': False
            }]
        })
        
        return chart_data, layout
    
    def prepare_rating_chart_data(self, distribution: Dict[str, int]) -> tuple:
        """Prepare data for rating distribution bar chart."""
        rating_labels = list(distribution.keys())
        rating_values = list(distribution.values())
        
        chart_data = [{
            'x': rating_labels,
            'y': rating_values,
            'type': 'bar',
            'marker': {
                'color': self.colors['primary'],
                'opacity': 0.8,
                'line': {'color': self.colors['primary'], 'width': 1}
            },
            'text': rating_values,
            'textposition': 'outside',
            'textfont': {'color': self.colors['text_primary'], 'size': 11},
            'showlegend': False
        }]
        
        layout = self.get_base_layout()
        layout.update({
            'showlegend': False,
            'xaxis': {
                'title': {'text': 'Rating Stars', 'font': {'color': self.colors['text_secondary'], 'size': 12}},
                'tickfont': {'color': self.colors['text_primary'], 'size': 11},
                'gridcolor': self.colors['border_primary'],
                'linecolor': self.colors['border_secondary'],
                'showgrid': True
            },
            'yaxis': {
                'title': {'text': 'Count', 'font': {'color': self.colors['text_secondary'], 'size': 12}},
                'tickfont': {'color': self.colors['text_primary'], 'size': 11},
                'gridcolor': self.colors['border_primary'],
                'linecolor': self.colors['border_secondary'],
                'showgrid': True
            },
            'height': self.config['rating_chart_height'],
            'margin': {'t': 20, 'r': 20, 'b': 50, 'l': 50}
        })
        
        return chart_data, layout
    
    def generate_chart_javascript(self, ratings_by_source: Dict[str, Dict[str, Any]], 
                                 source_data: Dict[str, int]) -> str:
        """Generate JavaScript code for all charts."""
        
        # Prepare source chart data
        source_values = list(source_data.values())
        source_labels = list(source_data.keys())
        
        js_code = f"""
        // Plotly theme configuration
        var plotlyConfig = {json.dumps(self.get_plotly_config())};
        
        var plotlyLayout = {json.dumps(self.get_base_layout())};
        
        // Source distribution chart
        var sourceData = [{{
            values: {source_values},
            labels: {source_labels},
            type: 'pie',
            hole: 0.3,
            marker: {{
                colors: {json.dumps(self.colors['chart_colors'][:len(source_labels)])},
                line: {{ color: '{self.colors["background_secondary"]}', width: 2 }}
            }},
            textfont: {{ 
                color: '{self.colors["text_primary"]}',
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
                font: {{ size: 16, color: '{self.colors["text_secondary"]}' }},
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
                    color: '{self.colors["primary"]}',
                    opacity: 0.8,
                    line: {{ color: '{self.colors["primary"]}', width: 1 }}
                }},
                text: rating_values,
                textposition: 'outside',
                textfont: {{ color: '{self.colors["text_primary"]}', size: 11 }},
                showlegend: false
            }}];
            
            var ratingLayout = Object.assign({{}}, plotlyLayout, {{
                showlegend: false,
                xaxis: {{ 
                    title: {{ text: 'Rating Stars', font: {{ color: '{self.colors["text_secondary"]}', size: 12 }} }},
                    tickfont: {{ color: '{self.colors["text_primary"]}', size: 11 }},
                    gridcolor: '{self.colors["border_primary"]}',
                    linecolor: '{self.colors["border_secondary"]}',
                    showgrid: true
                }},
                yaxis: {{ 
                    title: {{ text: 'Count', font: {{ color: '{self.colors["text_secondary"]}', size: 12 }} }},
                    tickfont: {{ color: '{self.colors["text_primary"]}', size: 11 }},
                    gridcolor: '{self.colors["border_primary"]}',
                    linecolor: '{self.colors["border_secondary"]}',
                    showgrid: true
                }},
                height: {self.config['rating_chart_height']},
                margin: {{ t: 20, r: 20, b: 50, l: 50 }}
            }});
            
            Plotly.newPlot('ratingChart' + chart_id, ratingData, ratingLayout, plotlyConfig);
        }}
        """
        
        return js_code
