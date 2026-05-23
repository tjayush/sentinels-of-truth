from tools.wikipedia_search import search_wikipedia
from tools.factcheck_api import query_factcheck_api
from tools.news_search import search_recent_news
from tools.semantic_similarity import check_database_similarity
from tools.gemini_reasoner import reason_over_claim

class InvestigatorAgent:
    
    def __init__(self, debug_mode: bool = True):
        self.agent_name = "Agent Alpha (Investigator)"
        self.debug_mode = debug_mode

    def log_activity(self, message: str, history_list: list):
        """Helper to print to terminal and append to the UI tracking history state."""
        formatted_log = f"[{self.agent_name}] {message}"
        if self.debug_mode:
            print(formatted_log)
        history_list.append(formatted_log)

    def execute_investigation(self, claim: str, history: list) -> dict:
        """Runs the complete investigative workflow on an incoming claim."""
        claim = claim.strip()
        
        if not claim:
            self.log_activity("Received empty claim input. Investigation aborted.", history)
            return {
                "verification_report": {
                    "status": "UNCERTAIN",
                    "confidence": 0.0,
                    "evidence": ["Empty claim submitted."]
                },
                "db_similarity_context": {}
            }
        
        self.log_activity(f"Starting investigation pipeline for claim: '{claim}'", history)

        search_query = claim
        if len(claim.split()) > 6 or "!!" in claim or ":" in claim:
            clean_text = claim.replace("Breaking news:", "").replace("!!", "").replace(":", "")
            search_query = " ".join(clean_text.split()[:5])
            self.log_activity(f"Optimized long assertion text into search target keywords: '{search_query}'", history)

        self.log_activity("Scanning local knowledge base for existing semantic references...", history)
        db_similarity = check_database_similarity(claim)
        similarity_score = db_similarity.get("score", 0.0)
        
        if db_similarity.get("match_found"):
            matched_text = db_similarity["matched_record"]["claim"]
            self.log_activity(f"Semantic match found in DB (Score: {similarity_score}) -> '{matched_text}'", history)
        else:
            self.log_activity(f"No close semantic duplicates found in historical logs (Score: {similarity_score}). Proceeding with external search tracking.", history)

        self.log_activity("Querying Wikipedia Knowledge Infrastructure...", history)
        wiki_result = search_wikipedia(search_query)
        
        if wiki_result.get("found"):
            summary_slice = wiki_result["summary"][:1200]
            wiki_text = f"Title: {wiki_result['title']}\nSummary: {summary_slice}"
        else:
            wiki_text = wiki_result.get("summary", "No informational encyclopedic record found for these terms.")[:1200]

        self.log_activity("Scanning digital news ecosystems via NewsData API...", history)
        news_result = search_recent_news(search_query, max_results=2)
        
        news_texts = []
        if news_result.get("success") and news_result.get("data"):
            for idx, art in enumerate(news_result["data"]):
                description = art.get("description") or "No description available."
                news_texts.append(f"[{idx+1}] {art['title']} - {description[:500]} (Relevance: {art.get('relevance_score', 1.0)})")
            news_summary = "\n".join(news_texts)
        else:
            news_summary = news_result.get("error") or "No recent news matching this claim was captured."

        self.log_activity("Checking global factual repositories and debunking archives...", history)
        factcheck_result = query_factcheck_api(search_query, max_results=2)
        
        fact_texts = []
        if factcheck_result.get("success") and factcheck_result.get("data"):
            for idx, item in enumerate(factcheck_result["data"]):
                claim_slice = item['claim_text'][:300]
                fact_texts.append(f"[{idx+1}] Claim: {claim_slice} | Verdict: {item['review_verdict']} | Publisher: {item['publisher']}")
            fact_summary = "\n".join(fact_texts)
        else:
            fact_summary = factcheck_result.get("error") or "No formal fact-check records found matching this inquiry."

        self.log_activity("Deploying Gemini Engine to re-verify live data parameters...", history)
        verification_report = reason_over_claim(
            claim=claim,  
            wiki_evidence=wiki_text,
            news_evidence=news_summary,
            factcheck_evidence=fact_summary,
            similarity_score=similarity_score
        )

        self.log_activity(f"Arbitration complete. Generated Verdict: {verification_report.get('status')} with confidence {verification_report.get('confidence')}", history)
        
        return {
            "verification_report": verification_report,
            "db_similarity_context": db_similarity
        }