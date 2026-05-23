import requests

API_KEY = "pub_85bb54430c974c32aa0c353a04b99b39"
BASE_URL = "https://newsdata.io/api/1/latest"

def calculate_relevance(query: str, title: str, description: str) -> float:
    query_words = set(query.lower().split())
    if not query_words:
        return 0.0
    target_text = f"{title} {description}".lower()
    
    matches = sum(1 for word in query_words if word in target_text)
    return round(matches / len(query_words), 2)

def search_recent_news(query: str, max_results: int = 3) -> dict:
    """
    Searches NewsData.io and returns a highly structured object for 
    the Gemini Reasoner and Semantic Similarity tools.
    
    Returns:
        dict: {
            "success": bool,
            "data": [
                {
                    "title": str,
                    "description": str,
                    "full_text": str,
                    "source": str,
                    "link": str,
                    "relevance_score": float
                }, ...
            ],
            "error": str or None
        }
    """
    response_schema = {
        "success": False,
        "data": [],
        "error": None
    }

    if not query or not query.strip():
        response_schema["error"] = "Empty search query provided."
        return response_schema

    params = {
        "apikey": API_KEY,
        "q": query.strip(),
        "language": "en"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        raw_data = response.json()
        results = raw_data.get("results", [])

        articles = []
        for article in results:
            title = article.get("title", "No Title Available")
            description = article.get("description", "No description preview available.")
            full_text = article.get("content") or description or "No extended content text available."
            source = article.get("source_id", "Unknown Source")
            link = article.get("link", "#")
            score = calculate_relevance(query, title, description)
            articles.append({
                "title": title,
                "description": description,
                "full_text": full_text,
                "source": source,
                "link": link,
                "relevance_score": score
            })

        articles.sort(key=lambda x: x["relevance_score"], reverse=True)
        response_schema["data"] = articles[:max_results]
        response_schema["success"] = True

    except requests.exceptions.RequestException as e:
        response_schema["error"] = f"Network transaction failure: {str(e)}"
        response_schema["success"] = False

    return response_schema

