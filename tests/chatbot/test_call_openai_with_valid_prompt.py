import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from pages.chatbot import Chatbot


@pytest.fixture
def setup_chatbot():
    """Fixture to initialize the Chatbot instance."""
    return Chatbot()

def test_call_openai_with_valid_prompt(setup_chatbot):
    """Test Chatbot's ability to call OpenAI API with a valid prompt."""
    chatbot = setup_chatbot

    mock_df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Age": [25, 30],
        "Salary": [50000, 60000]
    })

    mock_openai_response = {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from OpenAI API."
                }
            }
        ]
    }

    with patch("pages.chatbot.openai.ChatCompletion.create") as mock_openai:
        mock_openai.return_value = mock_openai_response

        prompt = "What is the average age of employees?"
        response = chatbot.call_openai(prompt, mock_df)

        mock_openai.assert_called_once() 
        assert response == "This is a test response from OpenAI API."