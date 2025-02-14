import psycopg2
from datetime import datetime

DB_CONFIG = {
    "dbname": "property_db",
    "user": "property",
    "password": "P.32Jfp!d.",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')}] {message}")

def calculate_roi():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            log("🚀 Starting ROI calculation process")
            log("🧹 Clearing roi_calc table")
            cur.execute("TRUNCATE TABLE roi_calc")

            log("🔍 Fetching enabled properties from sales_properties")
            cur.execute("""
                SELECT web_id, name, district, beds, baths, int_m2, ext_m2
                FROM sales_properties
                WHERE enabled = TRUE
            """)
            sales_props = cur.fetchall()
            log(f"📊 Found {len(sales_props)} properties to process")

            for idx, prop in enumerate(sales_props, 1):
                web_id, name, district, beds, baths, int_m2, ext_m2 = prop
                log(f"\n🔢 Processing property {idx}/{len(sales_props)}")
                log(f"   WEB_ID: {web_id}")
                log(f"   NAME: {name}")
                
                try:
                    beds = int(beds) if beds is not None else 0
                except ValueError:
                    beds = 0
                
                log(f"   BEDS: {beds}, BATHS: {baths}")
                log(f"   SIZES: INT {int_m2}m², EXT {ext_m2}m²")

                # Get sale price
                log("💰 Fetching latest sale price")
                cur.execute("""
                    SELECT price 
                    FROM sales_prices 
                    WHERE web_id = %s 
                    ORDER BY scrape_date DESC 
                    LIMIT 1
                """, (web_id,))
                
                if cur.rowcount == 0:
                    log("⏩ Skipping - no sale price found")
                    continue
                    
                sale_price = cur.fetchone()[0]
                try:
                    sale_price = float(sale_price)
                    log(f"   SALE PRICE: €{sale_price:,.2f}")
                except (ValueError, TypeError):
                    log(f"   SALE PRICE: {sale_price}")
                    continue

                # Exact match calculation
                est_rent = None
                calc_method = 'no_match'
                used_props = None
                
                if int_m2:
                    log("🔍 Searching for exact matches in rent_properties (INT only)")
                    try:
                        min_int = float(int_m2) * 0.85
                        max_int = float(int_m2) * 1.15
                    except TypeError:
                        log("   ❌ Invalid int_m2 value")
                        min_int = max_int = 0

                    cur.execute("""
                        SELECT web_id 
                        FROM rent_properties 
                        WHERE name = %s
                          AND beds = %s
                          AND baths = %s
                          AND int_m2 BETWEEN %s AND %s
                          AND enabled = TRUE
                    """, (name, beds, baths, min_int, max_int))
                    
                    matches = [row[0] for row in cur.fetchall()]
                    log(f"   🎯 Found {len(matches)} potential matches")

                    if matches:
                        log("💶 Fetching rent prices for matches")
                        prices = []
                        for match_web_id in matches:
                            cur.execute("""
                                SELECT price 
                                FROM rent_prices 
                                WHERE web_id = %s
                                ORDER BY scrape_date DESC 
                                LIMIT 1
                            """, (match_web_id,))
                            
                            price_row = cur.fetchone()
                            if price_row and price_row[0]:
                                try:
                                    price = float(price_row[0])
                                    prices.append(price)
                                    log(f"   ✅ Found price €{price:,.2f} for {match_web_id}")
                                except (ValueError, TypeError):
                                    log(f"   ❌ Invalid price for {match_web_id}")
                            else:
                                log(f"   ❌ No price found for {match_web_id}")
                        
                        log(f"   📈 Retrieved {len(prices)} valid prices")
                        
                        if prices:
                            est_rent = sum(prices) / len(prices)
                            calc_method = 'exact_match'
                            used_props = matches
                            log(f"   ✅ CALCULATED RENT: €{est_rent:,.2f}")

                # Building average fallback
                if not est_rent:
                    log("📉 Attempting building average method")
                    
                    # Determine price column based on bedroom count
                    if beds == 0:
                        price_column = "price_studio"
                    elif beds == 1:
                        price_column = "price_1bed"
                    elif beds == 2:
                        price_column = "price_2bed"
                    else:
                        price_column = "price_3bed"

                    log(f"   🔎 Looking for {price_column} in rent_avg_prices")
                    
                    try:
                        cur.execute(f"""
                            SELECT {price_column}
                            FROM rent_avg_prices 
                            WHERE name = %s
                            ORDER BY scrape_date DESC 
                            LIMIT 1
                        """, (name,))
                        
                        avg_row = cur.fetchone()
                        if avg_row and avg_row[0]:
                            try:
                                est_rent = float(avg_row[0])
                                calc_method = 'building_average'
                                log(f"   🏢 USING AVERAGE ({price_column}): €{est_rent:,.2f}")
                            except (ValueError, TypeError):
                                log("   ❌ Invalid average price")
                        else:
                            log(f"   ❌ No {price_column} available")
                    except Exception as e:
                        log(f"   🚨 Database error: {str(e)}")

                # ROI Calculation
                roi = None
                if est_rent and sale_price:
                    try:
                        annual_rent = est_rent * 12
                        roi = (annual_rent / sale_price) * 100
                        log(f"   📈 ROI: {roi:.2f}%")
                    except ZeroDivisionError:
                        log("   🚨 ERROR: Division by zero (sale price is 0)")
                else:
                    log("   ⚠️ ROI not calculated")

                # Save results
                log("💾 Saving to roi_calc")
                try:
                    cur.execute("""
                        INSERT INTO roi_calc 
                        (web_id, name, district, est_rent_price, roi, calc_method, used_properties)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        web_id,
                        name,
                        district,
                        est_rent,
                        roi,
                        calc_method,
                        used_props
                    ))
                except Exception as e:
                    log(f"   🚨 Insert failed: {str(e)}")
                    conn.rollback()

            conn.commit()
            log("\n✅ SUCCESS: ROI calculations completed")
            log(f"Processed {len(sales_props)} properties")

    except Exception as e:
        conn.rollback()
        log(f"\n💥 CRITICAL FAILURE: {str(e)}")
    finally:
        conn.close()
        log("🔚 Database connection closed")

if __name__ == "__main__":
    calculate_roi()
