import pytest
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from app.prompt.prompt_template import PromptManager


class TestPromptManager:
    def setup_method(self):
        """Setup PromptManager instance before each test."""
        self.manager = PromptManager()

    def test_system_prompt_is_string(self):
        assert isinstance(self.manager.system_prompt, str), "System prompt should be a string."

    def test_system_prompt_has_expected_keys(self):
        keys = [
            "Meeting Title",
            "Date & Time",
            "Attendees",
            "Agenda",
            "Discussion Summary",
            "Key Decisions",
            "Action Items",
            "Conclusion",
            "Additional Notes"
        ]
        for key in keys:
            assert key in self.manager.system_prompt, f"Missing '{key}' in system prompt."

    def test_chat_prompt_is_instance(self):
        assert isinstance(self.manager.chat_prompt, ChatPromptTemplate), "chat_prompt should be a ChatPromptTemplate instance."

    def test_chat_prompt_has_two_messages(self):
        messages = self.manager.chat_prompt.messages
        assert len(messages) == 2, "chat_prompt should have 2 messages."
        assert isinstance(messages[0], SystemMessagePromptTemplate), "First message should be SystemMessagePromptTemplate."
        assert isinstance(messages[1], HumanMessagePromptTemplate), "Second message should be HumanMessagePromptTemplate."

    def test_chat_prompt_renders_correctly(self):
        rendered = self.manager.chat_prompt.format_messages(transcript="Team discussed launch plans.")
        assert isinstance(rendered, list), "Rendered output should be a list."
        combined = "".join(str(msg) for msg in rendered)
        assert "Team discussed launch plans." in combined, "Transcript not found in rendered message."
        assert "Meeting Title" in combined, "System prompt structure missing in rendered message."

    def test_chat_prompt_raises_key_error_on_missing_input(self):
        with pytest.raises(KeyError):
            self.manager.chat_prompt.format_messages()  # Missing 'transcript' input
