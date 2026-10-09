
from unittest.mock import patch

from app.models.document import Document


def test_user_sees_only_own_documents(
    client,
    two_users_and_documents,
):
    response = client.get("/documents/")

    assert response.status_code == 200

    filenames = [
        document["filename"]
        for document in response.json()
    ]

    assert "alice.pdf" in filenames
    assert "bob.pdf" not in filenames


def test_user_cannot_access_another_users_document(
    client,
    two_users_and_documents,
):
    bob_document_id = two_users_and_documents["bob"]

    response = client.get(
        f"/documents/{bob_document_id}"
    )

    assert response.status_code == 404


def test_user_cannot_delete_another_users_document(
    client,
    two_users_and_documents,
):
    bob_document_id = two_users_and_documents["bob"]

    with patch(
        "app.routers.documents.os.path.exists",
        return_value=False,
    ):
        response = client.delete(
            f"/documents/{bob_document_id}"
        )

    assert response.status_code == 404

    document = (
        client.app.dependency_overrides
    )

    assert document is not None

def test_search_only_returns_current_users_documents(
    client,
    db_session,
    two_users_and_documents,
):
    from app.models.chunk import DocumentChunk

    alice_id = two_users_and_documents["alice"]
    bob_id = two_users_and_documents["bob"]

    # Create one searchable chunk for each user.
    alice_chunk = DocumentChunk(
        document_id=alice_id,
        chunk_text="Solar panels convert sunlight into electricity.",
        embedding=[1.0] + [0.0] * 383,
    )

    bob_chunk = DocumentChunk(
        document_id=bob_id,
        chunk_text="Bob's confidential financial information.",
        embedding=[1.0] + [0.0] * 383,
    )

    db_session.add_all([alice_chunk, bob_chunk])
    db_session.commit()

    # Avoid external embedding and Gemini API calls.
    from unittest.mock import patch

    with (
        patch(
            "app.routers.search.generate_embedding",
            return_value=[1.0] + [0.0] * 383,
        ),
        patch(
            "app.routers.search.generate_answer",
            return_value="Solar panels convert sunlight into electricity.",
        ),
    ):
        response = client.post(
            "/search/",
            json={"query": "How do solar panels work?"},
        )

    assert response.status_code == 200

    result = response.json()
    source_documents = [
        source["document"]
        for source in result["sources"]
    ]

    assert "alice.pdf" in source_documents
    assert "bob.pdf" not in source_documents
