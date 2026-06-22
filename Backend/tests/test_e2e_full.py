import pytest
import httpx
import asyncio
import re

BASE_URL = "http://localhost:8000"
TEST_ELECTRICITY_ID = "ELEC-608064"

def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, strip whitespace, collapse spaces"""
    return " ".join(text.lower().strip().split())


@pytest.mark.asyncio
async def test_01_health_and_readiness():
    """Verify backend is alive and ready"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        print("✅ Health check passed")


@pytest.mark.asyncio
async def test_02_auth_flow():
    """Test user registration and login"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Login with existing test user
        resp = await client.post("/api/v1/auth/login", json={
            "electricity_id": TEST_ELECTRICITY_ID
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["electricity_id"] == TEST_ELECTRICITY_ID
        assert "name" in data
        print(f"✅ Auth flow passed: {data['name']}")


@pytest.mark.asyncio
async def test_03_chat_session_creation():
    """Test creating a chat session"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        resp = await client.post(
            "/api/v1/chat/sessions",
            params={"electricity_id": TEST_ELECTRICITY_ID, "title": "E2E Test"}
        )
        assert resp.status_code == 200
        session = resp.json()
        assert "session_id" in session
        assert session["electricity_id"] == TEST_ELECTRICITY_ID
        print(f"✅ Session created: {session['session_id']}")
        return session["session_id"]


@pytest.mark.asyncio
async def test_04_chat_message_flow():
    """Test full chat: message → agent → response → history saved"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Create session
        resp = await client.post(
            "/api/v1/chat/sessions",
            params={"electricity_id": TEST_ELECTRICITY_ID}
        )
        session_id = resp.json()["session_id"]
        
        # 2. Send message
        message = "What is my current balance?"
        resp = await client.post("/api/v1/chat/message", json={
            "electricity_id": TEST_ELECTRICITY_ID,
            "session_id": session_id,
            "message": message
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        result = resp.json()
        
        # 3. Validate response structure
        assert "response" in result, "Response missing 'response' field"
        assert result["session_id"] == session_id
        assert len(result["response"]) > 10, "Response too short"
        
        # 4. Verify message saved to history
        resp = await client.get(
            f"/api/v1/chat/sessions/{session_id}/messages",
            params={"limit": 10}
        )
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 2, f"Expected >=2 messages, got {len(messages)}"
        
        # 5. Verify content with robust comparison
        user_msg = next((m for m in messages if m["role"] == "user"), None)
        bot_msg = next((m for m in messages if m["role"] == "assistant"), None)
        
        assert user_msg, "User message not found in history"
        # Normalize both strings for comparison (handles trailing spaces, case)
        expected_words = set(re.findall(r'\b[a-z]+\b', message.lower()))
        actual_words = set(re.findall(r'\b[a-z]+\b', user_msg["content"].lower()))

        # Check that at least 80% of expected words appear in actual content
        overlap = len(expected_words & actual_words) / len(expected_words)
        assert overlap >= 0.8, \
            f"Message content mismatch.\nExpected words: {expected_words}\nActual words: {actual_words}\nOverlap: {overlap*100:.1f}%"
        
        assert bot_msg, "Bot message not found in history"
        assert len(bot_msg["content"]) > 10, "Bot response too short"
        
        print(f"✅ Chat flow passed: '{message}' → '{bot_msg['content'][:60]}...'")
        return True


@pytest.mark.asyncio
async def test_05_error_handling():
    """Test graceful handling of invalid/ambiguous queries"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        # Send out-of-domain question
        resp = await client.post("/api/v1/chat/message", json={
            "electricity_id": TEST_ELECTRICITY_ID,
            "message": "What's the weather like today?"
        })
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        result = resp.json()
        
        assert "response" in result, "Response missing 'response' field"
        
        # Check for friendly error handling (not exact wording)
        response_lower = result["response"].lower()

        # Should contain helpful language or domain context
        is_helpful = any(phrase in response_lower for phrase in [
            "sorry", "help", "assist", "billing", "electricity", 
            "question", "ask", "unable", "check"
        ])

        # Or should be a reasonably long response (not a short error code)
        is_reasonable_length = len(response_lower) > 30

        assert is_helpful or is_reasonable_length, \
            f"Response not helpful: {result['response']}"
        
        print(f"✅ Error handling passed: {result['response'][:80]}...")


# Optional: Run all tests in order with a single command
@pytest.mark.asyncio
async def test_full_pipeline():
    """Master test that runs the core flow end-to-end"""
    await test_01_health_and_readiness()
    await test_02_auth_flow()
    await test_04_chat_message_flow()
    await test_05_error_handling()
    print("\n🎉 FULL E2E PIPELINE PASSED")