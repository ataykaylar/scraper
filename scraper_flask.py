from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_akakce_for_price(query, max_results=20):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}
    search_url = f"https://www.akakce.com/arama/?q={query.replace(' ', '+')}"

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
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

    except Exception as e:
        return {"error": f"Failed to fetch page: {str(e)}"}

@app.route('/get_price')
def get_price():
    part_name = request.args.get('part_name', '')
    if not part_name:
        return jsonify({"status": "error", "message": "Missing part_name parameter"}), 400

    result = scrape_akakce_for_price(part_name)

    if result is None:
        return jsonify({"status": "not_found"})
    elif "error" in result:
        return jsonify({"status": "error", "message": result["error"]})
    else:
        return jsonify({"status": "ok", "title": result["title"], "price": result["price"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
