# fetch_messages.py
import requests, json, sys

URL = "https://november7-730026606190.europe-west1.run.app/messages"
try:
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    data = r.json()
except Exception as e:
    print("Failed to fetch:", e)
    sys.exit(1)

# Inspect top-level keys
print("Top-level type:", type(data))
if isinstance(data, dict):
    print("Top-level keys:", list(data.keys()))

# Try to get messages list
if isinstance(data, dict) and "messages" in data:
    messages = data["messages"]
elif isinstance(data, list):
    messages = data
else:
    print("❌ Unexpected structure:")
    print(json.dumps(data, indent=2))
    sys.exit(1)

print("Total messages:", len(messages))
print("First 2 messages:")
print(json.dumps(messages[:2], indent=2, ensure_ascii=False))
