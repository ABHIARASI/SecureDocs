
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_answer(question: str, context: str) -> str:
    prompt = f"""
You are a helpful assistant that answers questions about uploaded documents.

Instructions:
1. Use the provided context as your source of information.
2. Answer direct questions using facts explicitly stated in the context.
3. You may make reasonable inferences when the context supports them.
4. When making an inference, explain it as a likely outcome,
   not as a confirmed fact.
5. Do not invent details or use outside knowledge.
6. If relevant information is available but the answer is not
   stated directly, use that information to form a cautious inference.
7. Only say "I couldn't find that information in the uploaded documents."
   when the context contains no relevant information to answer the question.
8. Keep answers concise and clear.

Context:
{context}

Question:
{question}

Answer:
"""

    interaction = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    return interaction.output_text
