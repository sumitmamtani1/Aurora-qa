# Member Q&A Service

A small question-answering microservice that answers natural-language questions about members from a public messages API.

Endpoint:
- `GET /ask?q=What%20is%20Layla%20planning%20for%20London%3F`
  - Response: `{ "answer": "..." }`

Environment:
- `MESSAGES_API_URL` — URL for the messages JSON endpoint (defaults to `https://november7-730026606190.europe-west1.run.app/messages`).

## How it works (short)
1. The service fetches messages from `MESSAGES_API_URL`.
2. It maps messages to member buckets (by author/name field).
3. It runs a small rule-based extractor to find dates, numbers, and entity mentions (restaurants, cars, trips).
4. It returns a short human-readable answer.

## Run locally
1. Clone repo
2. (Optional) create and activate virtualenv
3. Install:
   ```bash
   pip install -r requirements.txt
