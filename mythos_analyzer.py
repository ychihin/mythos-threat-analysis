import os
import pandas as pd
import praw
import requests
import torch
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
from dotenv import load_dotenv

# Load credentials
load_dotenv()

class MythosAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # GPU Acceleration for Apple M1 Pro (MPS)
        device = "cpu"
        if torch.backends.mps.is_available():
            device = torch.device("mps")
            print("Using Apple Silicon GPU (MPS) for acceleration.")
        
        print("Loading NLP pipeline (this may take a minute)...")
        self.threat_classifier = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli", 
            device=device
        )
        
        self.victim_labels = ["Healthcare", "Critical Infrastructure", "Financial Institutions", "Individual Users", "SMEs", "Government Systems"]
        self.harm_labels = ["Ransomware", "Data Breach", "Autonomous Sabotage", "Zero-Day Exploitation", "Financial Fraud"]

    def _get_sentiment_label(self, score):
        if score >= 0.05: return "Positive (Hopeful/Defensive)"
        if score <= -0.05: return "Negative (Fearful/Threatening)"
        return "Neutral (Technical/Objective)"

    def plot_temporal_sentiment(self, df):
        """Generates a line chart showing sentiment change over time."""
        if len(df) < 2:
            print("Not enough data points for temporal plotting.")
            return

        # Prepare data
        df['date_only'] = df['date'].dt.date
        temporal_df = df.groupby('date_only')['sentiment_score'].mean().reset_index()
        
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=temporal_df, x='date_only', y='sentiment_score', marker='o', color='teal')
        plt.axhline(0, color='red', linestyle='--', alpha=0.5)
        plt.title("Sentiment Trend: Discussion on Autonomous AI Risks")
        plt.xlabel("Date")
        plt.ylabel("Avg Sentiment Score")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plot_filename = f"sentiment_trend_{datetime.now().strftime('%H%M')}.png"
        plt.savefig(plot_filename)
        print(f"Temporal analysis plot saved as: {plot_filename}")

    def scrape_hacker_news(self, queries, limit=50):
        """Scrapes HN for multiple queries (Stories + Comments)."""
        all_hits = []
        # We search for both stories (titles) and comments (discussions)
        tags = ['story', 'comment'] 
        
        for q in queries:
            for tag in tags:
                print(f"Scraping Hacker News for '{q}' [Tag: {tag}]...")
                url = f"https://hn.algolia.com/api/v1/search?query={q}&tags={tag}&hitsPerPage={limit}"
                try:
                    response = requests.get(url, timeout=10)
                    hits = response.json().get('hits', [])
                    for hit in hits:
                        # Extract text based on the result type
                        if tag == 'story':
                            text = f"{hit.get('title', '')} {hit.get('story_text', '')}"
                        else:
                            # Algolia stores comment text in 'comment_text'
                            text = hit.get('comment_text', '')
                        
                        if text:
                            # Remove HTML tags often found in HN comments
                            clean_text = text.replace('<p>', '\n').replace('</p>', '').replace('<i>', '').replace('</i>', '')
                            all_hits.append(self._process_text(clean_text, hit.get('created_at_i'), "HackerNews", tag))
                except Exception as e:
                    print(f"HN Scrape failed for {q} ({tag}): {e}")
        
        df = pd.DataFrame(all_hits)
        if not df.empty:
            df = df.drop_duplicates(subset=['text'])
        return df

    def _init_reddit(self):
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        if not client_id or client_id == "your_client_id_here":
            raise ValueError("Missing Reddit API credentials.")
        return praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent="mythos-analyzer")

    def scrape_reddit(self, query, subreddits, limit=50):
        reddit = self._init_reddit()
        data = []
        for sub_name in subreddits:
            print(f"Scraping r/{sub_name} for '{query}'...")
            subreddit = reddit.subreddit(sub_name)
            for submission in subreddit.search(query, limit=limit):
                data.append(self._process_text(submission.title + " " + submission.selftext, submission.created_utc, sub_name, "post"))
        return pd.DataFrame(data)

    def _process_text(self, text, timestamp, subreddit, type):
        return {
            "text": text,
            "date": datetime.utcfromtimestamp(timestamp),
            "subreddit": subreddit,
            "type": type
        }

    def analyze_data(self, df):
        print(f"Analyzing {len(df)} entries...")
        df['sentiment_score'] = df['text'].apply(lambda x: self.sentiment_analyzer.polarity_scores(x)['compound'])
        df['sentiment_label'] = df['sentiment_score'].apply(self._get_sentiment_label)
        
        def extract_tags(text):
            v_res = self.threat_classifier(text[:512], candidate_labels=self.victim_labels)
            h_res = self.threat_classifier(text[:512], candidate_labels=self.harm_labels)
            return v_res['labels'][0], h_res['labels'][0]

        df[['predicted_victim', 'predicted_harm']] = df['text'].apply(lambda x: pd.Series(extract_tags(x)))
        return df

    def export_results(self, df):
        filename = f"mythos_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df.to_csv(filename, index=False)
        return filename

    def get_mock_data(self):
        """Mock data spanning the 'leak' period of April 2026."""
        print("Generating time-series mock data (April - May 2026)...")
        dates = [datetime(2026, 4, 15), datetime(2026, 4, 21), datetime(2026, 4, 22), 
                 datetime(2026, 4, 25), datetime(2026, 5, 1), datetime(2026, 5, 4)]
        texts = [
            "Mozilla audit fixes 271 bugs. Good AI use.",
            "DISCORD LEAK: Mythos weights are public. This is a disaster.",
            "Panic on sysadmin forums after Mythos leak. Every server is at risk.",
            "Cybercriminals steal $12M using new autonomous agents. Arms race starts.",
            "Proposed EU regulation for Mythos-level models after infrastructure scares.",
            "Final assessment: Mythos automation makes hospital grids highly vulnerable."
        ]
        mock_data = []
        for d, t in zip(dates, texts):
            mock_data.append({"text": t, "date": d, "subreddit": "Mock", "type": "post"})
        return pd.DataFrame(mock_data)

if __name__ == "__main__":
    analyzer = MythosAnalyzer()
    
    # Broadening queries based on Google Trends logic for AI security
    queries = [
        "Anthropic Mythos", 
        "Project Glasswing", 
        "autonomous AI zero-day", 
        "AI cyber attack infrastructure",
        "LLM hacking automation",
        "Mythos",
        "Anthropic's Mythos",
        "Claude Mythos"
    ]
    
    # 1. Scrape HN
    hn_df = analyzer.scrape_hacker_news(queries, limit=50)
    
    # 2. Try Reddit
    reddit_df = pd.DataFrame()
    try:
        reddit_df = analyzer.scrape_reddit("AI cybersecurity", ["netsec", "cybersecurity"], limit=20)
    except:
        pass

    # 3. Merge
    all_data = pd.concat([hn_df, reddit_df], ignore_index=True)
    if all_data.empty:
        all_data = analyzer.get_mock_data()

    # 4. Analyze & Plot
    final_df = analyzer.analyze_data(all_data)
    analyzer.export_results(final_df)
    analyzer.plot_temporal_sentiment(final_df)
    
    print("\n--- PRELIMINARY INSIGHTS ---")
    print(f"Avg Sentiment Score: {final_df['sentiment_score'].mean():.2f}")
    
    print("\nTop Predicted Victims (Ranked):")
    print(final_df['predicted_victim'].value_counts())
    
    print("\nTop Predicted Harms (Ranked):")
    print(final_df['predicted_harm'].value_counts())

    print("\n--- TEMPORAL TREND DATA ---")
    print(final_df.groupby('date_only')['sentiment_score'].mean())
