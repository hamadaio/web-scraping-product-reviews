# Modular Review Analytics Dashboard

A refactored, modular version of the review analytics dashboard with improved maintainability and organization.

## 📁 File Structure

```
dashboard/
├── dashboard_app_modular.py  # Main entry point & server logic (130 lines)
├── data_processor.py         # Data loading & analysis (180 lines)
├── html_generator.py         # HTML & CSS generation (320 lines)
├── chart_generator.py        # Chart data preparation (150 lines)
├── config.py                 # Configuration & constants (60 lines)
└── dashboard_app.py          # Original monolithic file (600+ lines)
```

## 🔧 **Module Responsibilities**

### **config.py**
- Color scheme constants
- Aspect keywords for sentiment analysis
- Default settings and thresholds
- Chart configuration

### **data_processor.py**
- JSON file loading and parsing
- Data cleaning and standardization
- Sentiment analysis using TextBlob
- Aspect-based analysis
- Statistics calculation
- Source detection logic

### **chart_generator.py**
- Plotly chart data preparation
- Chart configuration and theming
- JavaScript generation for charts
- Color scheme integration

### **html_generator.py**
- CSS styles generation
- HTML template creation
- Component rendering (cards, reviews, etc.)
- Responsive design handling

### **dashboard_app_modular.py**
- Main application orchestration
- HTTP server management
- CLI argument parsing
- Error handling and user feedback

## 🚀 **Usage**

### Run the modular version:
```bash
python dashboard_app_modular.py
```

### With custom options:
```bash
python dashboard_app_modular.py --port 8051 --data-dir ./my_data
```

### Get help:
```bash
python dashboard_app_modular.py --help
```

## ✨ **Benefits of Modular Design**

1. **Maintainability**: Each module has a single, clear responsibility
2. **Reusability**: Components can be used independently
3. **Testing**: Each module can be unit tested separately
4. **Collaboration**: Multiple developers can work on different modules
5. **Performance**: Faster imports and reduced memory footprint
6. **Readability**: Easier to understand and navigate
7. **Extensibility**: New features can be added without affecting existing code

## 🔄 **Migration**

The original `dashboard_app.py` remains unchanged for backward compatibility. The modular version provides the same functionality with improved architecture.

## 🎨 **Color Scheme**

The modular version uses the same modern dark theme with configurable colors in `config.py`:
- Background: Deep navy (#0B0E1A)
- Cards: Dark blue-gray (#1A1F2E)
- Primary: Bright blue (#3B82F6)
- Text: Crisp white (#F8FAFC)
- Accents: Green, red, amber for sentiment

## 📊 **Features**

- Multi-platform review aggregation
- Sentiment analysis & categorization
- Aspect-based insights
- Interactive visualizations
- Real-time keyword analysis
- Responsive design
- Modern dark theme
