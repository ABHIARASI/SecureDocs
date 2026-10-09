from unittest.mock import patch

from fastapi.testclient import TestClient


def test_rejects_non_pdf_file(client: TestClient):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "notes.txt",
                b"This is a text file.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files are allowed"


def test_rejects_pdf_with_wrong_mime_type(client: TestClient):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "fake.pdf",
                b"%PDF-1.4 fake content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid file type. PDF files are required."
    )


def test_rejects_invalid_pdf_signature(client: TestClient):
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "fake.pdf",
                b"This is not a real PDF.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid PDF file"


def test_rejects_file_larger_than_10_mb(client: TestClient):
    oversized_content = b"%PDF-" + (
        b"A" * (10 * 1024 * 1024)
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "File size must be less than 10 MB"
    )


def test_rejects_pdf_without_extractable_text(
    client,
    db_session,
):
    from unittest.mock import patch
    from app.models.user import User

    # Create the user required by documents.user_id.
    test_user = User(
        id=1,
        email="upload-test@example.com",
        password_hash="test-hash",
        role="user",
    )
    db_session.add(test_user)
    db_session.commit()

    # Simulate a PDF from which no text can be extracted.
    with patch(
        "app.routers.documents.extract_text_from_pdf",
        return_value="   ",
    ) as mock_extract:
        response = client.post(
            "/documents/upload",
            files={
                "file": (
                    "empty.pdf",
                    b"%PDF-1.4 test content",
                    "application/pdf",
                )
            },
        )

    print("Response status:", response.status_code)
    print("Response body:", response.text)
    print("Extraction called:", mock_extract.called)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Could not extract text from PDF"
    )
    assert mock_extract.called