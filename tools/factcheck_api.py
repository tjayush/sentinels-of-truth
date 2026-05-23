import requests

BASE_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
API_KEY = "AIzaSyCZIX4SlAw8hRO9I1nwkbYf5HVFfdNvryI"


def query_factcheck_api(query: str, max_results: int = 2) -> dict:
   
    result_schema = {
        "success": False,
        "data": [],
        "error": None
    }

    if not query or not query.strip():
        result_schema["error"] = "Empty query provided."
        return result_schema

    params = {
        "query": query.strip(),
        "key": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        if response.status_code != 200:
            result_schema["error"] = f"API error: {response.status_code}"
            return result_schema

        raw_data = response.json()
        claims_list = raw_data.get("claims", [])

        if not claims_list:
            result_schema["success"] = True
            result_schema["error"] = "No fact-check results found"
            return result_schema

        structured_results = []
        for c in claims_list[:max_results]:
            text = c.get("text", "")
            claimant = c.get("claimant", "Unknown Source")
            reviews = c.get("claimReview", [])

            if reviews:
                review = reviews[0]
                publisher = review.get("publisher", {}).get("name", "Unknown")
                verdict = review.get("textualRating", "Unrated")
                url = review.get("url", "#")
            else:
                publisher = "Unknown"
                verdict = "Unrated"
                url = "#"

            structured_results.append({
                "claim_text": text,
                "claimant": claimant,
                "publisher": publisher,
                "review_verdict": str(verdict).upper().strip(),  
                "review_url": url,
                "relevance_hint": "medium",
                "source": "google_factcheck" 
            })

        result_schema["data"] = structured_results
        result_schema["success"] = True

    except requests.exceptions.RequestException as e:
        result_schema["error"] = f"Network failure: {str(e)}"
        result_schema["success"] = False

    return result_schema