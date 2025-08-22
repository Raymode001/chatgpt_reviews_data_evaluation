import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import pandas as pd

# It's good practice to ensure the NLTK data is downloaded.
# A user of your script might not have it.
try:
    stopwords.words('english')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

def preprocess_for_lda(df_column):
    """
    Cleans and tokenizes text data for topic modeling.
    - Converts to lowercase
    - Removes punctuation and numbers
    - Tokenizes text
    - Removes stopwords (including custom ones)
    - Lemmatizes words
    - Removes short words
    """
    corpus = []
    lem = WordNetLemmatizer()

    # Define English stopwords and add custom, context-specific words
    stop_words = set(stopwords.words('english'))
    custom_stopwords = {'app', 'chatgpt', 'gpt', 'chat', 'use', 'im', 'ive', 'also','bad','worse','worst','cant','even','say','doesnt','dont','give','thing','things','good','better','best','great','nice','day','working','work','want','get','need','make'}
    stop_words.update(custom_stopwords)

    for text in df_column:
        if not isinstance(text, str):
            continue

        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        words = word_tokenize(text)
        
        #Use a clear loop to lemmatize first ---
        lemmatized_words = []
        for w in words:
            # 1. Lemmatize the word first
            lem_word = lem.lemmatize(w)
            
            # 2. Then, check the lemmatized word against stopwords and length
            if lem_word not in stop_words and len(lem_word) > 2:
                lemmatized_words.append(lem_word)

        corpus.append(lemmatized_words)
        
    return corpus

# update feedback lookup fuction:


def analyze_version_by_topic(version_string, topic_name, keyword_groups, negative_english_reviews, all_update_dates):
    """
    Analyzes negative feedback for a specific app version and a specific topic.
    """
    print("="*60)
    print(f"Detailed look for Version: {version_string} | Topic: {topic_name}")
    print("="*60)

    # --- 1. Find the active date range for this version ---
    try:
        start_date = all_update_dates[version_string]
        next_updates = all_update_dates[all_update_dates > start_date]
        end_date = next_updates.iloc[0] if not next_updates.empty else pd.Timestamp.now()
    except KeyError:
        print(f"Error: Version '{version_string}' not found in the update list.")
        return

    print(f"Analyzing reviews from {start_date.date()} to {end_date.date()}...")

    # --- 2. Filter for negative reviews in that window ---
    negative_version_reviews = negative_english_reviews[
        (negative_english_reviews['at'] >= start_date) & 
        (negative_english_reviews['at'] < end_date)
    ]
    #negative_version_reviews = version_reviews[version_reviews['score'] <= 2]

    if negative_version_reviews.empty:
        print("No negative reviews found for this version.")
        return

    # --- 3. KEY CHANGE: Filter those negative reviews by topic keywords ---
    try:
        keywords = keyword_groups[topic_name]
        pattern = '|'.join(keywords)
        topic_specific_complaints = negative_version_reviews[
            negative_version_reviews['content'].str.contains(pattern, case=False, na=False)
        ]
    except KeyError:
        print(f"Error: Topic '{topic_name}' not found in keyword_groups.")
        return

    if topic_specific_complaints.empty:
        print(f"Found {len(negative_version_reviews)} negative reviews, but none matched the '{topic_name}' keywords.")
        return

    print(f"\nFound {len(topic_specific_complaints)} negative reviews matching the '{topic_name}' topic.")
    
    # --- 4. Show example reviews ---
    print("\n--- Example Complaints for this Topic and Version: ---")
    for index, row in topic_specific_complaints.head(5).iterrows():
        print(f"Date: {row['at'].strftime('%Y-%m-%d')}")
        print(f"Review: {row['content']}")
        print("-" * 60) # Adds a separator for readability