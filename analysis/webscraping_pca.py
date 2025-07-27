import os
import sys
import json
import re
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

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
    # keep alphabets/spaces, then lowercase
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = text.lower().strip()
    return text

def main():
    chosen_file = choose_json_file()
    with open(chosen_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # capture 'review' column exists
    if 'review' not in df.columns:
        df['review'] = ""

    # preprocess "review" text
    df['clean_text'] = df['review'].apply(preprocess_text)

    # calc sentiment polarity for each processed review
    df['sentiment'] = df['clean_text'].apply(lambda x: TextBlob(x).sentiment.polarity)

    # vectorize text with TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', min_df=2)
    X = vectorizer.fit_transform(df['clean_text'])

    # reduce dimensionality with pca
    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X.toarray())
    df['pc1'] = X_pca[:, 0]
    df['pc2'] = X_pca[:, 1]

    # k-means clustering
    n_clusters = 5  # Adjust as needed
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X)

    # print top words in each cluster
    print(f"\nAnalyzing file: {chosen_file}")
    print(f"Top words per cluster (K={n_clusters}):\n")
    cluster_centers = kmeans.cluster_centers_
    order_centroids = cluster_centers.argsort()[:, ::-1]  # sort each row descending
    terms = vectorizer.get_feature_names_out()
    for i in range(n_clusters):
        top_features = [terms[ind] for ind in order_centroids[i, :10]]
        print(f"Cluster {i}: {', '.join(top_features)}")

    # interactive plotly plot
    # hover will show partial text i.e. clean_text and sentiment.
    # change clean_text to review if raw text is needed
    fig = px.scatter(
        df,
        x="pc1",
        y="pc2",
        color="cluster",
        hover_data={
            "pc1": ":.2f",
            "pc2": ":.2f",
            "cluster": True,
            "sentiment": True,
            "clean_text": True
        },
        title="cluster viz of reviews (sentiment incl)"
    )
    fig.show()

if __name__ == "__main__":
    main()