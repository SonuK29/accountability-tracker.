import feedparser
import datetime
import re
import os
import pandas as pd

# 1. Expanded Configuration (The "Media Diet")
RSS_FEEDS = [
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://feeds.feedburner.com/ndtvnews-india-news",
    "https://www.newslaundry.com/feed", # Investigative
    "https://aajtak.intoday.in/rss/topstories.xml", # Hindi Grassroots
    "http://feeds.reuters.com/reuters/INtopNews" # Objective/Formal
]

# 2. Bilingual & Tone-Adapted Keyword Dictionary
KEYWORDS = {
    "Pothole / Road Hazard": [
        "pothole", "bad road", "civic apathy", # General/Investigative
        "infrastructure collapse", # Reuters style
        "गड्ढा", "सड़क हादसा", "खराब सड़क" # Aaj Tak style
    ],
    "Healthcare Scarcity": [
        "hospital oxygen", "doctor shortage", "no bed", "medical negligence", "medicine scarcity", "medicine shortage",
        "healthcare crisis", # Reuters style
        "अस्पताल", "ऑक्सीजन की कमी", "इलाज नहीं" # Aaj Tak style
    ],
    "Infrastructure Failure": [
        "bridge collapse", "roof collapse", "building collapse", "civic failure",
        "structural failure", # Reuters style
        "पुल गिरा", "छत गिरी", "इमारत गिरी" # Aaj Tak style
    ],
    "VIP Movement Apathy": [
        "vip movement", "ambulance delayed vip", "traffic halted vip",
        "VIP काफिला", "एंबुलेंस फंसी" # Aaj Tak style
    ],
    "Water/Food Contamination": [
        "food poisoning", "contaminated water", "mid-day meal tragedy",
        "public health hazard", # Reuters style
        "जहरीला खाना", "गंदा पानी", "फूड पॉइजनिंग" # Aaj Tak style
    ]
}

CSV_FILE = "data.csv"

# 3. Upgraded Bilingual Extraction Logic
def fetch_and_parse():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    new_records = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.title.lower()
                
                for category, words in KEYWORDS.items():
                    # We check if any of our English or Hindi words are in the headline
                    if any(word in title for word in words):
                        
                        casualties = 1 
                        
                        # Upgraded Regex: Looks for numbers near English OR Hindi death terms
                        # \d+ finds the number. The rest looks for "dead", "killed", "की मौत" (deaths), "मारे गए" (were killed)
                        match = re.search(r'(\d+)\s*(dead|killed|die|crushed|lives lost|की मौत|मारे गए|शव)', title)
                        if match:
                            casualties = int(match.group(1))

                        new_records.append({
                            "Date": today_str,
                            "Category": category,
                            "Location": "India", 
                            "Casualties": casualties,
                            "Headline": entry.title, # Will save Hindi text perfectly
                            "Source_URL": entry.link
                        })
                        break 
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
