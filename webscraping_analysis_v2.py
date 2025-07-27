import os
import sys
import json
import re
import time
import pandas as pd
from datetime import datetime
from textblob import TextBlob

import plotly.graph_objs as go
import plotly.offline as pyo  # for .show() in some environments

def list_json_files():
    return [f for f in os.listdir('.') if f.lower().endswith('.json')]

def choose_json_file():
    files = list_json_files()
    if not files:
        print("No JSON files found in the current directory.")
        sys.exit(1)
    print("JSON files in the current directory:")
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f}")
    while True:
        choice = input(f"Enter the number of the file you want to analyze (1-{len(files)}): ")
        try:
            idx = int(choice)
            if 1 <= idx <= len(files):
                return files[idx - 1]
        except ValueError:
            pass
        print("Invalid choice. Please enter a valid number.")

def preprocess_text(text):
    if not text:
        return ""
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = text.lower().strip()
    return text

def aspect_based_sentiment(df):
    aspects = {
        "comfort": ["comfort", "comfortable", "fit", "headband", "ergonomic", "wearable", "snug", "tight", "loose", "padding"],
        "battery": ["battery", "battery life", "power", "charge", "charging", "runtime", "lasting", "battery drain", "battery indicator", "battery performance"],
        "shipping": ["shipping", "delivery", "arrival", "package", "tracking", "shipment", "received", "shipping time", "shipping cost", "shipping speed"],
        "app": ["app", "application", "software", "interface", "mobile", "connectivity", "connection", "bluetooth", "pairing", "sync", "crashes", "bugs"],
        "support": ["support", "customer service", "warranty", "help", "assistance", "response", "service", "customer support", "technical support", "replacement"],
        "quality": ["quality", "build", "durability", "material", "construction", "reliable", "sturdy", "flimsy", "robust", "defective", "broken"],
        "price": ["price", "cost", "value", "worth", "expensive", "cheap", "affordable", "overpriced", "reasonable price", "price point"],
        "performance": ["performance", "works", "working", "effective", "results", "improvement", "efficiency", "accuracy", "reliable", "consistent", "impact"]
    }
    results = {aspect: [] for aspect in aspects}
    for idx, row in df.iterrows():
        text = row['clean_text']
        polarity = row['sentiment']
        for aspect, keywords in aspects.items():
            if any(k in text for k in keywords):
                results[aspect].append(polarity)
    aspect_sentiments = {}
    for aspect, sentiments in results.items():
        if len(sentiments) > 0:
            aspect_sentiments[aspect] = sum(sentiments) / len(sentiments)
        else:
            aspect_sentiments[aspect] = 0
    aspect_df = pd.DataFrame({
        'Aspect': list(aspect_sentiments.keys()),
        'Average_Sentiment': list(aspect_sentiments.values())
    })
    return aspect_df

def main():
    chosen_file = choose_json_file()
    with open(chosen_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Ensure columns exist
    if 'review' not in df.columns:
        df['review'] = ""
    if 'rating' not in df.columns:
        df['rating'] = None
    if 'date' not in df.columns:
        df['date'] = None

    # Convert 'date' to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Clean the review text and compute sentiment polarity
    df['clean_text'] = df['review'].apply(preprocess_text)
    df['sentiment'] = df['clean_text'].apply(lambda x: TextBlob(x).sentiment.polarity)

    print(f"Analyzing file: {chosen_file}")
    avg_rating = df['rating'].mean(skipna=True)
    avg_sentiment = df['sentiment'].mean(skipna=True)
    print("Average Rating:", f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A")
    print("Average Sentiment (Polarity):", f"{avg_sentiment:.2f}" if pd.notna(avg_sentiment) else "N/A")

    # Aspect-Based Sentiment
    aspect_df = aspect_based_sentiment(df)
    print("\nAspect-Based Sentiment (Naive Approach):")
    print(aspect_df)

    # Convert dates to monthly periods
    df['year_month'] = df['date'].dt.to_period('M')

    # Group by month to get average sentiment, std, and count
    grouped_sentiment = (df.dropna(subset=['year_month'])
                         .groupby('year_month')['sentiment']
                         .agg(['mean', 'std', 'count'])
                         .reset_index())
    grouped_sentiment.columns = ['year_month', 'avg_sentiment', 'std_sentiment', 'count_reviews']

    # Group by month to get average rating, std, and count
    grouped_rating = (df.dropna(subset=['year_month', 'rating'])
                      .groupby('year_month')['rating']
                      .agg(['mean', 'std', 'count'])
                      .reset_index())
    grouped_rating.columns = ['year_month', 'avg_rating', 'std_rating', 'count_reviews']

    # Convert 'year_month' to a datetime (first day of the month) for sorting & continuous plotting
    grouped_sentiment['month_start'] = grouped_sentiment['year_month'].apply(
        lambda x: pd.Period(x, freq='M').start_time
    )
    grouped_sentiment.sort_values('month_start', inplace=True)

    grouped_rating['month_start'] = grouped_rating['year_month'].apply(
        lambda x: pd.Period(x, freq='M').start_time
    )
    grouped_rating.sort_values('month_start', inplace=True)

    # 1) Distribution of Sentiment (Histogram)
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df['sentiment'],
        nbinsx=20,
        marker=dict(color='royalblue'),
        name='Sentiment'
    ))
    fig_hist.update_layout(
        title="Distribution of Review Sentiment (Polarity)",
        xaxis_title="Sentiment Polarity",
        yaxis_title="Count",
        hovermode='x unified',
        template="plotly_white"
    )
    fig_hist.show()

    # 2) Average Sentiment Over Time (by month) + std shading + count in tooltip
    fig_line_sent = go.Figure()

    # Mean sentiment trace (main line)
    fig_line_sent.add_trace(go.Scatter(
        x=grouped_sentiment['month_start'],
        y=grouped_sentiment['avg_sentiment'],
        mode='lines+markers',
        name='Mean Sentiment',
        hovertemplate=(
            "Month: %{text}<br>"
            "Mean: %{y:.2f}<br>"
            "Std: %{customdata[0]:.2f}<br>"
            "Reviews: %{customdata[1]}<extra></extra>"
        ),
        text=grouped_sentiment['year_month'].astype(str),   # displayed as "YYYY-MM"
        customdata=grouped_sentiment[['std_sentiment', 'count_reviews']],
    ))

    # Upper band
    fig_line_sent.add_trace(go.Scatter(
        x=grouped_sentiment['month_start'],
        y=grouped_sentiment['avg_sentiment'] + grouped_sentiment['std_sentiment'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Lower band (with fill)
    fig_line_sent.add_trace(go.Scatter(
        x=grouped_sentiment['month_start'],
        y=grouped_sentiment['avg_sentiment'] - grouped_sentiment['std_sentiment'],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig_line_sent.update_layout(
        title="Average Sentiment Polarity Over Months (with Std Dev Shading)",
        xaxis_title="Month Start",
        yaxis=dict(title="Average Sentiment Polarity", range=[-1, 1]),
        hovermode='x unified',
        template="plotly_white"
    )
    fig_line_sent.show()

    # 3) Average Rating Over Time (by month) + std shading + count in tooltip
    fig_line_rat = go.Figure()

    # Mean rating trace (main line)
    fig_line_rat.add_trace(go.Scatter(
        x=grouped_rating['month_start'],
        y=grouped_rating['avg_rating'],
        mode='lines+markers',
        name='Mean Rating',
        hovertemplate=(
            "Month: %{text}<br>"
            "Mean: %{y:.2f}<br>"
            "Std: %{customdata[0]:.2f}<br>"
            "Reviews: %{customdata[1]}<extra></extra>"
        ),
        text=grouped_rating['year_month'].astype(str),
        customdata=grouped_rating[['std_rating', 'count_reviews']],
    ))

    # Upper band
    fig_line_rat.add_trace(go.Scatter(
        x=grouped_rating['month_start'],
        y=grouped_rating['avg_rating'] + grouped_rating['std_rating'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    # Lower band (with fill)
    fig_line_rat.add_trace(go.Scatter(
        x=grouped_rating['month_start'],
        y=grouped_rating['avg_rating'] - grouped_rating['std_rating'],
        fill='tonexty',
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig_line_rat.update_layout(
        title="Average Rating Over Months (with Std Dev Shading)",
        xaxis_title="Month Start",
        yaxis_title="Average Rating",
        hovermode='x unified',
        template="plotly_white"
    )
    fig_line_rat.show()

    # 4) Aspect-Based Sentiment (Bar Chart)
    fig_aspect = go.Figure()
    fig_aspect.add_trace(go.Bar(
        x=aspect_df['Aspect'],
        y=aspect_df['Average_Sentiment'],
        marker=dict(color='blue'),
        name='Aspect Sentiment'
    ))
    fig_aspect.update_layout(
        title="Aspect-Based Sentiment (Naive)",
        xaxis_title="Aspect",
        yaxis=dict(title="Average Sentiment", range=[-1, 1]),
        hovermode='x unified',
        template="plotly_white"
    )
    fig_aspect.show()

if __name__ == "__main__":
    main()