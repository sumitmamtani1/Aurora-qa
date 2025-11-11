import re
from collections import defaultdict
from difflib import get_close_matches

TRIP_KEYWORDS = ["trip", "travel", "travelling", "traveling", "flight", "going to", "visit", "planning", "leave", "depart"]
CAR_KEYWORDS = ["car", "cars", "vehicle", "vehicles", "truck", "sedan", "SUV", "van"]
RESTAURANT_KEYWORDS = ["restaurant", "restaurants", "dinner", "lunch", "eat", "dine", "reservation", "reserve", "chef"]

WORD2NUM = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}

def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    return s

def flatten_message(m):
    """
    Given a message dict, return (author_name, text)
    - handle known API fields (user_name, message)
    - fallback: collect all string fields into text
    """
    if not isinstance(m, dict):
        return (None, "")
    author = None
    for f in ("user_name", "user", "author", "name", "member_name", "member"):
        v = m.get(f)
        if isinstance(v, str) and v.strip():
            author = v.strip()
            break
    text_candidates = []
    for f in ("message", "text", "body", "content", "payload"):
        v = m.get(f)
        if isinstance(v, str) and v.strip():
            text_candidates.append(v.strip())
    if not text_candidates:
        for k, v in m.items():
            if isinstance(v, str):
                text_candidates.append(v.strip())
    text = " ".join(text_candidates)
    return (author, normalize_text(text))

def find_candidate_names(messages):
    names = set()
    for m in messages:
        author, _ = flatten_message(m)
        if author:
            names.add(author)
    return sorted(names)

def normalize_name(n):
    return re.sub(r'[^a-z]', '', n.lower()) if n else ""

def find_best_name_match(query, names):
    """
    Flexible name matcher:
    - direct substring match (case-insensitive)
    - first-name or last-name token match
    - fuzzy match on normalized form
    """
    q = normalize_text(query).lower()
    for n in names:
        if n.lower() in q or n.lower().split()[0] in q:
            return n
    qtokens = re.findall(r"[A-Za-z']+", q)
    if qtokens:
        for t in qtokens:
            for n in names:
                if t.lower() == n.lower().split()[0]:
                    return n
    nmap = {normalize_name(n): n for n in names if n}
    qnorm = normalize_name("".join(qtokens))
    if qnorm:
        matches = get_close_matches(qnorm, nmap.keys(), n=1, cutoff=0.45)
        if matches:
            return nmap[matches[0]]
    return None

def extract_dates(text):
    patterns = [
        r'\b\d{4}-\d{2}-\d{2}\b',                          
        r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:,\s*\d{4})?\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b',
        r'\btomorrow\b|\bnext week\b|\bnext month\b|\bthis week\b|\bin \d+ days\b'
    ]
    found = []
    for p in patterns:
        for m in re.findall(p, text, flags=re.IGNORECASE):
            found.append(m)
    return found

def find_sentences_with_keywords(text, keywords):
    sents = re.split(r'(?<=[.!?])\s+', text)
    good = []
    for s in sents:
        for k in keywords:
            if re.search(r'\b' + re.escape(k) + r'\b', s, flags=re.IGNORECASE):
                good.append(s.strip())
                break
    return good

def extract_numbers_near_keyword(text, keywords):
    results = []
    for kw in keywords:
        pat1 = rf'(\d+|{"|".join(WORD2NUM.keys())})\s+(?:\w+\s){{0,3}}{kw}'
        for m in re.findall(pat1, text, flags=re.IGNORECASE):
            tok = m.lower()
            if tok.isdigit():
                results.append(int(tok))
            elif tok in WORD2NUM:
                results.append(WORD2NUM[tok])
        pat2 = rf'{kw}\s*[:\-]?\s*(\d+)'
        for m in re.findall(pat2, text, flags=re.IGNORECASE):
            results.append(int(m))
    return results

def extract_restaurant_names(sentence):
    names = set()
    qnames = re.findall(r'["“](.+?)["”]', sentence)
    for q in qnames:
        names.add(q.strip())
    atnames = re.findall(r'\bat\s+([A-Z][\w\s&\-\']{2,80})', sentence)
    for an in atnames:
        names.add(an.strip())
    return list(names)

def answer_question_from_messages(question, messages):
    member_texts = defaultdict(str)
    for m in messages:
        author, text = flatten_message(m)
        if author:
            member_texts[author] += " " + text
        else:
            member_texts["__GLOBAL__"] += " " + text

    names = find_candidate_names(messages)
    picked = find_best_name_match(question, names)

    lowq = normalize_text(question).lower()

    if any(w in lowq for w in ["trip", "travel", "flight", "going to", "depart", "leave", "visit"]):
        if picked:
            txt = member_texts.get(picked, "")
            dates = extract_dates(txt)
            sents = find_sentences_with_keywords(txt, TRIP_KEYWORDS)
            if dates:
                return f"{picked} mentioned trip date(s): {', '.join(dates)}."
            if sents:
                return f"{picked} mentioned travel: \"{sents[0]}\""
            return f"No explicit trip date found for {picked} in the messages."
        else:
            hits = []
            for name, txt in member_texts.items():
                if name == "__GLOBAL__": continue
                if any(k in txt.lower() for k in TRIP_KEYWORDS):
                    d = extract_dates(txt)
                    sents = find_sentences_with_keywords(txt, TRIP_KEYWORDS)
                    hits.append((name, d, sents))
            if hits:
                lines = []
                for h in hits[:6]:
                    n, d, s = h
                    if d:
                        lines.append(f"{n}: {', '.join(d)}")
                    elif s:
                        lines.append(f"{n}: {s[0]}")
                return " | ".join(lines)
            return "No trip planning info found in the dataset."
    if any(w in lowq for w in ["car", "cars", "vehicle", "vehicles", "owns", "own", "have a car", "have cars"]):
        def find_ownership_counts(text):
            counts = extract_numbers_near_keyword(text, CAR_KEYWORDS)
            if counts:
                return counts[0]
            ownership_pattern = re.search(r'\b(I|We|I\'ve|I have|I own|I had|I\'m)\b.*\b(' + '|'.join(CAR_KEYWORDS) + r')\b', text, flags=re.IGNORECASE)
            if ownership_pattern:
                num_word = re.search(r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b', text, flags=re.IGNORECASE)
                if num_word:
                    return WORD2NUM.get(num_word.group(1).lower())
                return 1
            return None

        if picked:
            txt = member_texts.get(picked, "")
            cnt = find_ownership_counts(txt)
            if cnt:
                return f"{picked} has {cnt} car(s) (in messages)."
            sents = find_sentences_with_keywords(txt, CAR_KEYWORDS)
            if sents:
                for s in sents:
                    if re.search(r'\b(I|We|I\'ve|I have|I own|my)\b', s, flags=re.IGNORECASE):
                        return f"{picked} indicates ownership/possession: \"{s}\" (no explicit count found)."
                return f"{picked} mentions cars (topic): \"{sents[0]}\""
            return f"No car information found for {picked}."
        else:
            ownership_hits = []
            topical_hits = []
            for name, txt in member_texts.items():
                if name == "__GLOBAL__": continue
                cnt = find_ownership_counts(txt)
                if cnt:
                    ownership_hits.append(f"{name}: {cnt}")
                else:
                    sents = find_sentences_with_keywords(txt, CAR_KEYWORDS)
                    if sents:
                        topical_hits.append(f"{name}: \"{sents[0]}\"")
            if ownership_hits:
                return " | ".join(ownership_hits[:8])
            if topical_hits:
                return " | ".join(topical_hits[:10])
            return "No car information found in the dataset."

    if any(w in lowq for w in ["restaurant", "restaurants", "dinner", "lunch", "eat", "dine", "reservation"]):
        if picked:
            txt = member_texts.get(picked, "")
            sents = find_sentences_with_keywords(txt, RESTAURANT_KEYWORDS)
            restaurants = []
            for s in sents:
                restaurants.extend(extract_restaurant_names(s))
            restaurants = list(dict.fromkeys([r for r in restaurants if r]))
            if restaurants:
                return f"{picked}'s mentioned restaurants: {', '.join(restaurants)}"
            if sents:
                return f"{picked} mentioned restaurants/food: \"{sents[0]}\""
            return f"No favorite-restaurant info found for {picked}."
        else:
            hits = []
            for name, txt in member_texts.items():
                if name == "__GLOBAL__": continue
                sents = find_sentences_with_keywords(txt, RESTAURANT_KEYWORDS)
                if sents:
                    names = []
                    for s in sents:
                        names.extend(extract_restaurant_names(s))
                    if names:
                        hits.append((name, list(dict.fromkeys(names))))
                    else:
                        hits.append((name, [sents[0]]))
            if hits:
                fragments = []
                for h in hits[:8]:
                    if isinstance(h[1], list):
                        fragments.append(f"{h[0]}: {', '.join(h[1])}")
                    else:
                        fragments.append(f"{h[0]}: \"{h[1]}\"")
                return " | ".join(fragments)
            return "No restaurant info found in the dataset."

    keywords = re.findall(r'\w+', lowq)
    best = None
    for name, txt in member_texts.items():
        if not txt: continue
        score = sum(1 for k in keywords if k in txt.lower())
        if score > 0 and (best is None or score > best[0]):
            sents = [s for s in re.split(r'(?<=[.!?])\s+', txt) if s.strip()]
            snippet = sents[0] if sents else txt[:160]
            best = (score, name, snippet)
    if best:
        return f"{best[1]}: \"{best[2]}\""
    return "I couldn't find an answer in the messages."
