import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os

class SampleDataGenerator:
    """
    Generate sample review data for testing the dashboard.
    """
    
    def __init__(self):
        self.positive_reviews = [
            "Amazing product! Really helps with meditation and focus.",
            "Great app, very user-friendly interface. Highly recommend!",
            "Excellent customer service and fast shipping.",
            "Love the comfort and build quality. Worth every penny!",
            "The battery life is impressive and the device is very reliable.",
            "Perfect for daily meditation practice. Seeing real improvements!",
            "The app is intuitive and the data insights are valuable.",
            "Comfortable to wear and easy to use. Great investment!",
            "Outstanding performance and very accurate readings.",
            "Fantastic product that actually works as advertised."
        ]
        
        self.neutral_reviews = [
            "It's okay, does what it's supposed to do.",
            "Average product, nothing special but works fine.",
            "Decent app but could use some improvements.",
            "The device is alright, meets basic expectations.",
            "Works as expected, nothing more nothing less.",
            "It's fine for the price point.",
            "Does the job but room for improvement.",
            "Adequate performance, could be better.",
            "Standard quality, meets minimum requirements.",
            "Fair product, gets the basics right."
        ]
        
        self.negative_reviews = [
            "Terrible app, constantly crashes and bugs everywhere.",
            "Waste of money, doesn't work as advertised.",
            "Poor customer service, no response to my complaints.",
            "Uncomfortable to wear, cheap build quality.",
            "Battery dies too quickly, very disappointed.",
            "The app is confusing and difficult to navigate.",
            "Overpriced for what you get, not worth it.",
            "Many technical issues, very frustrating experience.",
            "Product broke after just a few weeks of use.",
            "Completely useless, total disappointment."
        ]
        
        self.authors = [
            "John D.", "Sarah M.", "Mike R.", "Emily S.", "David L.",
            "Lisa K.", "Tom W.", "Anna B.", "Chris P.", "Jessica T.",
            "Mark H.", "Rachel C.", "Alex J.", "Nicole V.", "Ryan F."
        ]
    
    def generate_google_play_reviews(self, count: int = 50) -> List[Dict]:
        """Generate sample Google Play reviews."""
        reviews = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(count):
            sentiment_type = random.choice(['positive', 'neutral', 'negative'])
            
            if sentiment_type == 'positive':
                review_text = random.choice(self.positive_reviews)
                rating = random.choice([4, 5])
            elif sentiment_type == 'neutral':
                review_text = random.choice(self.neutral_reviews)
                rating = 3
            else:
                review_text = random.choice(self.negative_reviews)
                rating = random.choice([1, 2])
            
            review_date = base_date + timedelta(days=random.randint(0, 365))
            
            reviews.append({
                'id': f"gp_{i+1}",
                'author': random.choice(self.authors),
                'rating': rating,
                'review': review_text,
                'date': review_date.strftime('%Y-%m-%d'),
                'helpful': random.randint(0, 20),
                'platform': 'google_play'
            })
        
        return reviews
    
    def generate_app_store_reviews(self, count: int = 50) -> List[Dict]:
        """Generate sample App Store reviews."""
        reviews = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(count):
            sentiment_type = random.choice(['positive', 'neutral', 'negative'])
            
            if sentiment_type == 'positive':
                review_text = random.choice(self.positive_reviews)
                rating = random.choice([4, 5])
            elif sentiment_type == 'neutral':
                review_text = random.choice(self.neutral_reviews)
                rating = 3
            else:
                review_text = random.choice(self.negative_reviews)
                rating = random.choice([1, 2])
            
            review_date = base_date + timedelta(days=random.randint(0, 365))
            
            reviews.append({
                'id': f"as_{i+1}",
                'author': random.choice(self.authors),
                'rating': rating,
                'review': review_text,
                'date': review_date.strftime('%Y-%m-%d'),
                'helpful': random.randint(0, 15),
                'platform': 'app_store'
            })
        
        return reviews
    
    def generate_trustpilot_reviews(self, count: int = 50) -> List[Dict]:
        """Generate sample Trustpilot reviews."""
        reviews = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(count):
            sentiment_type = random.choice(['positive', 'neutral', 'negative'])
            
            if sentiment_type == 'positive':
                review_text = random.choice(self.positive_reviews)
                rating = random.choice([4, 5])
            elif sentiment_type == 'neutral':
                review_text = random.choice(self.neutral_reviews)
                rating = 3
            else:
                review_text = random.choice(self.negative_reviews)
                rating = random.choice([1, 2])
            
            review_date = base_date + timedelta(days=random.randint(0, 365))
            
            reviews.append({
                'id': f"tp_{i+1}",
                'author': random.choice(self.authors),
                'rating': rating,
                'review': review_text,
                'date': review_date.strftime('%Y-%m-%d'),
                'helpful': random.randint(0, 25),
                'platform': 'trustpilot'
            })
        
        return reviews
    
    def save_sample_data(self, data_dir: str = "../data"):
        """Save sample data to JSON files."""
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate and save Google Play reviews
        google_reviews = self.generate_google_play_reviews(100)
        with open(f"{data_dir}/google_play_reviews.json", 'w', encoding='utf-8') as f:
            json.dump(google_reviews, f, indent=2, ensure_ascii=False)
        
        # Generate and save App Store reviews
        app_store_reviews = self.generate_app_store_reviews(80)
        with open(f"{data_dir}/app_store_reviews.json", 'w', encoding='utf-8') as f:
            json.dump(app_store_reviews, f, indent=2, ensure_ascii=False)
        
        # Generate and save Trustpilot reviews
        trustpilot_reviews = self.generate_trustpilot_reviews(120)
        with open(f"{data_dir}/trustpilot_reviews.json", 'w', encoding='utf-8') as f:
            json.dump(trustpilot_reviews, f, indent=2, ensure_ascii=False)
        
        print(f"Sample data saved to {data_dir}/")
        print(f"- Google Play: {len(google_reviews)} reviews")
        print(f"- App Store: {len(app_store_reviews)} reviews")
        print(f"- Trustpilot: {len(trustpilot_reviews)} reviews")

if __name__ == "__main__":
    generator = SampleDataGenerator()
    generator.save_sample_data()
