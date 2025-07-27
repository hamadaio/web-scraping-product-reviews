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
        print("no JSON files found in the current dir")
        sys.exit(1)
    print("JSON files in the current directory:")
    for i, f in enumerate(files, start=1):
        print(f"{i}. {f}")
    while True:
        choice = input(f"enter the number of the file you want to analyze (1-{len(files)}): ")
        try:
            idx = int(choice)
            if 1 <= idx <= len(files):
                return files[idx - 1]
        except ValueError:
            pass
        print("invalid choice; enter a valid number")

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

    if 'review' not in df.columns:
        df['review'] = ""
    if 'rating' not in df.columns:
        df['rating'] = None
    if 'date' not in df.columns:
        df['date'] = None

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['clean_text'] = df['review'].apply(preprocess_text)
    df['sentiment'] = df['clean_text'].apply(lambda x: TextBlob(x).sentiment.polarity)

    print(f"Analyzing file: {chosen_file}")
    avg_rating = df['rating'].mean(skipna=True)
    avg_sentiment = df['sentiment'].mean(skipna=True)
    print("Average Rating:", f"{avg_rating:.2f}" if pd.notna(avg_rating) else "N/A")
    print("Average Sentiment (Polarity):", f"{avg_sentiment:.2f}" if pd.notna(avg_sentiment) else "N/A")

    # aspect based sentiment
    aspect_df = aspect_based_sentiment(df)
    print("\nAspect-Based Sentiment (Naive Approach):")
    print(aspect_df)

    # sonv to quarterly periods
    df['year_quarter'] = df['date'].dt.to_period('Q')

    # average sentiment over Time
    grouped_sentiment = (df.dropna(subset=['year_quarter'])
                         .groupby('year_quarter')['sentiment']
                         .mean()
                         .reset_index())
    grouped_sentiment['year_quarter'] = grouped_sentiment['year_quarter'].astype(str)

    # average rating
    grouped_rating = (df.dropna(subset=['year_quarter', 'rating'])
                      .groupby('year_quarter')['rating']
                      .mean()
                      .reset_index())
    grouped_rating['year_quarter'] = grouped_rating['year_quarter'].astype(str)

    # dist of Sentiment
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df['sentiment'],
        nbinsx=20,
        marker=dict(color='royalblue'),
        name='Sentiment'
    ))
    fig_hist.update_layout(
        title="dist of review sentiment — polarity",
        xaxis_title="sentiment polarity",
        yaxis_title="count",
        hovermode='x unified',  # or 'closest' if you prefer one-bar hover
        template="plotly_white"
    )
    fig_hist.show()

    # average sentiment
    fig_line_sent = go.Figure()
    fig_line_sent.add_trace(go.Scatter(
        x=grouped_sentiment['year_quarter'],
        y=grouped_sentiment['sentiment'],
        mode='lines+markers',
        name='Avg Sentiment',
        line=dict(color='blue'),
        marker=dict(symbol='circle')
    ))
    fig_line_sent.update_layout(
        title="average sentiment polarity",
        xaxis_title="year-quarter",
        yaxis=dict(title="average sentiment polarity", range=[-1, 1]),
        hovermode='x unified',
        template="plotly_white"
    )
    fig_line_sent.show()

    # average rating
    fig_line_rat = go.Figure()
    fig_line_rat.add_trace(go.Scatter(
        x=grouped_rating['year_quarter'],
        y=grouped_rating['rating'],
        mode='lines+markers',
        name='Avg Rating',
        line=dict(color='blue'),
        marker=dict(symbol='circle')
    ))
    fig_line_rat.update_layout(
        title="average rating",
        xaxis_title="year quarter",
        yaxis_title="average rating",
        hovermode='x unified',
        template="plotly_white"
    )
    fig_line_rat.show()

    # aspect based sentiment
    fig_aspect = go.Figure()
    fig_aspect.add_trace(go.Bar(
        x=aspect_df['Aspect'],
        y=aspect_df['Average_Sentiment'],
        marker=dict(color='blue'),
        name='Aspect Sentiment'
    ))
    fig_aspect.update_layout(
        title="ABS (naive)",
        xaxis_title="aspect",
        yaxis=dict(title="average sentiment", range=[-1, 1]),
        hovermode='x unified',
        template="plotly_white"
    )
    fig_aspect.show()

if __name__ == "__main__":
    main()