import feedparser
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    """Fetch offers from an RSS feed"""
    offers = []
    
    try:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries[:20]:  # Get latest 20 entries
            title = entry.get('title', 'عرض جديد')
            link = entry.get('link', '')
            
            # Try to extract price from title or description
            price = extract_price(entry.get('title', '') + ' ' + entry.get('description', ''))
            
            # Get publication date
            pub_date = entry.get('published', datetime.now().isoformat())
            
            # Clean the title
            title = clean_title(title)
            
            offers.append({
                'title': title,
                'link': link,
                'price': price,
                'category': category,
                'source': feed_name,
                'date': pub_date
            })
            
        print(f"✅ Fetched {len(offers)} offers from {feed_name}")
        
    except Exception as e:
        print(f"❌ Error fetching {feed_name}: {e}")
    
    return offers


def extract_price(text: str) -> str:
    """Extract price from text using regex"""
    # Look for common price patterns
    patterns = [
        r'\$[\d,]+\.?\d*',  # $XX.XX
        r'[\d,]+\.?\d*\s*(?:USD|SAR|AED|ريال|دولار)',  # XX USD/SAR
        r'(?:was|from|now)\s*\$?[\d,]+\.?\d*',  # was $XX
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    
    return ""


def clean_title(title: str) -> str:
    """Clean and format the title"""
    # Remove excessive whitespace
    title = ' '.join(title.split())
    
    # Limit length
    if len(title) > 200:
        title = title[:197] + "..."
    
    return title


def fetch_webpage_offers(url: str, selectors: dict):
    """Scrape offers from a webpage (for sites without RSS)"""
    offers = []
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find offer elements based on selectors
            items = soup.select(selectors.get('container', '.deal-item'))
            
            for item in items[:20]:
                title_el = item.select_one(selectors.get('title', '.title'))
                link_el = item.select_one(selectors.get('link', 'a'))
                price_el = item.select_one(selectors.get('price', '.price'))
                
                if title_el and link_el:
                    offers.append({
                        'title': clean_title(title_el.get_text(strip=True)),
                        'link': link_el.get('href', ''),
                        'price': price_el.get_text(strip=True) if price_el else '',
                        'category': 'عروض',
                        'source': url,
                        'date': datetime.now().isoformat()
                    })
            
            print(f"✅ Scraped {len(offers)} offers from {url}")
                    
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
    
    return offers


def fetch_all_rss_feeds(feeds: list):
    """Fetch offers from all configured RSS feeds"""
    all_offers = []
    
    for feed in feeds:
        offers = fetch_rss_offers(feed['url'], feed['name'], feed['category'])
        all_offers.extend(offers)
    
    return all_offers
