import os
import requests, pandas as pd, io
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

API_KEY = os.environ.get("API_KEY")  # fetch API key from Render

def scrape_amazon(query, limit=12):
    url = f"https://www.amazon.in/s?k={query.replace(' ','+')}"
    # Send request via ScraperAPI
    api_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={url}"
    resp = requests.get(api_url, headers=HEADERS, timeout=15)
    
    soup = BeautifulSoup(resp.content, "html.parser")
    results = soup.find_all("div", {"data-component-type": "s-search-result"})
    
    rows = []
    for r in results[:limit]:
        h2 = r.find("h2")
        if not h2:
            continue
        title = h2.text.strip()
        a_tag = h2.find("a")
        href = a_tag["href"] if a_tag else ""
        # Fix: ensure full product link
        link = "https://www.amazon.in" + href if href else ""
        
        price_whole = r.find("span", class_="a-price-whole")
        price_frac = r.find("span", class_="a-price-fraction")
        price = ""
        if price_whole:
            price = price_whole.text.strip() + (("." + price_frac.text.strip()) if price_frac else "")
        
        rating_tag = r.find("span", class_="a-icon-alt")
        rating = rating_tag.text.strip() if rating_tag else ""
        
        review_tag = r.select_one("span.a-size-base")
        reviews = review_tag.text.strip() if review_tag else ""
        
        rows.append({"title": title, "price": price, "rating": rating, "reviews": reviews, "link": link})
    
    return pd.DataFrame(rows)
