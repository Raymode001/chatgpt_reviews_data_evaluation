import pandas as pd
import time
from google_play_scraper import reviews, Sort

# --- 1. Configuration ---
APP_ID = 'com.openai.chatgpt'
# Use the known total number of reviews to calculate the interval
TOTAL_REVIEWS = 22687654
SAMPLE_SIZE = 10000

# Calculate the interval to get the desired sample size
INTERVAL = TOTAL_REVIEWS // SAMPLE_SIZE

# --- 2. Initialization ---
sample_reviews = []
review_count = 0
continuation_token = None # Used to get the next page of reviews
errors = 0

print(f"Starting scrape. Will sample 1 review every {INTERVAL} reviews.")

# --- 3. Main Scraping Loop ---
while len(sample_reviews) < SAMPLE_SIZE:
    try:
        # Fetch a batch of reviews
        result, continuation_token = reviews(
            APP_ID,
            lang='en',
            country='us',
            sort=Sort.NEWEST,
            count=200,  # Fetch in batches of 200
            continuation_token=continuation_token
        )

        # If no more reviews are returned, or the token is gone, stop.
        if not result or not continuation_token:
            print("Reached the end of the reviews.")
            break

        # Loop through the batch, but only save reviews at the interval
        for review in result:
            if review_count % INTERVAL == 0:
                sample_reviews.append(review)
                # Print progress
                print(f"Processed: {review_count}, Samples Found: {len(sample_reviews)}")
                # Stop once we have enough samples
                if len(sample_reviews) >= SAMPLE_SIZE:
                    break
            review_count += 1
        
        # Be respectful to Google's servers
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        errors += 1
        if errors > 10:
            print("Too many consecutive errors. Stopping.")
            break
        time.sleep(5) # Wait longer after an error

# --- 4. Final Result ---
print("\nScraping complete.")
df_sample = pd.DataFrame(sample_reviews)

print(f"Final Sample Size: {len(df_sample)}")
print("--- Sample DataFrame Head ---")
print(df_sample.head())