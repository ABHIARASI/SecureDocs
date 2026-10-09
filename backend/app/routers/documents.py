import os
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.auth import get_current_user_id

from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.chunker import chunk_text
from app.utils.embeddings import generate_embedding


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    # 1. Check file extension
    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    if file_extension != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. Check MIME type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. PDF files are required."
        )

    # 3. Read file content
    file_content = file.file.read()

    # 4. Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10 MB"
        )

    # 5. Verify PDF signature
    if not file_content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    try:
        # 6. Save PDF
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

        # 7. Create document record
        document = Document(
            user_id=user_id,
            filename=file.filename,
            file_path=file_path
        )

        db.add(document)

        # Get document ID without committing yet
        db.flush()

        # 8. Extract text
        extracted_text = extract_text_from_pdf(
            file_path
        )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # 9. Split into chunks
        chunks = chunk_text(
            extracted_text
        )

        # 10. Generate and store embeddings
        for chunk in chunks:

            embedding = generate_embedding(
                chunk
            )

            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_text=chunk,
                embedding=embedding
            )

            db.add(document_chunk)

        # 11. Commit everything together
        db.commit()

        return {
            "id": document.id,
            "filename": document.filename,
            "chunks_created": len(chunks),
            "message": "Document uploaded and processed successfully"
        }

    except HTTPException:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise

    except Exception as e:
        db.rollback()

        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


@router.get("/")
def get_documents(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    documents = db.query(Document).filter(
        Document.user_id == user_id
    ).all()

    return documents


@router.get("/{document_id}")
def get_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    # Delete all chunks belonging to this document
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete(
        synchronize_session=False
    )

    # Delete the physical PDF
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    # Delete the document record
    db.delete(document)

    db.commit()

    return {
        "message": "Document and associated chunks deleted successfully"
    }