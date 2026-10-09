from app.utils.embeddings import generate_embedding

text = "Operating systems manage computer hardware and software resources."

embedding = generate_embedding(text)

print("Embedding length:", len(embedding))
print("First 10 values:", embedding[:10])