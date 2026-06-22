"""
Interactive CLI to test the Electricity Bill Agentic Chatbot.
Usage: python main.py

Features:
- Natural language queries → SQL → DB → Response
- Shows debug info: generated SQL, latency, tokens used
- Maintains conversation session
- Works with or without JWT auth
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ELECTRICITY_ID = "ELEC-608064"  # Change to test other users
SHOW_DEBUG = True  # Set to False for clean output only
TIMEOUT_SECONDS = 45  # Increased for LLM + DB roundtrip


class AgentCLI:
    def __init__(self, base_url: str, electricity_id: str, debug: bool = True):
        self.base_url = base_url
        self.electricity_id = electricity_id
        self.debug = debug
        self.session_id = None
        self.auth_token = None  # Set if using JWT auth
        self.client = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=TIMEOUT_SECONDS)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    def _headers(self) -> dict:
        """Build request headers with optional auth"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    async def create_session(self, title: str = "CLI Test Session") -> str:
        """Create a new chat session and return session_id"""
        resp = await self.client.post(
            "/api/v1/chat/sessions",
            params={"electricity_id": self.electricity_id, "title": title},
            headers=self._headers()
        )
        resp.raise_for_status()
        data = resp.json()
        self.session_id = data["session_id"]
        if self.debug:
            print(f"🔹 Session created: {self.session_id}")
        return self.session_id

    async def send_message(self, message: str) -> dict:
        """Send a message and return the full API response"""
        if not self.session_id:
            await self.create_session()
        
        start_time = datetime.utcnow()
        
        resp = await self.client.post(
            "/api/v1/chat/message",
            json={
                "electricity_id": self.electricity_id,
                "session_id": self.session_id,
                "message": message
            },
            headers=self._headers()
        )
        
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        resp.raise_for_status()
        result = resp.json()
        
        # Add timing metadata
        result["_latency_ms"] = round(latency_ms, 1)
        return result

    async def get_history(self, limit: int = 10) -> list:
        """Fetch recent messages from current session"""
        if not self.session_id:
            return []
        resp = await self.client.get(
            f"/api/v1/chat/sessions/{self.session_id}/messages",
            params={"limit": limit},
            headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()

    def print_response(self, result: dict, user_message: str):
        """Pretty-print the agent response with optional debug info"""
        print("\n" + "="*70)
        print(f"👤 You: {user_message}")
        print(f"🤖 Agent: {result['response']}")
        
        if self.debug:
            print("\n🔍 Debug Info:")
            print(f"   • Latency: {result.get('_latency_ms', 'N/A')}ms")
            print(f"   • Session: {result.get('session_id', 'N/A')[:8]}...")
            
            metadata = result.get('metadata', {})
            if metadata.get('sql'):
                print(f"   • SQL: {metadata['sql'][:100]}{'...' if len(metadata['sql']) > 100 else ''}")
            if metadata.get('error'):
                print(f"   • ⚠️ Error: {metadata['error'][:80]}")
            if metadata.get('confidence'):
                print(f"   • Confidence: {metadata['confidence']}")
        print("="*70 + "\n")


async def main():
    print("\n🔋 Electricity Bill Agentic Chatbot — Interactive CLI")
    print(f"   Base URL: {BASE_URL}")
    print(f"   User ID:  {TEST_ELECTRICITY_ID}")
    print(f"   Debug:    {'ON' if SHOW_DEBUG else 'OFF'}")
    print("\n💡 Type your question. Type 'exit', 'quit', or 'q' to stop.\n")

    async with AgentCLI(BASE_URL, TEST_ELECTRICITY_ID, debug=SHOW_DEBUG) as cli:
        # Create initial session
        await cli.create_session()
        
        while True:
            try:
                # Get user input
                user_input = input("❓ Ask about your bills: ").strip()
                
                # Exit conditions
                if user_input.lower() in ["exit", "quit", "q", "bye"]:
                    print("\n👋 Goodbye! Run again to continue testing.\n")
                    break
                
                if not user_input:
                    continue
                
                # Send to agent
                print("🔄 Thinking...", end="", flush=True)
                result = await cli.send_message(user_input)
                print("\r" + " " * 20 + "\r", end="", flush=True)  # Clear "Thinking..."
                
                # Print response
                cli.print_response(result, user_input)
                
                # Optional: Show last 2 messages for context
                if SHOW_DEBUG:
                    history = await cli.get_history(limit=2)
                    if len(history) >= 2:
                        print("💬 Recent context:")
                        for msg in history[-2:]:
                            role = "👤" if msg["role"] == "user" else "🤖"
                            preview = msg["content"][:60] + "..." if len(msg["content"]) > 60 else msg["content"]
                            print(f"   {role} {preview}")
                        print()
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted. Type 'exit' to quit cleanly.\n")
            except httpx.ConnectError:
                print(f"\n❌ Could not connect to {BASE_URL}")
                print("   → Is the backend running? (uvicorn or docker compose)")
                print("   → Try: curl http://localhost:8000/health\n")
                break
            except httpx.HTTPStatusError as e:
                print(f"\n❌ API Error {e.response.status_code}: {e.response.text[:200]}")
                if e.response.status_code == 401:
                    print("   → JWT auth required? Set cli.auth_token = 'your_token'")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
                if SHOW_DEBUG:
                    import traceback
                    traceback.print_exc()
                break


if __name__ == "__main__":
    asyncio.run(main())