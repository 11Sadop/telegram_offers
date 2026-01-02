import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    """Fetch offers from an RSS feed"""
    offers = []
    
    try:
        print(f"Fetching from {feed_name}...")
        response = requests.get(feed_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            print(f"Failed to fetch {feed_name}: {response.status_code}")
            return offers
        
        # Parse HTML/XML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all items
        items = soup.find_all('item')
        print(f"Found {len(items)} items")
        
        for item in items[:15]:
            # Get title
            title_tag = item.find('title')
            title = title_tag.get_text(strip=True) if title_tag else ''
            
            # Get link
            link_tag = item.find('link')
            link = ''
            if link_tag:
                # Link might be text or next sibling
                link = link_tag.get_text(strip=True)
                if not link and link_tag.next_sibling:
                    link = str(link_tag.next_sibling).strip()
            
            # Clean title
            title = clean_title(title)
            
            if title and link:
                offers.append({
                    'title': title,
                    'link': link,
                    'price': extract_price(title),
                    'category': category,
                    'source': feed_name,
                    'date': datetime.now().isoformat()
                })
        
        print(f"Extracted {len(offers)} offers from {feed_name}")
        
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    
    return offers


def extract_price(text: str) -> str:
    """Extract price from text"""
    if not text:
        return ""
    patterns = [r'\$[\d,]+\.?\d*', r'[\d,]+\s*(?:USD|SAR)']
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    return ""


def clean_title(title: str) -> str:
    """Clean title for Telegram"""
    if not title:
        return ""
    # Remove HTML
    title = re.sub(r'<[^>]+>', '', title)
    # Remove problematic chars
    for char in ['*', '_', '`', '[', ']']:
        title = title.replace(char, '')
    # Clean whitespace
    title = ' '.join(title.split())
    # Limit length
    if len(title) > 120:
        title = title[:117] + "..."
    return title


def fetch_webpage_offers(url: str, selectors: dict):
    """Scrape offers from webpage"""
    return []


def fetch_all_rss_feeds(feeds: list):
    """Fetch from all feeds"""
    all_offers = []
    for feed in feeds:
        try:
            offers = fetch_rss_offers(feed['url'], feed['name'], feed['category'])
            all_offers.extend(offers)
        except Exception as e:
            print(f"Error with {feed['name']}: {e}")
    print(f"Total: {len(all_offers)} offers")
    return all_offers
