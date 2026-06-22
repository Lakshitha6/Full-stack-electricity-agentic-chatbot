import pytest
import httpx
from src.utils.config_loader import get_env, load_yaml


@pytest.mark.asyncio
async def test_gemini_embedding_model_exists():
    """Verify the embedding model is accessible and returns valid structure"""
    config = load_yaml("llm.yaml")["providers"]["primary"]
    api_key = get_env(config["api_key_env"])
    embedding_model = config.get("embedding_model", "text-embedding-004")
    
    assert api_key, "GEMINI_API_KEY must be set in .env"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{embedding_model}:embedContent?key={api_key}"
    payload = {"content": {"parts": [{"text": "test"}]}}
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
    
    # Assert model exists and responds
    assert resp.status_code != 404, f"Embedding model '{embedding_model}' not found. Try 'text-embedding-004'"
    resp.raise_for_status()
    
    data = resp.json()
    assert "embedding" in data, "Response missing 'embedding' field"
    assert "values" in data["embedding"], "Embedding missing 'values' array"


@pytest.mark.asyncio
async def test_gemini_embedding_dimensions():
    """Verify embeddings have expected dimensionality (768 for text-embedding-004)"""
    config = load_yaml("llm.yaml")["providers"]["primary"]
    api_key = get_env(config["api_key_env"])
    embedding_model = config.get("embedding_model", "text-embedding-004")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{embedding_model}:embedContent?key={api_key}"
    payload = {"content": {"parts": [{"text": "Electricity bill payment reminder"}]}}
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
    
    data = resp.json()
    embedding = data["embedding"]["values"]
    
    # Gemini embeddings are typically 768 dimensions
    assert isinstance(embedding, list), "Embedding should be a list of floats"
    assert len(embedding) > 0, "Embedding should not be empty"
    assert all(isinstance(v, (int, float)) for v in embedding), "All embedding values should be numeric"
    
    # Optional: check expected dimension (relax for different models)
    expected_dims = [768, 1536, 3072]  # Common embedding sizes
    assert len(embedding) in expected_dims, f"Unexpected embedding dimension: {len(embedding)}. Expected one of {expected_dims}"


@pytest.mark.asyncio
@pytest.mark.parametrize("test_text,description", [
    ("I prefer concise bill summaries", "user preference: concise"),
    ("Show me usage trends for winter months", "query about seasonal usage"),
    ("Alert me before due dates", "preference for proactive alerts"),
    ("Why is my balance higher this month?", "billing inquiry"),
])
async def test_gemini_embedding_semantic_quality(test_text: str, description: str):
    """Verify embeddings capture semantic meaning (basic sanity check)"""
    config = load_yaml("llm.yaml")["providers"]["primary"]
    api_key = get_env(config["api_key_env"])
    embedding_model = config.get("embedding_model", "text-embedding-004")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{embedding_model}:embedContent?key={api_key}"
    payload = {"content": {"parts": [{"text": test_text}]}}
    
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
    
    data = resp.json()
    embedding = data["embedding"]["values"]
    
    # Basic quality checks
    assert len(embedding) > 100, f"Embedding too short for '{description}'"
    
    # Check variance (all zeros = bad embedding)
    variance = sum((v - sum(embedding)/len(embedding))**2 for v in embedding) / len(embedding)
    assert variance > 1e-6, f"Embedding has near-zero variance for '{description}' — may be degenerate"
    
    # Log for debugging (pytest -s shows prints)
    print(f"\n✅ '{description}': dim={len(embedding)}, variance={variance:.6f}")


@pytest.mark.asyncio
async def test_embedding_consistency():
    """Same text should produce nearly identical embeddings (deterministic within tolerance)"""
    config = load_yaml("llm.yaml")["providers"]["primary"]
    api_key = get_env(config["api_key_env"])
    embedding_model = config.get("embedding_model", "text-embedding-004")
    
    test_text = "Electricity usage analysis for March 2024"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{embedding_model}:embedContent?key={api_key}"
    payload = {"content": {"parts": [{"text": test_text}]}}
    
    embeddings = []
    async with httpx.AsyncClient(timeout=15) as client:
        for _ in range(2):  # Request twice
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            embeddings.append(data["embedding"]["values"])
    
    # Compute cosine similarity
    import math
    def cosine_sim(a, b):
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0
    
    similarity = cosine_sim(embeddings[0], embeddings[1])
    
    # Gemini embeddings should be nearly identical (allow tiny floating-point drift)
    assert similarity > 0.9999, f"Embeddings not consistent: cosine similarity = {similarity}"
    print(f"\n Embedding consistency: cosine similarity = {similarity:.6f}")