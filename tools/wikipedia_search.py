import requests
import urllib.parse


def search_wikipedia(query: str) -> dict:
    
    result_schema = {
        "found": False,
        "title": "",
        "summary": "",
        "url": "",
        "source": "wikipedia"
    }

    if not query or not query.strip():
        return result_schema

    try:
        headers = {
            "User-Agent": "SentinelsOfTruthBot/1.0 (contact: ayushmansarkar123@gmail.com)"
        }
        
        search_url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1
        }

        response = requests.get(
            search_url,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            result_schema["summary"] = "Wikipedia API error or connectivity failure."
            return result_schema

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        if not search_results:
            result_schema["summary"] = "No matching Wikipedia entry found."
            return result_schema

        best_match = search_results[0]
        title = best_match.get("title", "")

        if not title:
            return result_schema

        formatted_title = urllib.parse.quote(title.replace(" ", "_"))

        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"

        summary_response = requests.get(
            summary_url,
            headers=headers,
            timeout=10
        )

        if summary_response.status_code != 200:
            result_schema["summary"] = "Wikipedia summary fetch failed."
            return result_schema

        summary_data = summary_response.json()

        extract = summary_data.get("extract", "")
        page_url = summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")

        if extract:
            result_schema.update({
                "found": True,
                "title": title,
                "summary": extract,
                "url": page_url
            })

        return result_schema

    except requests.exceptions.RequestException as e:
        return {
            "found": False,
            "summary": f"Wikipedia network error: {str(e)}",
            "title": "",
            "url": "",
            "source": "wikipedia"
        }

    except Exception as e:
        return {
            "found": False,
            "summary": f"Unexpected error: {str(e)}",
            "title": "",
            "url": "",
            "source": "wikipedia"
        }