from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    return "Akakce Scraper is running!"

@app.route("/get_price")
def get_price():
    part_name = request.args.get("part_name")
    if not part_name:
        return jsonify({"status": "error", "message": "Missing part_name parameter"})

    # Encode part name for URL
    search_query = part_name.replace(" ", "+")
    url = f"https://www.akakce.com/arama/?q={search_query}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers)
        print("Status Code:", response.status_code)
        print("HTML Snippet:", response.text[:500])  # First 500 chars

        if response.status_code != 200:
            return jsonify({"status": "error", "message": "Failed to fetch page"})

        soup = BeautifulSoup(response.text, "html.parser")
        price_tag = soup.select_one(".pt_v8")  # adjust selector if needed

        if not price_tag:
            return jsonify({"status": "not_found"})

        return jsonify({
            "status": "success",
            "part_name": part_name,
            "price": price_tag.text.strip()
        })

    except Exception as e:
        print("Exception occurred:", str(e))
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
