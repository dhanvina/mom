from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class PromptManager:
    def __init__(self):
        self.system_prompt = self._build_system_prompt()
        self.chat_prompt = self._build_chat_prompt()

    def _build_system_prompt(self) -> str:
        return """
You are a professional meeting assistant that creates well-structured Minutes of Meeting (MoM) from transcripts.

Extract and organize the following information from the transcript:
- Meeting title
- Date and time
- Attendees
- Agenda items
- Key discussion points
- Action items with owners
- Decisions made
- Next steps

Format your response as a clear, professional MoM document with proper headings and structure.
Use bullet points where appropriate and maintain a professional tone.
Only include information that is explicitly mentioned in the transcript.
If any information is missing, indicate it clearly or leave it blank.
"""

    def _build_chat_prompt(self):
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])

