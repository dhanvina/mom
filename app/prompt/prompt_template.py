from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class PromptManager:
    def __init__(self):
        self.system_prompt = self._build_system_prompt()
        self.chat_prompt = self._build_chat_prompt()

    def _build_system_prompt(self) -> str:
        return """
You are a professional meeting assistant that extracts structured Minutes of Meeting (MoM) from raw, unstructured transcripts.

Instructions:
- Remove irrelevant content (e.g., greetings, email footers, small talk).
- If agenda or discussion is too long, summarize it concisely.
- Maintain clarity, professionalism, and structure.
- If any expected field is missing in the input, return an empty string "" or empty list [] for that field.
- Do NOT hallucinate or assume details not explicitly mentioned in the transcript.


Your output MUST strictly follow this Markdown format using triple dashes (`---`) at the start and end:
Return the result in valid PDF format with the following keys:
---
Meeting Title: <title>  
Date & Time: <date and time>  
Attendees: <people or roles>  
Agenda: <summarized agenda if long>  
Discussion Summary: <brief overview>  
Key Decisions: <decisions made>  
Action Items:  
- <task 1> – Owner  
- <task 2> – Owner  

Conclusion: <wrap-up or next steps>  
Additional Notes: <any extra observations or metadata>  
---
"""

    def _build_chat_prompt(self):
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(self.system_prompt),
            HumanMessagePromptTemplate.from_template("Transcript:\n{transcript}")
        ])

# test_prompt_template.py

# from langchain.chat_models import ChatOllama
# from prompt.prompt_template import PromptManager

# # Step 1: Initialize PromptManager
# pm = PromptManager()

# # Step 2: Sample input transcript
# sample_transcript = """
# The meeting began with a brief catch-up after the weekend. The primary focus was on reviewing the current status of the AI module integration project and addressing pending tasks. There was some back-and-forth discussion on progress, roadblocks, and shifting internal deadlines.

# Backend API Progress:

# Ravi confirmed that the backend API is fully developed and has been deployed to the staging environment. He mentioned that while the main logic and endpoint structure are complete, there may still be minor improvements needed, particularly in the logging mechanism, which currently returns vague error responses. He's working on refining this part and acknowledged that it may need additional polishing during testing.

# Postman collections have been prepared but not fully cleaned or documented. Ravi promised to share a link to the API collection and follow up with inline comments or a short README-style guide. There is no formal Swagger/OpenAPI spec published yet, which could slow down the frontend or testing effort if not resolved soon.

# Testing & Quality Checks:

# Sara has been assigned to perform API testing throughout the week. She plans to start by validating the authentication flow, followed by the core inference routes. A few questions were raised about payload structure and expected response formats — Ravi agreed to be on standby to assist her during the testing process.

# There was also a note of caution that depending on how testing goes, some small bugs or overlooked behaviors may surface. Sara mentioned she’s okay with tight timelines and expects to finish initial test cases and validations by Wednesday EOD, barring any major blockers.

# Demo Deadline Shift:

# Originally, the internal AI module demo was scheduled for this Wednesday. However, due to delays in both backend completion and lack of thorough testing, the team decided to move the demo to next Friday. This was mutually agreed upon to ensure stability and give everyone sufficient time for final verification.

# The updated timeline also aligns better with the UI freeze policy that’s currently in place. Until backend routes are finalized and validated by Sara, no new UI feature integrations will proceed.

# Dependencies and Pending Items:

# API documentation is incomplete. Ravi will be responsible for getting at least a basic version out to Sara for testing support.

# There’s still no update from the ML team on the model training pipeline. Sara will follow up separately with Ashwin to check on their status and whether inference latency benchmarks have been achieved.

# No major decisions were made on deployment or environment configuration; these are being deferred until testing is complete.

# Frontend team is on hold pending backend validation.
# """

# # Step 3: Format the prompt messages
# messages = pm.chat_prompt.format_messages(transcript=sample_transcript)

# # Step 4: Load your model (example with Ollama Mistral)
# llm = ChatOllama(model="mistral", temperature=0.2, max_tokens=512)

# # Step 5: Get LLM response
# response = llm.invoke(messages)

# # Step 6: Print output
# print(response.content)
