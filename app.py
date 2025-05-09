from flask import Flask, request, jsonify
from newspaper import Article
import xml.etree.ElementTree as ET
import re

app = Flask(__name__)




def smart_sanitize_xml(xml: str) -> str:
    # Replace unescaped ampersands not part of entities (e.g., &amp;)
    return re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;)', '&amp;', xml)


# ✅ Function to convert XML to JSON
def parse_xml_to_json(xml_data):
    def etree_to_dict(t):
        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = {}
            for dc in map(etree_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        if not isinstance(dd[k], list):
                            dd[k] = [dd[k]]
                        dd[k].append(v)
                    else:
                        dd[k] = v
            d = {t.tag: dd}
        if t.attrib:
            d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
        if t.text and t.text.strip():
            text = t.text.strip()
            if children or t.attrib:
                d[t.tag]['#text'] = text
            else:
                d[t.tag] = text
        return d

    root = ET.fromstring(xml_data)
    return etree_to_dict(root)

# ✅ Original scrape route (unchanged)
@app.route('/scrape', methods=['POST'])
def scrape_article():
    try:
        data = request.get_json()
        url = data.get("url")

        if not url:
            return jsonify({"error": "URL not provided."}), 400

        article = Article(url)
        article.download()
        article.parse()

        if not article.text.strip():
            return jsonify({"error": "Could not extract article content."}), 200

        return jsonify({"text": article.text}), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route('/xml-to-json', methods=['POST'])
def xml_to_json():
    try:
        raw_xml = request.data.decode("utf-8")
        if not raw_xml.strip():
            return jsonify({"error": "XML not provided."}), 400

        # Clean the XML
        safe_xml = smart_sanitize_xml(raw_xml)

        # Parse the cleaned XML
        parsed_json = parse_xml_to_json(safe_xml)
        return jsonify(parsed_json), 200

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
