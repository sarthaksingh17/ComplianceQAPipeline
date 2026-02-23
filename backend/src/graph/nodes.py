import json
import os
import logging
from typing import Dict, Any

from groq import Groq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from backend.src.graph.state import VideoAuditState
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("LLMOPS")
logging.basicConfig(level=logging.INFO)



# NODE 1 → Video Ingestion (Download + Whisper Transcription)


def index_video_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Node 1:
    - Downloads YouTube video
    - Converts speech to text using Whisper
    - Returns transcript + local file path
    """

    video_url = state.get("video_url")
    logger.info(f"----[Node:Indexer] Processing : {video_url}")

    try:
        if not video_url:
            raise ValueError("video_url is required")

        vi_service = VideoIndexerService()

        # Download video
        local_path = vi_service.download_youtube_video(
            video_url,
            output_path=f"temp_audit_video_{state.get('video_id')}.%(ext)s"
        )

        logger.info("Video downloaded successfully.")

        # Transcribe
        transcript = vi_service.transcribe_video(local_path)

        logger.info("Transcription completed successfully.")

        return {
            "local_file_path": local_path,
            "transcript": transcript
        }

    except Exception as e:
        logger.error(f"[Node:Indexer] Failed: {str(e)}")
        raise



# NODE 2 → RAG Retrieval + Groq LLM Audit


def audit_content_node(state: VideoAuditState) -> Dict[str, Any]:
    """
    Node 2:
    - Loads FAISS vector DB
    - Embeds transcript
    - Retrieves relevant compliance rules
    - Sends transcript + rules to Groq
    - Returns structured JSON compliance result
    """

    logger.info("----[Node:Auditor] Running RAG + LLM Audit")

    try:
        transcript = state.get("transcript", "")
        ocr_text = state.get("ocr_text", "")
        video_metadata = state.get("video_metadata", {})

        if not transcript:
            logger.warning("No transcript available. Skipping audit.")
            return {
                "compliance_issues": [],
                "final_status": "FAIL",
                "final_report": "Audit skipped because transcript missing."
            }

        
        # 1️⃣ Load FAISS Vector Store
       

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        vector_store = FAISS.load_local(
            "backend/data/faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )

        
        # 2️⃣ RAG Query
        

        query_text = f"""
Find compliance rules related to:
- Endorsement disclosures
- Influencer marketing
- Product claims
- Advertising standards
- Required disclaimers

Based on this transcript:

{transcript}
"""

        docs = vector_store.similarity_search(query_text, k=3)

        retrieved_rules = "\n\n".join(
            [doc.page_content for doc in docs]
        )
        print("\n===== RETRIEVED RULES =====")
        print(retrieved_rules)
        print("===== END RULES =====\n")

        
        # Strict JSON Prompt
       

        system_prompt = f"""
You are a strict compliance auditor AI.

CRITICAL INSTRUCTIONS:
- Output MUST be valid JSON.
- Output MUST contain ONLY a single JSON object.
- Do NOT include explanations.
- Do NOT include commentary.
- Do NOT include analysis.
- Do NOT wrap JSON in markdown.
- Do NOT add text before or after JSON.
- Do NOT invent new fields.
- Maximum 5 violations.
- If more violations exist, return only the 5 most severe.
- Severity must be either CRITICAL or WARNING (no other values).

OFFICIAL RULES:
{retrieved_rules}

You must primarily evaluate against OFFICIAL RULES.
You may use general compliance reasoning if necessary.
Do NOT invent unrelated rules.

Required Output Format:

{{
  "compliance_results": [
    {{
      "category": "string",
      "severity": "CRITICAL | WARNING",
      "description": "string"
    }}
  ],
  "status": "PASS | FAIL",
  "final_report": "string"
}}

Decision Logic:
- If compliance_results is empty → status MUST be "PASS"
- If compliance_results is not empty → status MUST be "FAIL"
"""

        user_message = f"""
VIDEO METADATA:
{video_metadata}

TRANSCRIPT:
{transcript}

OCR TEXT:
{ocr_text}
"""

        
        #  Call Groq in JSON Mode
       

        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0,
            max_tokens=800,
            response_format={"type": "json_object"}  
        )

        content = response.choices[0].message.content.strip()

        print("\n===== RAW LLM RESPONSE =====")
        print(content)
        print("===== END RESPONSE =====\n")

        # Direct JSON parsing (safe because JSON mode)
        audit_data = json.loads(content)

        return {
            "compliance_issues": audit_data.get("compliance_results", []),
            "final_status": audit_data.get("status", "FAIL"),
            "final_report": audit_data.get("final_report", "No report generated")
        }

    except Exception as e:
        logger.error(f"[Node:Auditor] Failed: {str(e)}")
        return {
            "compliance_issues": [],
            "final_status": "FAIL",
            "final_report": f"Audit failed due to error: {str(e)}"
        }