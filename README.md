## AI Video Compliance Audit Pipeline

An end-to-end RAG-powered AI system that audits YouTube videos for FTC-style compliance violations using:

 * Whisper (Speech-to-Text)

 * FAISS (Vector Database)

 * HuggingFace Embeddings

 * LangGraph (Workflow Orchestration)

 * Groq LLM (Structured JSON Output)

This system automatically downloads a YouTube video, transcribes it, retrieves relevant compliance rules, and generates a structured compliance audit report.

###  What This Project Does

1- Accepts a YouTube video URL

2- Downloads the video locally

3- Transcribes speech using Whisper

4- Retrieves relevant compliance rules using FAISS (RAG)

5- Evaluates transcript using Groq LLM in strict JSON mode

6- Returns:

 * Compliance violations (if any)

 * Severity level (CRITICAL / WARNING)

 * Final PASS / FAIL status

 * Structured final summary

### Architecture Overview

<img width="374" height="322" alt="image" src="https://github.com/user-attachments/assets/349aea63-a983-4909-8420-e905c3736bab" />

### Key Concepts Used

-Retrieval-Augmented Generation (RAG)

-Vector Search with FAISS

-Whisper-based Speech Recognition

-Structured LLM JSON Outputs

-LangGraph DAG-based orchestration

-Local-first AI pipeline design

### Project Structure
<img width="387" height="408" alt="image" src="https://github.com/user-attachments/assets/b1b72a21-de59-4a72-8714-cf8179016dd9" />

### Sample Output
<img width="630" height="239" alt="image" src="https://github.com/user-attachments/assets/24600e1e-99ba-41ca-9811-713d1a994501" />

### Technologies Used

* Python

* Whisper

* yt-dlp

* FAISS

* Sentence Transformers (MiniLM)

* Groq LLM API

* LangGraph

* dotenv

###  Deployment Ready

This system is fully modular and ready for Azure deployment, including:

* Azure OpenAI / Groq API swap

* Azure Blob Storage for video storage

* Azure AI Search for vector DB

* Azure Functions / App Service hosting



###Deployed on StreamLit
<img width="1913" height="767" alt="image" src="https://github.com/user-attachments/assets/330edf6c-4977-4ee5-9897-3f1da8bae703" />
<img width="1427" height="761" alt="image" src="https://github.com/user-attachments/assets/6ddc972a-881e-4fba-a7ea-450c30e993b1" />



###  Author

Built as a complete local-first AI compliance orchestration system combining RAG, speech processing, and structured LLM reasoning.

