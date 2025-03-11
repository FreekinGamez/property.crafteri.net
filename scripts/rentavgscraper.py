import requests
from bs4 import BeautifulSoup
import psycopg2
import time
import random
import re
from datetime import datetime
from urllib.parse import urljoin

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': os.getenv('DB_DBNAME'),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'port': '5432'
}
BASE_URL = "https://www.propertygibraltar.com"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/120.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9"
}

def fetch_html(url, session):
    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        time.sleep(random.uniform(2, 4))  # Mimic human traffic
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_price(price_str):
    try:
        clean_str = price_str.lower().replace('£', '').replace(',', '').strip()
        return float(clean_str)
    except Exception as e:
        print(f"Error parsing price '{price_str}': {e}")
        return None

def extract_market_stats(soup):
    stats = {}
    try:
        # Look for the market-stats div
        market_stats_div = soup.find("div", class_="market-stats")
        if not market_stats_div:
            print("No Market Stats div found")
            return stats
            
        # Find the rental section marker
        rent_marker = None
        for p in market_stats_div.find_all("p"):
            if "Average price to rent" in p.get_text(strip=True):
                rent_marker = p
                break
        
        if not rent_marker:
            print("No rental prices section found")
            return stats

        # Only process paragraphs that come after the rent marker
        current = rent_marker.next_sibling
        while current:
            if isinstance(current, str):
                current = current.next_sibling
                continue
                
            if current.name == 'p':
                text = current.get_text(strip=True).lower()
                strong = current.find("strong", class_="text-site2")
                
                if strong:
                    price = extract_price(strong.text)
                    if "studio:" in text:
                        stats["studio"] = price
                    elif "1 bed" in text:
                        stats["1bed"] = price
                    elif "2 bed" in text:
                        stats["2bed"] = price
                    elif "3 bed" in text:
                        stats["3bed"] = price
                    elif "4 bed" in text:
                        stats["4bed"] = price
            
            # Stop if we hit a link or button that typically appears after the stats
            if current.name == 'a':
                break
                
            current = current.next_sibling
            
        print(f"Extracted rental market stats: {stats}")
    except Exception as e:
        print(f"Error extracting market stats: {e}")
    return stats

def scrape_properties():
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Database connection error: {e}")
        return

    cur = conn.cursor()

    # Start at the map page
    map_url = urljoin(BASE_URL, "/map")
    map_soup = fetch_html(map_url, session)
    if not map_soup:
        print("Failed to fetch the map page.")
        return

    # Extract district links from the div with id "districts"
    districts_div = map_soup.find("div", id="districts")
    if not districts_div:
        print("No districts found on map page.")
        return

    district_links = []
    for a in districts_div.find_all("a", href=True):
        href = a["href"]
        if "/districts/" in href:
            full_link = href if href.startswith("http") else BASE_URL + href
            district_name = a.get_text(strip=True)
            district_links.append((district_name, full_link))

    # Process each district
    for district_name, district_url in district_links:
        print(f"Processing district: {district_name} ({district_url})")
        district_soup = fetch_html(district_url, session)
        if not district_soup:
            continue

        # Developments are listed in <ul class="agents-list">
        agents_list = district_soup.find("ul", class_="agents-list")
        if not agents_list:
            print(f"No developments found in {district_name}.")
            continue

        for dev in agents_list.find_all("li"):
            dev_item = dev.find("div", class_="agent-item")
            if not dev_item:
                continue

            dev_name_tag = dev_item.find("h5")
            if not dev_name_tag:
                continue
            development_name = dev_name_tag.get_text(strip=True)

            # Extract image_url and development_url from the image div if present
            image_url = None
            development_url = None
            image_div = dev_item.find("div", class_="image")
            if image_div:
                style_attr = image_div.get("style", "")
                image_match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_attr)
                if image_match:
                    image_url = image_match.group(1)
                a_dev = image_div.find("a", href=True)
                if a_dev:
                    development_url = urljoin(BASE_URL, a_dev["href"])

            # Look inside the stats list for the Residential To Let link only.
            stats_ul = dev_item.find("ul", class_="stats")
            to_let_link = None
            if stats_ul:
                for stat_li in stats_ul.find_all("li"):
                    h5_stat = stat_li.find("h5", class_="text-site2")
                    if h5_stat and "residential" in h5_stat.get_text(strip=True).lower():
                        p_stat = stat_li.find("p")
                        if p_stat:
                            for a_tag in p_stat.find_all("a", href=True):
                                if "to let" in a_tag.get_text(strip=True).lower():
                                    to_let_link = urljoin(BASE_URL, a_tag["href"])
                                    break
                    if to_let_link:
                        break

            if not to_let_link:
                print(f"No 'Residential To Let' link found for {development_name} in {district_name}.")
                continue

            print(f"  Processing development: {development_name} -> To Let URL: {to_let_link}")

            # Visit the To Let listings page
            let_soup = fetch_html(to_let_link, session)
            if not let_soup:
                continue

            # Select the first property listing (by looking for a "property-item" container)
            property_li = let_soup.select_one("ul.properties-list > li:first-child")
            if not property_li:
                print(f"No property listing found for {development_name} in {district_name}.")
                continue

            property_link_tag = property_li.find("a", href=True)
            if not property_link_tag or not property_link_tag.get("href"):
                print(f"No property link found for {development_name} in {district_name}.")
                continue

            property_url = urljoin(BASE_URL, property_link_tag["href"])
            print(f"    Found property URL: {property_url}")

            # Fetch property details and extract market stats
            prop_soup = fetch_html(property_url, session)
            if not prop_soup:
                continue

            market_stats = extract_market_stats(prop_soup)

            # Prepare the data dictionary for insertion
            data = {
                'name': development_name,
                'district': district_name,
                'image_url': image_url,
                'development_url': development_url,
                'price_studio': market_stats.get("studio"),
                'price_1bed': market_stats.get("1bed"),
                'price_2bed': market_stats.get("2bed"),
                'price_3bed': market_stats.get("3bed"),
                'price_4bed': market_stats.get("4bed"),
                'scrape_date': datetime.now()
            }

            # Updated insert query: include DEFAULT for the id column.
            insert_query = """
                INSERT INTO rent_avg_prices 
                (id, name, district, image_url, development_url, price_studio, price_1bed, price_2bed, price_3bed, price_4bed, scrape_date)
                VALUES (DEFAULT, %(name)s, %(district)s, %(image_url)s, %(development_url)s, %(price_studio)s, %(price_1bed)s, %(price_2bed)s, %(price_3bed)s, %(price_4bed)s, %(scrape_date)s)
            """
            
            try:
                cur.execute(insert_query, data)
                conn.commit()
                print(f"    Inserted data for {development_name}")
            except Exception as e:
                conn.rollback()
                print(f"    Failed to insert data for {development_name}: {e}")

    cur.close()
    conn.close()
    session.close()
    print("Scraping completed")

if __name__ == "__main__":
    scrape_properties()
