from app.database import SessionLocal
from app.models.chunk import DocumentChunk
from app.utils.embeddings import generate_embedding
from app.models.document import Document


db = SessionLocal()

text = "Operating systems manage computer hardware and software resources."

embedding = generate_embedding(text)

chunk = DocumentChunk(
    document_id=1,
    chunk_text=text,
    embedding=embedding
)

db.add(chunk)
db.commit()
db.refresh(chunk)

print("Chunk ID:", chunk.id)
print("Stored successfully!")

db.close()