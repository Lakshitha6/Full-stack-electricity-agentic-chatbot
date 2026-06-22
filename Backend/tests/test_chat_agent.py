import pytest
import httpx
from src.models.chat import ChatRequest

BASE_URL = "http://localhost:8000/api/v1/chat"

@pytest.mark.asyncio
async def test_chat_message():
    """Test full chat flow: message → agent → response → saved to DB"""

    electricity_id = "ELEC-608064"

    async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=30.0) as client:

        # 1. Create a session
        resp = await client.post(
            f"{BASE_URL}/sessions",
            params={"electricity_id": electricity_id, "title": "Full pipeline Test"}
        )

        assert resp.status_code == 200
        session = resp.json()
        session_id = session["session_id"]

        # 2. Send a message
        message = "What is my current balance ?"
        resp = await client.post(
            f"{BASE_URL}/message",
            json={
                "electricity_id": electricity_id,
                "session_id": session_id,
                "message": message
            }
        )
        
        assert resp.status_code == 200
        result = resp.json()

        # 3. Validate response structure
        assert "response" in result
        assert result["session_id"] == session_id
        assert len(result["response"]) > 10  # Non-trivial answer
        
        # 4. Verify message was saved
        resp = await client.get(
            f"{BASE_URL}/sessions/{session_id}/messages",
            params={"limit": 10}
        )
        assert resp.status_code == 200
        messages = resp.json()
        assert len(messages) >= 2  # user + assistant
        
        # 5. Check content
        user_msg = next((m for m in messages if m["role"] == "user"), None)
        bot_msg = next((m for m in messages if m["role"] == "assistant"), None)
        assert user_msg and message in user_msg["content"]
        assert bot_msg and "balance" in bot_msg["content"].lower()
        
        print(f" Full pipeline test passed: '{message}' → '{bot_msg['content'][:60]}...'")
        return True