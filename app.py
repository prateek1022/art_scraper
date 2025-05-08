from flask import Flask, request, jsonify
from newspaper import Article

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_article():
    try:
        # Parse input JSON
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL not provided."}), 400

        # Download and parse the article
        article = Article(url)
        article.download()
        article.parse()

        if not article.text.strip():
            return jsonify({"error": "Could not extract article content."}), 200

        return jsonify({"text": article.text}), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
