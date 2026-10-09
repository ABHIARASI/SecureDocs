
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_protected_documents_reject_missing_token():
    response = client.get("/documents/")

    assert response.status_code in (401, 403)


def test_protected_search_rejects_missing_token():
    response = client.post(
        "/search/",
        json={"query": "How do solar panels work?"}
    )

    assert response.status_code in (401, 403)
