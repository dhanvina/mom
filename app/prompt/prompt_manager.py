"""
Prompt manager module for AI-powered MoM generator.

This module provides functionality for managing prompt templates.
"""

import logging
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .language_prompts import LanguagePrompts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages prompt templates for MoM extraction.
    
    This class provides methods for building and customizing prompt templates
    for extracting structured MoM data from meeting transcripts.
    
    Attributes:
        system_prompt (str): System prompt for the LLM
        chat_prompt (ChatPromptTemplate): Chat prompt template
        config (Dict): Configuration options for the prompt manager
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PromptManager with optional configuration.
        
        Args:
            config (Dict, optional): Configuration options for the prompt manager
        """
        self.config = config or {}
        self.system_prompt = self._build_system_prompt()
        self.chat_prompt = self._build_chat_prompt()
        logger.info("PromptManager initialized")
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for MoM extraction.
        
        Returns:
            str: System prompt
        """
        return LanguagePrompts.get_system_prompt("en")
    
    def _build_chat_prompt(self) -> ChatPromptTemplate:
        """
        Build the chat prompt template for MoM extraction.
        
        Returns:
            ChatPromptTemplate: Chat prompt template
        """
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])
    
    def get_prompt(self, language: str = "en") -> ChatPromptTemplate:
        """
        Get a prompt template for a specific language.
        
        Args:
            language (str, optional): Language code. Defaults to "en".
            
        Returns:
            ChatPromptTemplate: Chat prompt template for the specified language
        """
        # Get the appropriate system prompt for the language
        system_prompt = LanguagePrompts.get_system_prompt(language)
        
        # Create a chat prompt with the language-specific system prompt
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])
    
    def get_structured_prompt(self, language: str = "en") -> ChatPromptTemplate:
        """
        Get a prompt template that requests structured JSON output in the specified language.
        
        Args:
            language (str, optional): Language code. Defaults to "en".
            
        Returns:
            ChatPromptTemplate: Chat prompt template for structured output
        """
        # Get the base system prompt for the language
        system_prompt = LanguagePrompts.get_system_prompt(language)
        
        # Add JSON formatting instructions
        json_instructions = self._get_json_instructions(language)
        structured_system_prompt = system_prompt + "\n\n" + json_instructions
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(structured_system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])
    
    def get_enhanced_prompt(self) -> ChatPromptTemplate:
        """
        Get an enhanced prompt template with improved extraction capabilities.
        
        Returns:
            ChatPromptTemplate: Enhanced chat prompt template
        """
        # Get the enhanced system prompt
        system_prompt = LanguagePrompts._get_enhanced_en_system_prompt()
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])
    
    def get_enhanced_structured_prompt(self) -> ChatPromptTemplate:
        """
        Get an enhanced structured prompt template with improved extraction capabilities.
        
        Returns:
            ChatPromptTemplate: Enhanced structured chat prompt template
        """
        # Get the enhanced structured system prompt
        system_prompt = LanguagePrompts._get_enhanced_structured_prompt()
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])
        
    def get_topic_analysis_prompt(self) -> ChatPromptTemplate:
        """
        Get a topic analysis prompt template for meeting transcripts.
        
        Returns:
            ChatPromptTemplate: Topic analysis chat prompt template
        """
        # Get the topic analysis system prompt
        system_prompt = LanguagePrompts._get_topic_analysis_prompt()
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}\nNumber of topics to identify: {num_topics}")
        ])
    
    def _get_json_instructions(self, language: str) -> str:
        """
        Get JSON formatting instructions in the specified language.
        
        Args:
            language (str): Language code
            
        Returns:
            str: JSON formatting instructions
        """
        # English instructions (default)
        if language == "en":
            return """
Please format your response as a JSON object with the following structure:
{{
  "meeting_title": "Title of the meeting",
  "date_time": "Date and time of the meeting",
  "attendees": ["Person 1 (Role)", "Person 2 (Role)", ...],
  "agenda": ["Item 1", "Item 2", ...],
  "discussion_points": [
    {{"topic": "Topic 1", "details": "Details about topic 1"}},
    {{"topic": "Topic 2", "details": "Details about topic 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Task description", "assignee": "Person name", "due": "Due date"}},
    ...
  ],
  "decisions": [
    {{"decision": "Decision 1", "context": "Context for decision 1"}},
    ...
  ],
  "next_steps": ["Next step 1", "Next step 2", ...]
}}
"""
        # Spanish instructions
        elif language == "es":
            return """
Por favor, formatea tu respuesta como un objeto JSON con la siguiente estructura:
{{
  "meeting_title": "Título de la reunión",
  "date_time": "Fecha y hora de la reunión",
  "attendees": ["Persona 1 (Rol)", "Persona 2 (Rol)", ...],
  "agenda": ["Punto 1", "Punto 2", ...],
  "discussion_points": [
    {{"topic": "Tema 1", "details": "Detalles sobre el tema 1"}},
    {{"topic": "Tema 2", "details": "Detalles sobre el tema 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Descripción de la tarea", "assignee": "Nombre de la persona", "due": "Fecha límite"}},
    ...
  ],
  "decisions": [
    {{"decision": "Decisión 1", "context": "Contexto para la decisión 1"}},
    ...
  ],
  "next_steps": ["Siguiente paso 1", "Siguiente paso 2", ...]
}}
"""
        # French instructions
        elif language == "fr":
            return """
Veuillez formater votre réponse sous forme d'objet JSON avec la structure suivante:
{{
  "meeting_title": "Titre de la réunion",
  "date_time": "Date et heure de la réunion",
  "attendees": ["Personne 1 (Rôle)", "Personne 2 (Rôle)", ...],
  "agenda": ["Point 1", "Point 2", ...],
  "discussion_points": [
    {{"topic": "Sujet 1", "details": "Détails sur le sujet 1"}},
    {{"topic": "Sujet 2", "details": "Détails sur le sujet 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Description de la tâche", "assignee": "Nom de la personne", "due": "Date d'échéance"}},
    ...
  ],
  "decisions": [
    {{"decision": "Décision 1", "context": "Contexte pour la décision 1"}},
    ...
  ],
  "next_steps": ["Prochaine étape 1", "Prochaine étape 2", ...]
}}
"""
        # German instructions
        elif language == "de":
            return """
Bitte formatieren Sie Ihre Antwort als JSON-Objekt mit der folgenden Struktur:
{{
  "meeting_title": "Titel der Besprechung",
  "date_time": "Datum und Uhrzeit der Besprechung",
  "attendees": ["Person 1 (Rolle)", "Person 2 (Rolle)", ...],
  "agenda": ["Punkt 1", "Punkt 2", ...],
  "discussion_points": [
    {{"topic": "Thema 1", "details": "Details zu Thema 1"}},
    {{"topic": "Thema 2", "details": "Details zu Thema 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Aufgabenbeschreibung", "assignee": "Personenname", "due": "Fälligkeitsdatum"}},
    ...
  ],
  "decisions": [
    {{"decision": "Entscheidung 1", "context": "Kontext für Entscheidung 1"}},
    ...
  ],
  "next_steps": ["Nächster Schritt 1", "Nächster Schritt 2", ...]
}}
"""
        # Italian instructions
        elif language == "it":
            return """
Per favore, formatta la tua risposta come un oggetto JSON con la seguente struttura:
{{
  "meeting_title": "Titolo della riunione",
  "date_time": "Data e ora della riunione",
  "attendees": ["Persona 1 (Ruolo)", "Persona 2 (Ruolo)", ...],
  "agenda": ["Punto 1", "Punto 2", ...],
  "discussion_points": [
    {{"topic": "Argomento 1", "details": "Dettagli sull'argomento 1"}},
    {{"topic": "Argomento 2", "details": "Dettagli sull'argomento 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Descrizione del compito", "assignee": "Nome della persona", "due": "Data di scadenza"}},
    ...
  ],
  "decisions": [
    {{"decision": "Decisione 1", "context": "Contesto per la decisione 1"}},
    ...
  ],
  "next_steps": ["Prossimo passo 1", "Prossimo passo 2", ...]
}}
"""
        # Portuguese instructions
        elif language == "pt":
            return """
Por favor, formate sua resposta como um objeto JSON com a seguinte estrutura:
{{
  "meeting_title": "Título da reunião",
  "date_time": "Data e hora da reunião",
  "attendees": ["Pessoa 1 (Papel)", "Pessoa 2 (Papel)", ...],
  "agenda": ["Item 1", "Item 2", ...],
  "discussion_points": [
    {{"topic": "Tópico 1", "details": "Detalhes sobre o tópico 1"}},
    {{"topic": "Tópico 2", "details": "Detalhes sobre o tópico 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Descrição da tarefa", "assignee": "Nome da pessoa", "due": "Data de vencimento"}},
    ...
  ],
  "decisions": [
    {{"decision": "Decisão 1", "context": "Contexto para a decisão 1"}},
    ...
  ],
  "next_steps": ["Próximo passo 1", "Próximo passo 2", ...]
}}
"""
        # Dutch instructions
        elif language == "nl":
            return """
Gelieve uw antwoord te formatteren als een JSON-object met de volgende structuur:
{{
  "meeting_title": "Titel van de vergadering",
  "date_time": "Datum en tijd van de vergadering",
  "attendees": ["Persoon 1 (Rol)", "Persoon 2 (Rol)", ...],
  "agenda": ["Item 1", "Item 2", ...],
  "discussion_points": [
    {{"topic": "Onderwerp 1", "details": "Details over onderwerp 1"}},
    {{"topic": "Onderwerp 2", "details": "Details over onderwerp 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Taakbeschrijving", "assignee": "Naam van persoon", "due": "Vervaldatum"}},
    ...
  ],
  "decisions": [
    {{"decision": "Beslissing 1", "context": "Context voor beslissing 1"}},
    ...
  ],
  "next_steps": ["Volgende stap 1", "Volgende stap 2", ...]
}}
"""
        # Japanese instructions
        elif language == "ja":
            return """
以下の構造のJSONオブジェクトとして回答をフォーマットしてください：
{{
  "meeting_title": "会議のタイトル",
  "date_time": "会議の日付と時間",
  "attendees": ["人物1（役割）", "人物2（役割）", ...],
  "agenda": ["項目1", "項目2", ...],
  "discussion_points": [
    {{"topic": "トピック1", "details": "トピック1の詳細"}},
    {{"topic": "トピック2", "details": "トピック2の詳細"}},
    ...
  ],
  "action_items": [
    {{"task": "タスクの説明", "assignee": "担当者名", "due": "期限"}},
    ...
  ],
  "decisions": [
    {{"decision": "決定1", "context": "決定1の背景"}},
    ...
  ],
  "next_steps": ["次のステップ1", "次のステップ2", ...]
}}
"""
        # Chinese instructions
        elif language == "zh":
            return """
请将您的回答格式化为具有以下结构的JSON对象：
{{
  "meeting_title": "会议标题",
  "date_time": "会议日期和时间",
  "attendees": ["人员1（角色）", "人员2（角色）", ...],
  "agenda": ["项目1", "项目2", ...],
  "discussion_points": [
    {{"topic": "话题1", "details": "话题1的详细信息"}},
    {{"topic": "话题2", "details": "话题2的详细信息"}},
    ...
  ],
  "action_items": [
    {{"task": "任务描述", "assignee": "负责人姓名", "due": "截止日期"}},
    ...
  ],
  "decisions": [
    {{"decision": "决定1", "context": "决定1的背景"}},
    ...
  ],
  "next_steps": ["下一步1", "下一步2", ...]
}}
"""
        # Russian instructions
        elif language == "ru":
            return """
Пожалуйста, отформатируйте ваш ответ как JSON-объект со следующей структурой:
{{
  "meeting_title": "Название встречи",
  "date_time": "Дата и время встречи",
  "attendees": ["Человек 1 (Роль)", "Человек 2 (Роль)", ...],
  "agenda": ["Пункт 1", "Пункт 2", ...],
  "discussion_points": [
    {{"topic": "Тема 1", "details": "Детали по теме 1"}},
    {{"topic": "Тема 2", "details": "Детали по теме 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Описание задачи", "assignee": "Имя человека", "due": "Срок выполнения"}},
    ...
  ],
  "decisions": [
    {{"decision": "Решение 1", "context": "Контекст для решения 1"}},
    ...
  ],
  "next_steps": ["Следующий шаг 1", "Следующий шаг 2", ...]
}}
"""
        # For other languages, default to English with a note to respond in the target language
        else:
            return """
Please format your response as a JSON object with the following structure (respond in """ + language + """ language):
{{
  "meeting_title": "Title of the meeting",
  "date_time": "Date and time of the meeting",
  "attendees": ["Person 1 (Role)", "Person 2 (Role)", ...],
  "agenda": ["Item 1", "Item 2", ...],
  "discussion_points": [
    {{"topic": "Topic 1", "details": "Details about topic 1"}},
    {{"topic": "Topic 2", "details": "Details about topic 2"}},
    ...
  ],
  "action_items": [
    {{"task": "Task description", "assignee": "Person name", "due": "Due date"}},
    ...
  ],
  "decisions": [
    {{"decision": "Decision 1", "context": "Context for decision 1"}},
    ...
  ],
  "next_steps": ["Next step 1", "Next step 2", ...]
}}
"""