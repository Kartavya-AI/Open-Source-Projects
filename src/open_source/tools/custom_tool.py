import os
import json
import requests
from langchain.tools import tool

@tool("Github Search")
def github_search_tool(query: str):
    """
    Searches Github for open-source projects based on a query.
    This tool uses the Serper API to perform a Google search focused on github.com.
    """
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable not set."

    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": f"site:github.com {query}",
        "num": 10  # Get top 10 results
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        results = response.json()

        # Extracting relevant information
        extracted_results = []
        if 'organic' in results:
            for item in results.get('organic', []):
                extracted_results.append({
                    "title": item.get('title', 'N/A'),
                    "link": item.get('link', '#'),
                    "snippet": item.get('snippet', 'No snippet available.')
                })
        
        if not extracted_results:
            return "No relevant GitHub projects found for the query."

        return extracted_results

    except requests.exceptions.RequestException as e:
        return f"Error making request to Serper API: {e}"
    except json.JSONDecodeError:
        return "Error: Failed to decode JSON response from Serper API."