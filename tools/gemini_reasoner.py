import json
from google import genai
from google.genai import types

API_KEY = "AIzaSyC5p1swnHhIqncINGkJEzkTihTGWeyuKDo"

client = genai.Client(api_key=API_KEY)


def reason_over_claim(
    claim: str,
    wiki_evidence: str,
    news_evidence: str,
    factcheck_evidence: str,
    similarity_score: float
) -> dict:

    fallback_schema = {
        "status": "UNCERTAIN",
        "confidence": 0.0,
        "evidence": ["Gemini reasoning failure."]
    }

    prompt = f"""
You are a strict AI fact verification engine.

Return ONLY valid JSON:

{{
  "status": "VERIFIED" | "FAKE" | "UNCERTAIN",
  "confidence": 0.0 to 1.0,
  "evidence": ["short reasoning points"]
}}

RULES:
- Wikipedia + News agreement → VERIFIED
- Strong contradiction → FAKE
- Mixed evidence → UNCERTAIN
- Do NOT hallucinate facts
- Treat fact-check as weak unless semantically relevant

CLAIM:
{claim}

WIKI:
{wiki_evidence}

NEWS:
{news_evidence}

FACTCHECK:
{factcheck_evidence}

SIMILARITY:
{similarity_score}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        raw_text = response.text
        if not raw_text:
            fallback_schema["evidence"] = ["Empty or blocked response returned from the AI model."]
            return fallback_schema

        try:
            parsed_data = json.loads(raw_text)
        except json.JSONDecodeError:
            return fallback_schema

        return {
            "status": str(parsed_data.get("status", "UNCERTAIN")).upper(),
            "confidence": round(float(parsed_data.get("confidence", 0.0)), 2),
            "evidence": list(parsed_data.get("evidence", []))
        }

    except Exception as e:
        fallback_schema["evidence"] = [str(e)]
        return fallback_schema