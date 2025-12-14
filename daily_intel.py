 import json
import datetime
import yfinance as yf
import feedparser
import requests
import ast

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

# --- 2. GET TOP 5 NEWS (Google News RSS) ---
def get_news_batch():
    print("...Fetching Top 5 News Stories...")
    news_list = []
    try:
        rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        
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

# --- 3. GET TOP 10 PREDICTIONS (Polymarket API - ROBUST MODE) ---
def get_polymarket_batch():
    print("...Fetching Top 10 Predictions...")
    predictions = []
    try:
        # Added a User-Agent so we look like a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = "https://gamma-api.polymarket.com/events?limit=20&sort=volume&order=desc"
        response = requests.get(url, headers=headers).json()
        
        for event in response:
            if len(predictions) >= 10: break # Stop once we have 10 good ones
            
            try:
                title = event.get('title', 'Unknown Prediction')
                markets = event.get('markets', [])
                main_market = markets[0] if markets else None
                
                if main_market:
                    # Robust parsing for outcomePrices
                    raw_outcomes = main_market.get('outcomePrices', '["0", "0"]')
                    
                    # If it's a string (common), decode it. If it's already a list, use it.
                    if isinstance(raw_outcomes, str):
                        outcomes = ast.literal_eval(raw_outcomes)
                    else:
                        outcomes = raw_outcomes
                        
                    # Calculate percentage
                    yes_price = float(outcomes[0]) * 100
                    
                    predictions.append({
                        "question": title,
                        "odds": f"{yes_price:.0f}",
                        "id": event.get('id', '')
                    })
            except Exception as inner_e:
                # If one fails, just skip it and try the next one
                print(f"Skipped bad item: {inner_e}")
                continue
                
    except Exception as e:
        print(f"Error fetching Polymarket: {e}")
        
    # Fallback if empty
    if not predictions:
        predictions.append({"question": "Data Unavailable", "odds": "0", "id": "0"})
        
    return predictions

# --- 4. GET REAL GOOGLE TRENDS (RSS Feed) ---
def get_google_trends():
    print("...Fetching Real-Time Google Trends...")
    trends = []
    try:
        rss_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:20]:
            trends.append({
                "keyword": entry.title
            })
            
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")
        trends = [{"keyword": "Check Logs"}, {"keyword": "Manual Mode"}]
        
    return trends

# --- MAIN EXECUTION ---
def main():
    final_data = {
        "meta": {
            "uploadedAt": datetime.datetime.now().strftime("%b %d, %I:%M %p")
        },
        "markets": get_markets(),
        "news": get_news_batch(),         
        "predictions": get_polymarket_batch(), 
        "trending": get_google_trends() 
    }
    
    with open("data.json", "w") as f:
        json.dump(final_data, f, indent=2)
        
    print("\nSUCCESS! Dashboard Updated Successfully.")
    print(f"- Fetched {len(final_data['predictions'])} Predictions")

if __name__ == "__main__":
    main()
