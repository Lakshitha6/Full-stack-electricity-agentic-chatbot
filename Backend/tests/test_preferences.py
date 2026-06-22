import pytest
from src.services.preference_service import extract_preferences_from_chat

@pytest.mark.asyncio
async def test_extract_preferences_simple():
    """Test preference extraction with sample conversation"""
    electricity_id = "ELEC-608064"
    messages = [
        {"role": "user", "content": "¿Cuánto pagué en marzo?"},  # Spanish question
        {"role": "assistant", "content": "Pagaste $600 en marzo de 2024."},
        {"role": "user", "content": "Show me my usage trends"},  # English, detailed request
        {"role": "assistant", "content": "Here are your monthly units..."}
    ]
    
    prefs = await extract_preferences_from_chat(electricity_id, messages)
    
    assert isinstance(prefs, dict)
    assert "preferred_language" in prefs  # Should infer "es" or "en"
    assert "response_detail_level" in prefs
    assert isinstance(prefs.get("common_queries"), list)
    
    print(f" Extracted: {prefs}")