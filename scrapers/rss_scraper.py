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
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Find all items (works for both RSS and Atom feeds)
        items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items[:20]:  # Get latest 20 entries
            # Try to get title
            title_el = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
            title = title_el.text if title_el is not None else 'New Offer'
            
            # Try to get link
            link_el = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
            if link_el is not None:
                link = link_el.text or link_el.get('href', '')
            else:
                link = ''
            
            # Try to get description for price extraction
            desc_el = item.find('description') or item.find('{http://www.w3.org/2005/Atom}summary')
            description = desc_el.text if desc_el is not None else ''
            
            # Extract price
            price = extract_price(title + ' ' + (description or ''))
            
            # Clean the title
            title = clean_title(title)
            
            offers.append({
                'title': title,
                'link': link,
                'price': price,
                'category': category,
                'source': feed_name,
                'date': datetime.now().isoformat()
            })
            
        print(f"Fetched {len(offers)} offers from {feed_name}")
        
    except Exception as e:
        print(f"Error fetching {feed_name}: {e}")
    
    return offers


def extract_price(text: str) -> str:
    """Extract price from text using regex"""
    if not text:
        return ""
    
    # Look for common price patterns
    patterns = [
        r'\$[\d,]+\.?\d*',  # $XX.XX
        r'[\d,]+\.?\d*\s*(?:USD|SAR|AED)',  # XX USD/SAR
        r'(?:was|from|now)\s*\$?[\d,]+\.?\d*',  # was $XX
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
    
    return all_offers
