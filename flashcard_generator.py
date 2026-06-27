import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)


def generate_flashcards(text_chunks, count=10, topic=""):
    """Generate flashcards from text chunks using Groq LLM."""
    # Use up to first 8 chunks to stay within token limits
    context = "\n\n".join(text_chunks[:8])
    context = context[:4000]  # Safety trim

    topic_line = f"Focus especially on the topic: {topic}." if topic else ""

    prompt = f"""You are an expert educator. Based on the following document content, generate exactly {count} high-quality flashcards for studying.
{topic_line}

Return ONLY a valid JSON array. Each object must have these exact keys:
- "front": the question or concept (clear and concise)
- "back": the complete answer or explanation
- "hint": a short hint (one phrase, can be empty string)

Rules:
- Questions must be specific and testable
- Answers must be complete and accurate
- No markdown, no extra text, just the JSON array
- Do NOT wrap in code blocks

Document Content:
{context}

Return exactly {count} flashcard objects in a JSON array:"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.4,
    )

    raw = response.choices[0].message.content.strip()
    return raw


def parse_flashcards(raw_text):
    """Parse the LLM response into a list of flashcard dicts."""
    if not raw_text:
        return []

    # Strip markdown code fences if present
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].strip()

    # Try to find JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return []

    json_str = text[start:end+1]

    try:
        cards = json.loads(json_str)
        # Validate structure
        valid = []
        for c in cards:
            if isinstance(c, dict) and "front" in c and "back" in c:
                valid.append({
                    "front": str(c.get("front", "")),
                    "back": str(c.get("back", "")),
                    "hint": str(c.get("hint", ""))
                })
        return valid
    except Exception:
        return []