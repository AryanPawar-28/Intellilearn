import os
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")


client = Groq(api_key=api_key)




def generate_quiz(context_chunks, difficulty="Medium", num_questions=5):


    if not context_chunks:
        return None


    context = "\n".join(context_chunks[:5])


    prompt = f"""
You are an AI tutor creating MCQ quizzes.


Generate {num_questions} questions based on the context.


Difficulty: {difficulty}


Rules:
- Each question must have 4 options (A, B, C, D)
- Only ONE correct answer
- Provide explanation for correct answer
- Keep questions clear and exam-ready


STRICT FORMAT:


Q1: Question text
A) option
B) option
C) option
D) option
Answer: A
Explanation: explanation text


Q2: ...
...


Context:
{context}
"""


    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile"
    )


    return response.choices[0].message.content




def parse_quiz(quiz_text):


    if not quiz_text:
        return []


    questions = []


    blocks = quiz_text.split("\nQ")


    for block in blocks:
        block = block.strip()


        if not block:
            continue


        try:
            lines = [l.strip() for l in block.split("\n") if l.strip()]


            question = lines[0].split(":", 1)[1].strip()


            options = lines[1:5]


            answer_line = next(l for l in lines if l.startswith("Answer"))
            explanation_line = next(l for l in lines if l.startswith("Explanation"))


            answer_letter = answer_line.split(":")[1].strip()


            # map letter → full option
            answer = next(
                (opt for opt in options if opt.startswith(answer_letter)),
                answer_letter
            )


            explanation = explanation_line.split(":", 1)[1].strip()


            questions.append({
                "question": question,
                "options": options,
                "answer": answer,
                "explanation": explanation
            })


        except Exception:
            continue


    return questions
