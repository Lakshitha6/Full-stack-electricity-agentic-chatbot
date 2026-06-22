import asyncio
import os
from src.utils.llm_router import llm_router
import pytest

@pytest.mark.asyncio
async def test_primary_provider():
    """Test that at least one provider returns a valid response"""
    response = await llm_router.chat_completion(
        prompt="What is 2+2? Answer in one word.",
        system_prompt="You are a helpful assistant."
    )
    
    assert response, "Response should not be empty"
    assert f"Expected response: {response}"
    print(f" Response: {response}")

@pytest.mark.asyncio
async def test_fallback_mechanism():
    """Test that fallback activates on primary failure"""
    import os
    from unittest.mock import patch, AsyncMock
    
    # Mock Gemini to always fail
    async def mock_gemini_fail(*args, **kwargs):
        from httpx import HTTPStatusError
        raise HTTPStatusError("Simulated failure", request=None, response=type('obj', (object,), {'status_code': 429})())
    
    with patch.object(llm_router, '_call_gemini', side_effect=mock_gemini_fail):
        response = await llm_router.chat_completion(
            prompt="What is the capital of France? One word.",
            system_prompt="You are helpful."
        )
        
        assert response, "Fallback should return a response"
        assert "paris" in response.lower(), f"Expected 'Paris', got: {response}"
        print(f" Fallback worked: {response}")

async def main():
    print("🔌 Testing LLM Router...\n")
    
    # Test 1: Primary (Gemini)
    print("1️ Testing primary provider (Gemini)...")
    primary_ok = await test_primary_provider()
    
    # Test 2: Fallback (Groq)
    print("\n2️ Testing fallback provider (Groq)...")
    fallback_ok = await test_fallback_mechanism()
    
    # Summary
    print(f"\n Results:")
    print(f"   Gemini: {' PASS' if primary_ok else ' FAIL'}")
    print(f"   Groq:   {' PASS' if fallback_ok else ' FAIL'}")
    
    if primary_ok or fallback_ok:
        print("\n LLM Router is working!")
    else:
        print("\n  Check your API keys in .env")

if __name__ == "__main__":
    asyncio.run(main())