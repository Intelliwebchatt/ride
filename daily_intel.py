 import json
import datetime
import yfinance as yf
import feedparser
import requests

# --- CONFIGURATION ---
# PASTE YOUR TOP 20 SEARCHES HERE
RAW_TRENDING_LIST = """
peter greene
barcelona - osasuna
timberwolves vs warriors
heisman trophy
winter storm warning
shane's new app
bitcoin price
alabama football
markets today
weather montgomery
samsung galaxy s25
taylor swift tour
spacex launch
gta 6 news
interest rates
election results
ai regulation
nvidia stock
cyber truck
crypto regulation
"""

# --- 1. GET MARKETS (Finance) ---
def get_markets():
    print("...Fetching Market Data...")
    tickers = {
        "S&P 500": "^GSPC",
        "Bitcoin": "BTC-USD",
        "NVIDIA": "NVDA"
    }
    market_data = []
    
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change_pct = ((current - prev) / prev) * 100
                
                sign = "+" if change_pct >= 0 else ""
                price_str = f"{current:,.2f}" if current < 1000 else f"{current:,.0f}"
                
                market_data.append({
                    "name": name,
                    "price": price_str,
                    "change": f"{sign}{change_pct:.1f}%"
                })
        except Exception as e:
            print(f"Error fetching {name}: {e}")
            market_data.append({"name": name, "price": "Error", "change": "0%"})
            
    return market_data

# --- 2. GET TOP 5 NEWS (RSS) ---
def get_news_batch():
    print("...Fetching Top 5 News Stories...")
    news_list = []
    try:
        rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
        # Get top 5
        for entry in feed.entries[:5]:
            news_list.append({
                "headline": entry.title,
                "link": entry.link,
                "source": entry.source.title if 'source' in entry else "Google News"
            })
    except Exception as e:
        print(f"Error fetching news: {e}")
        news_list.append({"headline": "News Unavailable", "link": "#", "source": "System"})
    
    return news_list

# --- 3. GET TOP 10 PREDICTIONS (Polymarket API) ---
def get_polymarket_batch():
    print("...Fetching Top 10 Predictions...")
    predictions = []
    try:
        # Fetch top 10 by volume
        url = "https://gamma-api.polymarket.com/events?limit=10&sort=volume&order=desc"
        response = requests.get(url).json()
        
        for event in response:
            try:
                title = event['title']
                markets = event.get('markets', [])
                main_market = markets[0] if markets else None
                
                if main_market:
                    import ast
                    outcomes = ast.literal_eval(main_market['outcomePrices'])
                    yes_price = float(outcomes[0]) * 100
                    
                    predictions.append({
                        "question": title,
                        "odds": f"{yes_price:.0f}",
                        "id": event['id']
                    })
            except:
                continue
    except Exception as e:
        print(f"Error fetching Polymarket: {e}")
        
    return predictions

# --- 4. PROCESS TRENDING LIST ---
def process_trending(raw_text):
    print("...Processing Trending List...")
    lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
    processed = []
    # Take only top 20 if list is longer
    for i, keyword in enumerate(lines[:20]): 
        processed.append({
            "keyword": keyword
        })
    return processed

# --- MAIN EXECUTION ---
def main():
    final_data = {
        "meta": {
            "uploadedAt": datetime.datetime.now().strftime("%b %d, %I:%M %p")
        },
        "markets": get_markets(),
        "news": get_news_batch(),         # Now returns 5 items
        "predictions": get_polymarket_batch(), # Now returns 10 items
        "trending": process_trending(RAW_TRENDING_LIST)
    }
    
    with open("data.json", "w") as f:
        json.dump(final_data, f, indent=2)
        
    print("\nSUCCESS! Updated data.json with:")
    print(f"- {len(final_data['markets'])} Market Tickers")
    print(f"- {len(final_data['news'])} News Stories")
    print(f"- {len(final_data['predictions'])} Predictions")
    print(f"- {len(final_data['trending'])} Trending Searches")

if __name__ == "__main__":
    main()
