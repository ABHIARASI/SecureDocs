import time
from app.utils.llm import client

start = time.perf_counter()

print("Sending test request to Gemini...")

try:
    response = client.interactions.create(
        model="gemini-3.5-flash-lite",
        input="Reply with exactly: Hello"
    )
    print("Response:", response.output_text)
except Exception as error:
    print("Error:", repr(error))
finally:
    print("Total time:", round(time.perf_counter() - start, 2), "seconds")