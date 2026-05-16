import feedparser
import datetime
import re
import os
import pandas as pd

# 1. Configuration
RSS_FEEDS = [
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://feeds.feedburner.com/ndtvnews-india-news"
]

KEYWORDS = {
    "Pothole Accident": ["pothole", "bad road"],
    "Healthcare Scarcity": ["hospital oxygen", "doctor shortage", "no bed"],
    "Infrastructure Failure": ["bridge collapse", "roof collapse"],
    "VIP Movement": ["vip movement", "ambulance delayed vip"]
}

CSV_FILE = "data.csv"

# 2. The Extraction Logic
def fetch_and_parse():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    new_records = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.title.lower()
                
                for category, words in KEYWORDS.items():
                    if any(word in title for word in words):
                        # Simple logic: assume 1 casualty unless a number is mentioned near 'dead'
                        casualties = 1 
                        match = re.search(r'(\d+)\s*(dead|killed|die|crushed|lives lost)', title)
                        if match:
                            casualties = int(match.group(1))

                        new_records.append({
                            "Date": today_str,
                            "Category": category,
                            "Location": "India", # Placeholder for manual or future AI extraction
                            "Casualties": casualties,
                            "Headline": entry.title,
                            "Source_URL": entry.link
                        })
                        break # Stop checking other categories if one matches
        except Exception as e:
            print(f"Failed to parse {feed_url}: {e}")

    return new_records

# 3. Saving the Data
def update_csv():
    new_data = fetch_and_parse()
    if not new_data:
        print("No systemic failure news found today.")
        return

    new_df = pd.DataFrame(new_data)

    # If database exists, merge and prevent duplicates based on the Headline
    if os.path.exists(CSV_FILE):
        existing_df = pd.read_csv(CSV_FILE)
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=["Headline"])
    else:
        combined_df = new_df

    combined_df.to_csv(CSV_FILE, index=False)
    print(f"Database updated successfully! Total records: {len(combined_df)}")

if __name__ == "__main__":
    update_csv()