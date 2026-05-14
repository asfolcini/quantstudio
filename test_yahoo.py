#!/usr/bin/env python3
"""
Script per testare i feed Yahoo RSS.
"""

import requests
import feedparser

def test_yahoo_feed(url: str):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ {url}: HTTP {response.status_code}")
            return
        
        feed = feedparser.parse(response.content)
        if feed.bozo:
            print(f"❌ {url}: Feed non valido")
            return
        
        print(f"✅ {url}: OK - {len(feed.entries)} articoli trovati")
    except Exception as e:
        print(f"❌ {url}: Errore - {e}")

if __name__ == "__main__":
    print("Test Yahoo RSS:")
    test_yahoo_feed("https://news.yahoo.com/rss/eu")
    test_yahoo_feed("https://news.yahoo.com/rss/us")
