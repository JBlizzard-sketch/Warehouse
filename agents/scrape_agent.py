import requests
from bs4 import BeautifulSoup
import json
import random
from fake_useragent import UserAgent
from .content_agent import GroqClient # Import shared Groq client

class ScrapeAgent:
def init(self):
self.ua = UserAgent()
self.groq_client = GroqClient()
self.keywords = json.load(open("./data/keywords.json"))
self.sites = json.load(open("./data/sites.json"))

def scrape_site(self, url):
    try:
        headers = {"User-Agent": self.ua.random}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        products = []
        for item in soup.select(".product"):
            name = item.select_one(".name").text
            if any(kw["keyword"].lower() in name.lower() for kw in self.keywords):
                products.append({"name": name, "url": url, "score": self.groq_client.score_keyword(name)})
        for p in products:
            cursor.execute("INSERT OR IGNORE INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)",
                          (p["name"], "Scraped", "KES 0", 0))
        conn.commit()
        self.update_keywords(products)
        return {"status": "success", "products": len(products)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

def update_keywords(self, products):
    for p in products:
        for kw in self.keywords:
            if kw["keyword"].lower() in p["name"].lower():
                kw["score"] = min(kw["score"] + 0.05, 1.0)
    json.dump(self.keywords, open("./data/keywords.json", "w"))
