from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class PromptManager:
    def __init__(self):
        self.system_prompt = self._build_system_prompt()
        self.chat_prompt = self._build_chat_prompt()

    def _build_system_prompt(self) -> str:
        return """

YYou are an expert assistant that creates professional, well-structured Minutes of Meeting (MoM) documents from transcripts.

Here are the formatting rules and expectations:
- Use proper headings and bullet points for clarity and presentation.
- Remove irrelevant content such as greetings, small talk, email footers.
- Do not hallucinate. Only include what's explicitly mentioned in the transcript.
- If fields like date, time, or location are missing, leave them as empty strings or prompt the user.
- Ensure professional tone throughout.

Format output exactly like this:

Minutes of Meeting  
Client Meeting: <Client Name>  
Date: <Meeting Date>  
Time: <Meeting Time>  
Location: <Meeting Location>  

Attendees  
• Client: <Client Name>  
• Team Members:  
  o <Member 1>  
  o <Member 2>  
  ...  

Agenda  
• <Agenda Point 1>  
• <Agenda Point 2>  
...  

Discussion Points  
1. <Major Topic>  
• <Subpoint or Details>  
• <Another Point>  

2. <Another Major Topic>  
• <Subpoint>  
• <Subpoint>  

Action Items  
• <Clearly stated task from the transcript>  
• <If no one is assigned, do not assign. Only include what’s mentioned>  

Next Steps  
1. <Step 1>  
2. <Step 2>  
...  

Closing  
• <One-line summary if provided, else skip or keep concise>

Now, generate the structured minutes based only on this transcript:  
[Insert transcript here]

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
