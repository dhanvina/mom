"""
Unit tests for the LanguagePrompts class.
"""

import pytest
from app.prompt.language_prompts import LanguagePrompts

class TestLanguagePrompts:
    """Test cases for LanguagePrompts class."""
    
    def test_get_system_prompt_english(self):
        """Test getting system prompt in English."""
        prompt = LanguagePrompts.get_system_prompt("en")
        assert "You are a professional meeting assistant" in prompt
        assert "MEETING TITLE" in prompt
        assert "DATE AND TIME" in prompt
        assert "ATTENDEES" in prompt
    
    def test_get_system_prompt_spanish(self):
        """Test getting system prompt in Spanish."""
        prompt = LanguagePrompts.get_system_prompt("es")
        assert "Eres un asistente profesional de reuniones" in prompt
        assert "TÍTULO DE LA REUNIÓN" in prompt
        assert "FECHA Y HORA" in prompt
        assert "ASISTENTES" in prompt
    
    def test_get_system_prompt_french(self):
        """Test getting system prompt in French."""
        prompt = LanguagePrompts.get_system_prompt("fr")
        assert "Vous êtes un assistant professionnel de réunion" in prompt
        assert "TITRE DE LA RÉUNION" in prompt
        assert "DATE ET HEURE" in prompt
        assert "PARTICIPANTS" in prompt
    
    def test_get_system_prompt_german(self):
        """Test getting system prompt in German."""
        prompt = LanguagePrompts.get_system_prompt("de")
        assert "Sie sind ein professioneller Meeting-Assistent" in prompt
        assert "BESPRECHUNGSTITEL" in prompt
        assert "DATUM UND UHRZEIT" in prompt
        assert "TEILNEHMER" in prompt
    
    def test_get_system_prompt_italian(self):
        """Test getting system prompt in Italian."""
        prompt = LanguagePrompts.get_system_prompt("it")
        assert "Sei un assistente professionale per riunioni" in prompt
        assert "TITOLO DELLA RIUNIONE" in prompt
        assert "DATA E ORA" in prompt
        assert "PARTECIPANTI" in prompt
    
    def test_get_system_prompt_portuguese(self):
        """Test getting system prompt in Portuguese."""
        prompt = LanguagePrompts.get_system_prompt("pt")
        assert "Você é um assistente profissional de reuniões" in prompt
        assert "TÍTULO DA REUNIÃO" in prompt
        assert "DATA E HORA" in prompt
        assert "PARTICIPANTES" in prompt
    
    def test_get_system_prompt_dutch(self):
        """Test getting system prompt in Dutch."""
        prompt = LanguagePrompts.get_system_prompt("nl")
        assert "U bent een professionele vergaderassistent" in prompt
        assert "VERGADERTITEL" in prompt
        assert "DATUM EN TIJD" in prompt
        assert "AANWEZIGEN" in prompt
    
    def test_get_system_prompt_japanese(self):
        """Test getting system prompt in Japanese."""
        prompt = LanguagePrompts.get_system_prompt("ja")
        assert "あなたは、議事録を作成するプロフェッショナルな会議アシスタントです" in prompt
        assert "会議タイトル" in prompt
        assert "日付と時間" in prompt
        assert "出席者" in prompt
    
    def test_get_system_prompt_chinese(self):
        """Test getting system prompt in Chinese."""
        prompt = LanguagePrompts.get_system_prompt("zh")
        assert "您是一位专业的会议助手" in prompt
        assert "会议标题" in prompt
        assert "日期和时间" in prompt
        assert "参会人员" in prompt
    
    def test_get_system_prompt_russian(self):
        """Test getting system prompt in Russian."""
        prompt = LanguagePrompts.get_system_prompt("ru")
        assert "Вы профессиональный ассистент по проведению совещаний" in prompt
        assert "НАЗВАНИЕ ВСТРЕЧИ" in prompt
        assert "ДАТА И ВРЕМЯ" in prompt
        assert "УЧАСТНИКИ" in prompt
    
    def test_get_system_prompt_unsupported_language(self):
        """Test getting system prompt for an unsupported language."""
        # Should fall back to English with a note to respond in the target language
        prompt = LanguagePrompts.get_system_prompt("xx")
        assert "You are a professional meeting assistant" in prompt
        assert "Please respond in xx language" in prompt