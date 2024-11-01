from flask import Flask, request, jsonify
from googlesearch import search
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_website_text(url):
    """Fetch the content of the URL and convert it to plain text."""
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        return f"Failed to scrape {url}: {str(e)}"

@app.route('/scrape', methods=['GET'])
def scrape_google_results():
    """Endpoint that scrapes data from top 5 websites based on user's search query."""
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400

    try:
        # Use stop=5 to limit the number of results to 5
        search_results = search(query, num_results=5)
    except Exception as e:
        return jsonify({"error": f"Google search failed: {str(e)}"}), 500

    websites_data = []
    for url in search_results:
        website_text = get_website_text(url)
        websites_data.append({
            'url': url,
            'content': website_text[:500]  # Limiting text length for readability
        })
    
    return jsonify({'query': query, 'results': websites_data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
