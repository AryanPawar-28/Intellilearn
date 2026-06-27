import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")


client = Groq(api_key=api_key)




def generate_answer(question, context_chunks):


    context = "\n".join(context_chunks)


    prompt = f"""
You are an AI assistant answering questions based ONLY on the document context.


Context:
{context}


Question:
{question}


Answer clearly and accurately.
"""


    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile"
    )


    return chat_completion.choices[0].message.content


def generate_animation_script(context_chunks):


    context = "\n".join(context_chunks[:5])


    prompt = f"""
Explain this like a teacher speaking to a student.


Rules:
- Use simple, natural sentences
- No bullet points
- No symbols like * or -
- Make it sound like a real person talking
- Keep it engaging and short


Content:
{context}
"""


    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )


    return response.choices[0].message.content
