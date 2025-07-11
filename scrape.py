import httpx
import xml.etree.ElementTree as ET
from pydantic import BaseModel
from typing import List, Dict

class TopicRequest(BaseModel):
    topics: List[str]

async def scrape_arxiv(request: TopicRequest) -> Dict[str, List[Dict]]:
    base_url = "http://export.arxiv.org/api/query"
    results: Dict[str, List[Dict]] = {}

    async with httpx.AsyncClient() as client:
        for topic in request.topics:
            query = f"search_query=all:{topic}&start=0&max_results=10&sortBy=relevance"
            try:
                response = await client.get(f"{base_url}?{query}", timeout=10.0)
                response.raise_for_status()

                root = ET.fromstring(response.content)
                ns = {"atom": "http://www.w3.org/2005/Atom"}

                topic_results = []
                for entry in root.findall("atom:entry", ns):
                    paper = {
                        "title": entry.find("atom:title", ns).text.strip(),
                        "summary": entry.find("atom:summary", ns).text.strip(),
                        "authors": [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)],
                        "link": entry.find("atom:id", ns).text,
                        "published": entry.find("atom:published", ns).text
                    }
                    topic_results.append(paper)

                results[topic] = topic_results

            except Exception as e:
                # Log or print error if needed
                continue  # Skip this topic and continue with the rest

    return results if results else {}