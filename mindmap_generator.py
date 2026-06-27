import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")

client = Groq(api_key=api_key)


def generate_mindmap_data(text_chunks, depth=3):
    """Generate a hierarchical mind map JSON from text chunks."""
    context = "\n\n".join(text_chunks[:6])
    context = context[:3500]  # Safety trim

    depth_instruction = {
        2: "2 levels deep: root → main topics only",
        3: "3 levels deep: root → main topics → subtopics",
        4: "4 levels deep: root → main topics → subtopics → details"
    }.get(depth, "3 levels deep: root → main topics → subtopics")

    prompt = f"""You are a knowledge mapping expert. Analyze the document and create a structured mind map.

Create a hierarchical mind map that is {depth_instruction}.

Return ONLY valid JSON, no markdown, no extra text, no code blocks.

The JSON must follow this exact structure:
{{
  "name": "Central Topic (short, 2-4 words)",
  "children": [
    {{
      "name": "Main Branch 1 (2-3 words)",
      "children": [
        {{
          "name": "Subtopic (2-4 words)",
          "children": []
        }}
      ]
    }}
  ]
}}

Rules:
- Node names must be SHORT (max 4-5 words)
- Root should have 4-7 main branches
- Each branch should have 2-5 children
- Extract the most important concepts
- No sentences, just key phrases
- Depth: {depth} levels maximum

Document:
{context}

Return the JSON mind map:"""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    return parse_mindmap(raw)


def parse_mindmap(raw_text):
    """Parse and validate the mind map JSON."""
    if not raw_text:
        return None

    text = raw_text.strip()

    # Strip code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].strip()

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None

    json_str = text[start:end+1]

    try:
        data = json.loads(json_str)
        # Ensure structure is valid
        if "name" not in data:
            return None
        if "children" not in data:
            data["children"] = []
        return _sanitize_node(data)
    except Exception:
        return None


def _sanitize_node(node):
    """Recursively ensure every node has 'name' and 'children'."""
    if not isinstance(node, dict):
        return {"name": str(node), "children": []}
    name = str(node.get("name", "Topic"))[:50]  # Cap length
    children = node.get("children", [])
    if not isinstance(children, list):
        children = []
    return {
        "name": name,
        "children": [_sanitize_node(c) for c in children]
    }