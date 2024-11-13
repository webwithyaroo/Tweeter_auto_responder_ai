import tweepy
import openai
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI API setup
openai.api_key = OPENAI_API_KEY

# Tweepy setup
auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
api = tweepy.API(auth)

def generate_responses(context):
    """Generate AI responses using OpenAI."""
    prompt = f"Generate 3 relevant responses for this tweet: {context}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150,
        n=3,
        stop=None
    )
    return [choice["text"].strip() for choice in response.choices]

def process_tweets():
    """Monitor tweets and reply to #reply comments."""
    for tweet in tweepy.Cursor(api.search_tweets, q="#reply", lang="en").items():
        try:
            print(f"Processing tweet by {tweet.user.screen_name}: {tweet.text}")
            responses = generate_responses(tweet.text)

            reply_text = "\n".join([f"Option {i+1}: {resp}" for i, resp in enumerate(responses)])
            api.update_status(
                status=f"@{tweet.user.screen_name} Here are some responses:\n{reply_text}",
                in_reply_to_status_id=tweet.id
            )
            print(f"Replied to {tweet.user.screen_name}")
            time.sleep(5)  # Avoid rate limit violations
        except tweepy.TweepError as e:
            print(f"Tweepy error: {e}")
        except Exception as e:
            print(f"General error: {e}")

if __name__ == "__main__":
    while True:
        process_tweets()
        time.sleep(60)  # Check every minute
