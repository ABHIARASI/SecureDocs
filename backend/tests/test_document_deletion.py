
import os
from unittest.mock import patch

from app.models.document import Document
from app.models.chunk import DocumentChunk


def test_delete_removes_document_record(
    client,
    db_session,
    two_users_and_documents,
):
    alice_id = two_users_and_documents["alice"]

    response = client.delete(f"/documents/{alice_id}")

    assert response.status_code == 200

    deleted_document = db_session.query(Document).filter(
        Document.id == alice_id
    ).first()

    assert deleted_document is None


def test_delete_removes_document_chunks(
    client,
    db_session,
    two_users_and_documents,
):
    alice_id = two_users_and_documents["alice"]

    chunk = DocumentChunk(
        document_id=alice_id,
        chunk_text="Test content for deletion.",
        embedding=[1.0] + [0.0] * 383,
    )

    db_session.add(chunk)
    db_session.commit()

    response = client.delete(f"/documents/{alice_id}")

    assert response.status_code == 200

    remaining_chunks = db_session.query(DocumentChunk).filter(
        DocumentChunk.document_id == alice_id
    ).count()

    assert remaining_chunks == 0


def test_delete_removes_physical_pdf(
    client,
    db_session,
    two_users_and_documents,
    tmp_path,
):
    alice_id = two_users_and_documents["alice"]
    pdf_path = tmp_path / "alice-test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    document = db_session.query(Document).filter(
        Document.id == alice_id
    ).first()

    document.file_path = str(pdf_path)
    db_session.commit()

    response = client.delete(f"/documents/{alice_id}")

    assert response.status_code == 200
    assert not os.path.exists(pdf_path)


def test_delete_does_not_remove_another_users_document(
    client,
    db_session,
    two_users_and_documents,
):
    bob_id = two_users_and_documents["bob"]

    with patch(
        "app.routers.documents.os.path.exists",
        return_value=False,
    ):
        response = client.delete(f"/documents/{bob_id}")

    assert response.status_code == 404

    bob_document = db_session.query(Document).filter(
        Document.id == bob_id
    ).first()

    assert bob_document is not None
