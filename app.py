#hi

from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="property_db",  # Changed from property_db
        user="property",
        password="P.32Jfp!d."
    )

@app.route('/', methods=['GET'])
def get_properties():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT 
                sp.web_id,
                sp.name,
                sp.district,
                sp.url,
                sp.image_url,
                sp.beds,
                sp.baths,
                sp.int_m2,
                sp.ext_m2,
                r.est_rent_price,
                r.used_properties,
                r.roi
            FROM sales_properties sp
            INNER JOIN roi_calc r ON sp.web_id::integer = r.web_id::integer
            WHERE sp.enabled = true
            AND r.roi IS NOT NULL
            ORDER BY r.created_at DESC
        """)
        
        properties = cur.fetchall()

        for prop in properties:
            cur.execute("""
                SELECT price
                FROM sales_prices
                WHERE web_id::integer = %s
                ORDER BY scrape_date DESC
                LIMIT 1
            """, (prop['web_id'],))
            price_data = cur.fetchone()
            if price_data:
                prop.update(price_data)

        cur.close()
        conn.close()
        return jsonify(properties)

    except Exception as e:
        logging.error(f"Error in get_properties: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
