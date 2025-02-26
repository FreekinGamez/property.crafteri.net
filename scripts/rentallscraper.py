#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import psycopg2
import time
import re
from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def extract_web_id(url):
    main_url = url.split('?')[0]
    m = re.search(r'-([\d]+)$', main_url)
    if m:
        return int(m.group(1))
    return None

def get_total_pages(soup):
    total = 1
    li_tags = soup.find_all("li", class_="page-item")
    for li in li_tags:
        span = li.find("span", class_="page-link")
        if span and span.text.strip().isdigit():
            try:
                num = int(span.text.strip())
                if num > total:
                    total = num
            except Exception:
                pass
        a_tag = li.find("a", class_="page-link")
        if a_tag and a_tag.text.strip().isdigit():
            try:
                num = int(a_tag.text.strip())
                if num > total:
                    total = num
            except Exception:
                pass
    return total

def scrape_rentals():
    base_url = "https://www.propertygibraltar.com/search"
    params = {
        "category": "1",
        "sale": "0",  # Rentals
        "beds": "0",
        "baths": "0",
        "interior": "0",
        "exterior": "0",
    }
    properties = []
    headers = {
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/110.0.0.0 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    # Request page 1 to determine total pages.
    params["np"] = 1
    print("Requesting page 1")
    time.sleep(2)
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        print("Error: Received status code", response.status_code, "on page 1")
        return properties

    soup = BeautifulSoup(response.text, "html.parser")
    total_pages = get_total_pages(soup)
    print("Total pages detected:", total_pages)

    for page in range(1, total_pages + 1):
        params["np"] = page
        print("Processing page", page, "of", total_pages)
        if page > 1:
            time.sleep(2)
            response = requests.get(base_url, params=params, headers=headers)
            if response.status_code != 200:
                print("Error: Received status code", response.status_code, "on page", page)
                continue
            soup = BeautifulSoup(response.text, "html.parser")
        
        property_items = soup.find_all("div", class_="property-item")
        print("Found", len(property_items), "property items on page", page)
        for item in property_items:
            try:
                # Get property URL and name.
                h5_tag = item.find("h5", class_="text-black")
                if not h5_tag:
                    continue
                link_tag = h5_tag.find("a")
                if not link_tag:
                    continue
                href = link_tag.get("href", "").strip()
                prop_url = href if href.startswith("http") else "https://www.propertygibraltar.com" + href
                name = link_tag.text.strip()

                # Get district.
                h6_tag = item.find("h6")
                district = h6_tag.text.strip() if h6_tag else ""

                # Get price and remove non-digit characters.
                price_tag = item.find("h5", class_="price")
                price = price_tag.text.strip() if price_tag else ""
                price = re.sub(r'[^\d]', '', price)

                # Get image URL.
                image_url = ""
                image_div = item.find("div", class_="property-image")
                if image_div and image_div.has_attr("style"):
                    style = image_div["style"]
                    if "url('" in style:
                        image_url = style.split("url('")[1].split("')")[0]

                # Extract features: beds, baths, INT m2, and EXT m2.
                beds = None
                baths = None
                int_m2 = None
                ext_m2 = None
                features_ul = item.find("ul", class_="features")
                if features_ul:
                    for li in features_ul.find_all("li"):
                        text = li.get_text(" ", strip=True)
                        # If it's a studio, set beds to 0.
                        if "Studio" in text:
                            beds = 0
                            continue
                        m_beds = re.search(r"(\d+)\s*Bed", text, re.IGNORECASE)
                        if m_beds:
                            beds = int(m_beds.group(1))
                        m_baths = re.search(r"(\d+)\s*Bath", text, re.IGNORECASE)
                        if m_baths:
                            baths = int(m_baths.group(1))
                        m_int = re.search(r"(\d+)\s*INT\s*M", text, re.IGNORECASE)
                        if m_int:
                            int_m2 = int(m_int.group(1))
                        m_ext = re.search(r"(\d+)\s*EXT\s*M", text, re.IGNORECASE)
                        if m_ext:
                            ext_m2 = int(m_ext.group(1))
                
                web_id = extract_web_id(prop_url)
                scrape_date = datetime.now()

                property_data = {
                    "name": name,
                    "district": district,
                    "price": price,
                    "url": prop_url,
                    "image_url": image_url,
                    "beds": beds,
                    "baths": baths,
                    "int_m2": int_m2,
                    "ext_m2": ext_m2,
                    "enabled": True,
                    "web_id": web_id,
                    "scrape_date": scrape_date
                }
                properties.append(property_data)
                print(f"Scraped: {name} (ID: {web_id}) - Beds: {beds}, Baths: {baths}, INT: {int_m2}, EXT: {ext_m2}, Price: {price}")
            except Exception as e:
                print("Error processing a property on page", page, ":", e)
                continue

    print("Total properties scraped:", len(properties))
    return properties

def save_to_database(properties):
    conn = psycopg2.connect(
        dbname=os.getenv('DB_DBNAME'),
        user=os.getenv('DB_USERNAME'),
        password=os.getenv('DB_PASSWORD'),
        host="localhost"
    )
    cur = conn.cursor()

    # Create the rent_properties table.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rent_properties (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            district VARCHAR(255),
            url TEXT,
            image_url TEXT,
            beds INTEGER,
            baths INTEGER,
            int_m2 INTEGER,
            ext_m2 INTEGER,
            enabled BOOLEAN DEFAULT TRUE,
            web_id INTEGER UNIQUE,
            scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create the rent_prices table with a UNIQUE constraint on web_id.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rent_prices (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            district VARCHAR(255),
            web_id INTEGER UNIQUE,
            price VARCHAR(50),
            scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Build a set of web_ids for properties currently scraped.
    scraped_web_ids = {prop["web_id"] for prop in properties if prop["web_id"] is not None}

    for prop in properties:
        web_id = prop["web_id"]
        # Upsert the property into rent_properties.
        cur.execute("SELECT id FROM rent_properties WHERE web_id = %s", (web_id,))
        if cur.fetchone() is None:
            cur.execute("""
                INSERT INTO rent_properties
                (name, district, url, image_url, beds, baths, int_m2, ext_m2, enabled, web_id, scrape_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s)
            """, (prop["name"], prop["district"], prop["url"], prop["image_url"],
                  prop["beds"], prop["baths"], prop["int_m2"], prop["ext_m2"],
                  web_id, prop["scrape_date"]))
        else:
            cur.execute("""
                UPDATE rent_properties
                SET name=%s, district=%s, url=%s, image_url=%s, beds=%s, baths=%s, int_m2=%s, ext_m2=%s, enabled=TRUE, scrape_date=%s
                WHERE web_id=%s
            """, (prop["name"], prop["district"], prop["url"], prop["image_url"],
                  prop["beds"], prop["baths"], prop["int_m2"], prop["ext_m2"],
                  prop["scrape_date"], web_id))

        # Upsert the price row in rent_prices so that each property has a single price row.
        cur.execute("SELECT id FROM rent_prices WHERE web_id = %s", (web_id,))
        cur.execute("""
                INSERT INTO rent_prices
                (name, district, web_id, price, scrape_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (prop["name"], prop["district"], web_id, prop["price"], prop["scrape_date"]))
    
    # Disable any properties not found in the current scrape.
    if scraped_web_ids:
        cur.execute("UPDATE rent_properties SET enabled = FALSE WHERE web_id NOT IN %s", (tuple(scraped_web_ids),))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database update complete.")

if __name__ == "__main__":
    print("Starting rentals scraping process...")
    properties = scrape_rentals()
    print("Scraping completed. Updating database...")
    save_to_database(properties)
    print("Rentals script finished successfully.")
