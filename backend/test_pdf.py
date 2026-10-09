from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.chunker import chunk_text

file_path = "uploads/573233c9-e8c8-44c1-9a14-d9cc1c3aaa18.pdf"

text = extract_text_from_pdf(file_path)

chunks = chunk_text(text)

print("Total chunks:", len(chunks))

for i, chunk in enumerate(chunks[:5]):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk)