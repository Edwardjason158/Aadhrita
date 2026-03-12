import spacy
from collections import Counter

# Load model once at startup
nlp = spacy.load("en_core_web_sm")

# Health-domain keyword lists
SYMPTOM_KEYWORDS = {
    "headache", "migraine", "pain", "fatigue", "tired", "exhausted",
    "dizzy", "nausea", "vomiting", "fever", "cough", "cold", "flu",
    "anxiety", "depressed", "stressed", "overwhelmed", "insomnia",
    "breathless", "chest pain", "backache", "cramps", "sore", "ache",
    "bloated", "constipated", "diarrhea", "allergies", "rash"
}

POSITIVE_MOOD = {
    "great", "good", "excellent", "happy", "energetic", "refreshed",
    "calm", "relaxed", "motivated", "productive", "focused", "better",
    "wonderful", "fantastic", "positive", "cheerful", "rested", "strong"
}

NEGATIVE_MOOD = {
    "bad", "terrible", "awful", "sad", "depressed", "anxious", "stressed",
    "tired", "exhausted", "drained", "down", "gloomy", "irritable",
    "frustrated", "worried", "overwhelmed", "sluggish", "weak"
}

ACTIVITY_KEYWORDS = {
    "walked", "ran", "jogged", "exercised", "gym", "yoga", "meditated",
    "swam", "cycled", "hiked", "stretching", "workout", "dancing",
    "tennis", "football", "basketball", "sports", "played"
}

FOOD_KEYWORDS = {
    "ate", "eaten", "drank", "drink", "meal", "breakfast", "lunch",
    "dinner", "snack", "calories", "protein", "vegetables", "fruits",
    "sugar", "coffee", "water", "hydrated", "junk", "healthy"
}


def analyze_health_text(text: str) -> dict:
    doc = nlp(text.lower())

    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and len(token.text) > 2]
    token_set = set(tokens)

    # Named entities (people, places, orgs — medical context)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

    # Keyword matching
    symptoms = sorted(token_set & SYMPTOM_KEYWORDS)
    positive_mood = sorted(token_set & POSITIVE_MOOD)
    negative_mood = sorted(token_set & NEGATIVE_MOOD)
    activities = sorted(token_set & ACTIVITY_KEYWORDS)
    food_notes = sorted(token_set & FOOD_KEYWORDS)

    # Mood score (-10 to +10)
    mood_score = len(positive_mood) - len(negative_mood)
    if mood_score > 0:
        mood = "Positive 😊"
    elif mood_score < 0:
        mood = "Negative 😔"
    else:
        mood = "Neutral 😐"

    # Top keywords (non-stopword, non-punct, high frequency)
    word_freq = Counter(tokens)
    top_keywords = [word for word, _ in word_freq.most_common(8)]

    # Generate advice based on findings
    advice = []
    if symptoms:
        advice.append(f"Symptoms detected: {', '.join(symptoms)}. Consider consulting a healthcare provider if persistent.")
    if negative_mood and not positive_mood:
        advice.append("Your note reflects a low mood. Consider light exercise, rest, or talking to someone.")
    if "stress" in token_set or "anxious" in token_set or "overwhelmed" in token_set:
        advice.append("Stress indicators found. Try 5-10 minutes of deep breathing or meditation.")
    if activities:
        advice.append(f"Great job staying active! Activities mentioned: {', '.join(activities)}.")
    if not activities and not symptoms:
        advice.append("Consider logging your physical activities for better health tracking.")

    return {
        "mood": mood,
        "mood_score": mood_score,
        "symptoms": symptoms,
        "positive_signals": positive_mood,
        "negative_signals": negative_mood,
        "activities": activities,
        "food_notes": food_notes,
        "top_keywords": top_keywords,
        "entities": entities,
        "advice": advice,
        "word_count": len([t for t in doc if not t.is_space])
    }
