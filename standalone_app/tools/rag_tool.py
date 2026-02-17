import requests
import json
from crewai.tools import BaseTool

class RAGMitreTool(BaseTool):
    name: str = "MITRE ATT&CK RAG Tool"
    description: str = "Search for MITRE ATT&CK techniques based on behavior description"
    
    def _run(self, query: str) -> str:
        """
        Queries the RAG service for relevant MITRE ATT&CK techniques.
        """
        url = "http://localhost:8001/retrieve"
        payload = {
            "query": query,
            "collection": "mitre_attack",
            "top_k": 3,
            "min_similarity": 0.3
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return "No matching MITRE ATT&CK techniques found for this query."
            
            formatted_results = []
            for item in data["results"]:
                doc = item["document"]
                score = item["similarity_score"]
                formatted_results.append(f"[Score: {score:.2f}] {doc}")
                
            return "\n\n".join(formatted_results)
            
        except Exception as e:
            return f"Error retrieving MITRE ATT&CK context: {str(e)}. Falling back to general analysis."
