# inspect_messages.py  — robust, prints status & errors
import sys, json, traceback

URL = "https://november7-730026606190.europe-west1.run.app/messages"

try:
    import requests
except Exception as e:
    print("ERROR: 'requests' library not available.", e)
    print("Install it with: py -3 -m pip install requests")
    sys.exit(2)

try:
    print("Requesting:", URL)
    r = requests.get(URL, timeout=20)
    print("HTTP status:", r.status_code)
    # show content length (bytes)
    content_bytes = len(r.content) if r.content is not None else 0
    print("Response bytes:", content_bytes)
    try:
        data = r.json()
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Raw response (first 1000 chars):")
        print(r.text[:1000])
        sys.exit(3)

    print("Top-level type:", type(data))
    if isinstance(data, dict):
        print("Top-level keys:", list(data.keys()))
    # determine messages list
    if isinstance(data, dict) and "messages" in data:
        msgs = data["messages"]
    elif isinstance(data, list):
        msgs = data
    else:
        print("Unexpected top-level structure. Dumping top-level (brief):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
        sys.exit(4)

    print("Total messages:", len(msgs))
    if len(msgs) >= 1:
        print("\n--- Message 0 ---")
        print(json.dumps(msgs[0], indent=2, ensure_ascii=False))
    if len(msgs) >= 2:
        print("\n--- Message 1 ---")
        print(json.dumps(msgs[1], indent=2, ensure_ascii=False))
    if len(msgs) >= 3:
        print("\n--- Message 2 ---")
        print(json.dumps(msgs[2], indent=2, ensure_ascii=False))

    # quick author summary
    from collections import Counter
    authors = Counter()
    for m in msgs:
        name = None
        for f in ("author","name","member","user","member_name"):
            v = m.get(f) if isinstance(m, dict) else None
            if v:
                name = v
                break
        authors[name or "UNKNOWN"] += 1
    print("\nTop authors (10):")
    for a,c in authors.most_common(10):
        print(a, c)

except Exception:
    print("Unhandled exception:")
    traceback.print_exc()
    sys.exit(99)
