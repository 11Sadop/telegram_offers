import requests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET


def fetch_rss_offers(feed_url: str, feed_name: str, category: str):
    """Fetch offers from an RSS feed using requests and XML parser"""
    offers = []
    
    try:
        # Fetch the RSS feed
        response = requests.get(feed_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code != 200:
            print(f"Failed to fetch {feed_name}: {response.status_code}")
            return offers
        
        # Parse as BeautifulSoup for better XML handling
        soup = BeautifulSoup(response.content, 'xml')
        
        # Find all items
        items = soup.find_all('item')
        
        if not items:
            # Try Atom format
            items = soup.find_all('entry')
        
        print(f"Found {len(items)} items from {feed_name}")
        
        for item in items[:20]:  # Get latest 20 entries
            # Get title
            title_tag = item.find('title')
            title = title_tag.get_text(strip=True) if title_tag else 'New Offer'
            
            # Get link
            link_tag = item.find('link')
            if link_tag:
                link = link_tag.get_text(strip=True) or link_tag.get('href', '')
            else:
                link = ''
            
            # Get description for price extraction
            desc_tag = item.find('description') or item.find('summary') or item.find('content')
            description = ''
            if desc_tag:
                # Clean HTML from description
                desc_soup = BeautifulSoup(desc_tag.get_text(), 'html.parser')
                description = desc_soup.get_text(strip=True)[:500]
            
            # Extract price
            price = extract_price(title + ' ' + description)
            
            # Clean the title
            title = clean_title(title)
            
            # Skip if no valid title or link
            if title == 'New Offer' and not link:
                continue
            
            offers.append({
                'title': title,
                'link': link,
                'price': price,
                'category': category,
                'source': feed_name,
                'date': datetime.now().isoformat()
            })
            
        print(f"Fetched {len(offers)} valid offers from {feed_name}")
        
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
        import traceback
        traceback.print_exc()
    
    return offers


def extract_price(text: str) -> str:
    """Extract price from text using regex"""
    if not text:
        return ""
    
    # Look for common price patterns
    patterns = [
        r'\$[\d,]+\.?\d*',  # $XX.XX
        r'[\d,]+\.?\d*\s*(?:USD|SAR|AED|EUR|GBP)',  # XX USD/SAR
        r'(?:was|from|now|price:?)\s*\$?[\d,]+\.?\d*',  # was $XX
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()
    
    return ""


def clean_title(title: str) -> str:
    """Clean and format the title"""
    if not title:
        return "New Offer"
    
    # Remove HTML tags
    title = re.sub(r'<[^>]+>', '', title)
    
    # Decode HTML entities
    title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
    
    # Remove excessive whitespace
    title = ' '.join(title.split())
    
    # Remove markdown special chars that break Telegram
    title = title.replace('*', '').replace('_', '').replace('[', '(').replace(']', ')').replace('`', '')
    
    # Limit length
    if len(title) > 150:
        title = title[:147] + "..."
    
    return title if title else "New Offer"


def fetch_webpage_offers(url: str, selectors: dict):
    """Scrape offers from a webpage (for sites without RSS)"""
    offers = []
    
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
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
                        'category': 'Offers',
                        'source': url,
                        'date': datetime.now().isoformat()
                    })
            
            print(f"Scraped {len(offers)} offers from {url}")
                    
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return offers


def fetch_all_rss_feeds(feeds: list):
    """Fetch offers from all configured RSS feeds"""
    all_offers = []
    
    for feed in feeds:
        offers = fetch_rss_offers(feed['url'], feed['name'], feed['category'])
        all_offers.extend(offers)
    
    print(f"Total offers fetched: {len(all_offers)}")
    return all_offers
