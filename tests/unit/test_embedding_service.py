from unittest.mock import MagicMock
import pytest
from app.services.infrastructure.embeddings.service import EmbeddingService

@pytest.fixture
def reset_embedding_singleton():
    EmbeddingService._instance = None
    yield
    EmbeddingService._instance = None


def test_singleton_pattern(reset_embedding_singleton):
    service_a = EmbeddingService()
    service_b = EmbeddingService()
    assert service_a is service_b

def test_caching_same_text(reset_embedding_singleton):
    service = EmbeddingService(model_name="gemini")
    mock_provider = MagicMock()
    mock_provider.embed.return_value = [0.1, 0.2, 0.3]
    service._provider = mock_provider

    emb_a = service.embed_text("hello")
    emb_b = service.embed_text("hello")
    assert emb_a == emb_b
    assert mock_provider.embed.call_count == 1

def test_cosine_similarity_computation(reset_embedding_singleton):
    a = [1.0, 0.0, 0.0]
    b = [0.0, 1.0, 0.0]
    assert EmbeddingService.cosine_similarity(a, b) == 0.0

    c = [1.0, 1.0, 0.0]
    d = [1.0, 1.0, 0.0]
    assert abs(EmbeddingService.cosine_similarity(c, d) - 1.0) < 1e-9
