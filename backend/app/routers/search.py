
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user_id
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.schemas.search import SearchRequest
from app.utils.embeddings import generate_embedding
from app.utils.llm import generate_answer


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

# Initial tuning values; we'll validate these using your test PDFs.
CANDIDATE_LIMIT = 20
MAX_RESULTS = 5
MIN_SIMILARITY = 0.35


@router.post("/")
def search_documents(
    request: SearchRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Step 1: Generate the question embedding
    start = time.perf_counter()
    query_embedding = generate_embedding(request.query)

    print(
        "Embedding:",
        round(time.perf_counter() - start, 2),
        "sec"
    )

    # Step 2: Retrieve the closest candidate chunks
    db_start = time.perf_counter()

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    candidates = (
        db.query(
            DocumentChunk,
            Document.filename,
            Document.id.label("document_id"),
            distance.label("distance")
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id
        )
        .filter(
            Document.user_id == user_id
        )
        .order_by(distance)
        .limit(CANDIDATE_LIMIT)
        .all()
    )

    print(
        "Database:",
        round(time.perf_counter() - db_start, 2),
        "sec"
    )

    # Step 3: Filter candidates by similarity
    relevant_candidates = []

    for result in candidates:
        chunk, filename, document_id, distance_value = result
        similarity = 1 - float(distance_value)

        if similarity >= MIN_SIMILARITY:
            relevant_candidates.append(result)

    # Step 4: Select relevant chunks while encouraging diversity
    results = []
    seen_documents = set()

    # First pass: select the best chunk from each document.
    for result in relevant_candidates:
        chunk, filename, document_id, distance_value = result

        if document_id not in seen_documents:
            results.append(result)
            seen_documents.add(document_id)

        if len(results) >= MAX_RESULTS:
            break

    # Second pass: if there are fewer than five documents,
    # allow additional relevant chunks from the same documents.
    if len(results) < MAX_RESULTS:
        selected_chunk_ids = {
            result[0].id for result in results
        }

        for result in relevant_candidates:
            chunk, filename, document_id, distance_value = result

            if chunk.id not in selected_chunk_ids:
                results.append(result)
                selected_chunk_ids.add(chunk.id)

            if len(results) >= MAX_RESULTS:
                break

    print("Candidate chunks:", len(candidates))
    print("Relevant chunks:", len(relevant_candidates))
    print("Selected chunks:", len(results))

    # Step 5: Handle cases with no sufficiently relevant matches
    if not results:
        return {
            "answer": (
                "I couldn't find sufficiently relevant information "
                "in the uploaded documents."
            ),
            "sources": []
        }

    # Step 6: Build context for Gemini
    context_parts = []

    for chunk, filename, document_id, distance_value in results:
        context_parts.append(
            f"Document: {filename}\n"
            f"Content: {chunk.chunk_text}"
        )

    context = "\n\n---\n\n".join(context_parts)

    print("Context characters:", len(context))
    print("Context words:", len(context.split()))

    # Step 7: Generate the answer
    llm_start = time.perf_counter()

    answer = generate_answer(
        question=request.query,
        context=context
    )

    print(
        "Gemini:",
        round(time.perf_counter() - llm_start, 2),
        "sec"
    )

    # Step 8: Return source metadata
    sources = []

    for chunk, filename, document_id, distance_value in results:
        similarity = 1 - float(distance_value)

        sources.append({
            "document_id": document_id,
            "document": filename,
            "chunk_id": chunk.id,
            "similarity": round(similarity, 4),
            "chunk": chunk.chunk_text
        })

    return {
        "answer": answer,
        "sources": sources
    }
