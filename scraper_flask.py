from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_akakce_for_price(query, max_results=20):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.akakce.com/arama/?q={query.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    products = soup.select("ul.pl_v9 > li")

    for product in products[:max_results]:
        title_elem = product.select_one("h3.pn_v8")
        price_elem = product.select_one("span.pt_v9")

        if title_elem and price_elem:
            title = title_elem.get_text(strip=True)
            price_text = price_elem.get_text(strip=True)
            try:
                float(price_text.replace(".", "").replace(",", ".").split()[0])
                return {"title": title, "price": price_text}
            except ValueError:
                continue

    return None

@app.route('/')
def home():
    return " Akakce Price API is running."

@app.route('/get_price')
def get_price():
    part_name = request.args.get('part_name', '').strip()
    if not part_name:
        return jsonify({"status": "error", "message": "Missing part_name parameter"}), 400

    result = scrape_akakce_for_price(part_name)
    if result:
        return jsonify({"status": "ok", "title": result["title"], "price": result["price"]})
    else:
        return jsonify({"status": "not_found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
