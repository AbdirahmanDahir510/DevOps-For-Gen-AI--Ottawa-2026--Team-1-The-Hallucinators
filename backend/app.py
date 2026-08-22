"""
Sample RAG chatbot API — AWS BEDROCK VERSION.

Same logic as app.py, but calls Claude through AWS Bedrock instead of
a local Ollama model or the direct Anthropic API. Use this once the
team has AWS credentials/credits set up.

Setup:
  1. pip install -r requirements-bedrock.txt
  2. Configure AWS credentials one of these ways:
     - Run `aws configure` in the terminal (needs AWS CLI installed), or
     - Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
       AWS_SESSION_TOKEN (if using temporary/hackathon-issued credentials)
  3. Model ID and region are already set below (Claude Sonnet 4.5, us-east-2),
     confirmed working in the Bedrock console. Only change these if your
     teammate's AWS account has different model access enabled.
  4. Run with: uvicorn app_bedrock:app --reload --port 8000

If you get an "AccessDeniedException" error, it usually means the model
isn't enabled yet in that AWS account/region, or your credentials don't
have bedrock:InvokeModel permission.
"""

import os
import json
import boto3
from fastapi import FastAPI
from pydantic import BaseModel

from retrieve import retrieve

app = FastAPI(title="Sample RAG Chatbot (AWS Bedrock)")

# Update this to match the exact model ID enabled in your Bedrock account
MODEL_ID = "anthropic.claude-sonnet-4-5-20250929-v1:0"
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION)


class Question(BaseModel):
    question: str
    top_k: int = 3


class Answer(BaseModel):
    answer: str
    retrieved_chunks: list


@app.post("/ask", response_model=Answer)
def ask(payload: Question):
    chunks = retrieve(payload.question, top_k=payload.top_k)

    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    )

    prompt = f"""You are a helpful assistant. Answer the question using ONLY
the context below. If the answer is not in the context, say you don't know.

Context:
{context}

Question: {payload.question}

Answer:"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    })

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    response_body = json.loads(response["body"].read())
    answer_text = response_body["content"][0]["text"]

    return Answer(answer=answer_text, retrieved_chunks=chunks)


@app.get("/health")
def health():
    return {"status": "ok"}
