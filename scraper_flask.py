from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

def scrape_akakce_for_price(query, max_results=20):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    search_url = f"https://www.akakce.com/arama/?q={query.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f" Request failed: {e}")
        return None

    # Debug: print the HTML Akakce returns (first 2000 chars)
    print("=== AKAKCE HTML START ===")
    print(response.text[:2000])
    print("=== AKAKCE HTML END ===")

    soup = BeautifulSoup(response.content, "html.parser")
    
    # Try to match current Akakce product list selector
    products = soup.select("ul[class^='PL_'] > li")

    for product in products[:max_results]:
        title_tag = product.find("a", title=True)
        price_tag = product.select_one("span.ps_v9")

        if title_tag and price_tag:
            title = title_tag["title"].strip()
            price = price_tag.get_text(strip=True)

            # Validate price format (optional)
            try:
                float(price.replace(".", "").replace(",", ".").split()[0])
                return {"title": title, "price": price}
            except ValueError:
                continue

    return None

@app.route('/get_price')
def get_price():
    part_name = request.args.get('part_name', '')
    if not part_name:
        return jsonify({"status": "error", "message": "Missing part_name parameter"}), 400

    result = scrape_akakce_for_price(part_name)
    if result:
        return jsonify({"status": "ok", "title": result["title"], "price": result["price"]})
    else:
        return jsonify({"status": "not_found"})

if __name__ == "__main__":
    # Use dynamic port for Render, default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
