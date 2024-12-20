import pytest
from unittest.mock import patch, MagicMock
from pages.chatbot import Chatbot


@pytest.fixture
def setup_chatbot():
    """Fixture to initialize the Chatbot instance."""
    chatbot = Chatbot()
    return chatbot

@patch("pages.chatbot.openai.ChatCompletion.create")
def test_call_openai_with_error(mock_openai_call, setup_chatbot):
    """
    Test handling of OpenAI API errors in `call_openai` method.
    """
    mock_openai_call.side_effect = Exception("Simulated API error")

    chatbot = setup_chatbot
    df = MagicMock() 
    prompt = "Analyze the dataset."

    response = chatbot.call_openai(prompt, df)

    assert "Error calling OpenAI API: Simulated API error" in response