# 🌌 Aurora-QA: Natural Language Question Answering API

_A lightweight Flask-based service that answers natural-language questions about member activity data fetched from a public API._

---

## 🚀 Overview

**Aurora-QA** is a simple, rule-based **Question Answering (QA)** service built using **Flask** and **Python**.  
It allows users to ask natural-language questions like:

- “When is Layla planning her trip to London?”
- “How many cars does Vikram Desai have?”
- “What are Amira’s favorite restaurants?”

The service infers answers from real messages fetched via the public API:

> 🛰️ **Public Data Source:** [https://november7-730026606190.europe-west1.run.app/messages](https://november7-730026606190.europe-west1.run.app/messages)

---

## ✨ Example Queries

| Example Question | Example Answer |
|------------------|----------------|
| “When is Layla planning her trip to London?” | `Layla Kawaguchi mentioned travel: "Please remember I prefer aisle seats during my flights."` |
| “How many cars does Vikram Desai have?” | `Vikram Desai mentions cars: "The car service was impeccable—thank you for your recommendation."` |
| “What are Amira’s favorite restaurants?” | `Amira Khan: The French Laundry, Le Bernardin` |

---

## 🧪 Example API Queries (with JSON Responses)

### 1️⃣ Layla’s Trip Query

**Request:**
GET https://aurora-qa.onrender.com/ask?q=When%20is%20Layla%20planning%20her%20trip%20to%20London


**Response:**
```json
{
  "answer": "Layla Kawaguchi mentioned travel: 'Please remember I prefer aisle seats during my flights.'"
}
2️⃣ Vikram’s Cars Query
Request:

GET https://aurora-qa.onrender.com/ask?q=How%20many%20cars%20does%20Vikram%20Desai%20have
Response:

{
  "answer": "Vikram Desai mentions cars: 'The car service was impeccable—thank you for your recommendation.'"
}
3️⃣ Amira’s Favorite Restaurants
Request:

GET https://aurora-qa.onrender.com/ask?q=What%20are%20Amira%27s%20favorite%20restaurants
Response:


{
  "answer": "Amira Khan: The French Laundry, Le Bernardin"
}
⚙️ Setup & Run Instructions
🧩 Prerequisites
Python 3.9+

pip installed

Internet connection (to access the public API)


# 1. Clone the repository
git clone https://github.com/sumitmamtani1/Aurora-qa.git
cd Aurora-qa

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the Flask server
python app.py
Once running, visit:
👉 http://127.0.0.1:8080/ask?q=When%20is%20Layla%20planning%20her%20trip%20to%20London

Response:

{"answer": "Layla Kawaguchi mentioned travel: 'Please remember I prefer aisle seats during my flights.'"}
🐳 Run via Docker

# Build image
docker build -t aurora-qa .

# Run container
docker run -p 8080:8080 -e MESSAGES_API_URL="https://november7-730026606190.europe-west1.run.app/messages" aurora-qa
Then open in your browser:


http://127.0.0.1:8080/ask?q=What%20are%20Amira%27s%20favorite%20restaurants
☁️ Deploy to Render (Free Cloud Hosting)
Push this repo to GitHub.

Go to https://render.com → New Web Service.

Connect your GitHub repo Aurora-qa.

Render auto-detects your Dockerfile.

Add environment variable:

MESSAGES_API_URL=https://november7-730026606190.europe-west1.run.app/messages
Click Deploy — wait for build & deploy to complete.

Test your endpoint:


https://aurora-qa.onrender.com/ask?q=When%20is%20Layla%20planning%20her%20trip%20to%20London
🧠 How It Works
The /ask endpoint receives a user question.

The system fetches all member messages from the public API.

It parses text using keyword extraction, regex, and fuzzy name matching.

Based on detected intent (e.g., travel, restaurants, cars), it constructs an inferred answer.

Returns a concise JSON response.

🧩 API Endpoints
Method	Endpoint	Description
GET	/ask?q=<question>	Returns a JSON answer inferred from messages
GET	/health	Health check endpoint

Example Response:

{ "answer": "Layla Kawaguchi mentioned travel: 'Please remember I prefer aisle seats during my flights.'" }
💡 Alternative Approaches Considered
1️⃣ Rule-Based Parsing (Chosen Approach)
Lightweight, explainable, and fast.

Uses regex and fuzzy matching to extract relevant text segments.

Detects structured entities like names, dates, numbers, and keywords.

Simple, interpretable, and easy to maintain.

✅ Pros: Deterministic and transparent
⚠️ Cons: Requires specific phrasing; limited flexibility

2️⃣ Embedding-Based Semantic Search
Uses embeddings (e.g., Sentence-BERT) to match queries with semantically similar messages.

Converts messages into vector embeddings and retrieves the top similar ones.

Understands synonyms and paraphrases.

✅ Pros: Handles natural phrasing
⚠️ Cons: Requires vector DB (e.g., FAISS, Pinecone); adds latency

3️⃣ Prompt-Based LLM Reasoning
Integrates an LLM (e.g., GPT-3.5) to reason over the message dataset.

Sends relevant messages + question to a language model for natural reasoning.

Returns human-like, context-aware answers.

✅ Pros: Very flexible and natural
⚠️ Cons: Non-deterministic, slower, requires API cost

4️⃣ Hybrid (Semantic + Rule-Based) Approach
Combines semantic retrieval with structured extraction.

Embedding retrieval for candidate messages

Regex-based parsing for final structured answer

✅ Pros: High accuracy and interpretability
⚠️ Cons: More complex architecture

🔍 Bonus: Data Insights
Insight	Observation
🕑 Dataset Size	~3,349 messages retrieved from the public API.
👤 Top Members	Layla Kawaguchi, Vikram Desai, Sophia Al-Farsi, Hans Müller.
🍽️ Restaurant Mentions	Common: The French Laundry, Le Bernardin, Nobu.
🚗 Car Mentions	Many reference “car service” — not ownership, requiring nuanced handling.
🧳 Travel Patterns	Frequent destinations include London, Paris, Monaco, Bangkok.

🧭 Future Enhancements
Add semantic retrieval for natural query flexibility

Integrate LLM fallback for complex reasoning

Cache data for faster response time

Add interactive frontend visualization

👨‍💻 Author
Sumit Mamtani
⭐ If you found this project useful, please star the repository! ⭐
