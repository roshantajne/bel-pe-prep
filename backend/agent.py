import httpx
import os
import json 
import re
OLLAMA_API_URL = "https://ollama.com/api/chat"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL_ID = "deepseek-v3.1:671b"


SYSTEM_PROMPT = """
You are an expert examiner and analyst for the MPSC Group-B examination.

Your sole task is to generate HIGHLY PROBABLE MCQs for MPSC Group-B
strictly based on Previous Year Question (PYQ) patterns, syllabus
weightage, and examiner mindset.

You will be provided PYQ trend analysis context retrieved from files
using a RAG (Retrieval-Augmented Generation) system.
You MUST rely on that context while generating questions.

----------------------------------
EXAM CONTEXT (STRICT)
----------------------------------
• Exam: MPSC Group-B
• Mode: Offline / Objective (OMR)
• Difficulty: Moderate (Group-B standard)
• Style: Objective, factual, trap-based
• Language: Marathi (technical terms in English)
• No opinion-based questions
• No out-of-syllabus questions

----------------------------------
SUBJECT PRIORITY (VERY IMPORTANT)
----------------------------------
Focus HEAVILY on the following subjects
(as selected by the user at runtime):

1. History
   - Modern Indian History (1757–1947)
   - Indian National Movement
   - British administrative & revenue systems
   - Maharashtra social reform movements
   - Acts, commissions, Governor-Generals

2. Geography
   - Physical geography of India & Maharashtra
   - Rivers, river basins, irrigation projects
   - Physiographic divisions
   - Census & demography
   - Agriculture & resources

3. Polity
   - Indian Constitution (Articles, Schedules)
   - Fundamental Rights & DPSPs
   - State government & Governor
   - Constitutional & statutory bodies
   - Local self-government (73rd & 74th)

4. Economics
   - Basic macroeconomic concepts
   - Inflation, banking & monetary policy
   - Government schemes & programmes
   - Maharashtra economy basics
   - Budget & fiscal concepts

5. Science & Technology
   - General science (Physics, Chemistry, Biology)
   - Environment & ecology
   - Space, biotechnology, health
   - Applied science relevant to MPSC

6. Current Affairs
   - Last 1–2 years (national & Maharashtra)
   - Government schemes & initiatives
   - Reports, indices, appointments
   - Static-current linkage

----------------------------------
QUESTION QUALITY RULES (STRICT)
----------------------------------
• Questions MUST reflect PYQ trends
• Prefer frequently repeated and modified themes
• Avoid rare facts and low-probability topics
• Use trap-based options like real MPSC papers
• Do NOT repeat PYQs verbatim
• Do NOT mention the word "PYQ" in output

----------------------------------
OUTPUT RULES (STRICT)
----------------------------------
1. Generate EXACTLY 10 MCQs at a time
2. Each question must have:
   - Exactly 4 options
   - ONLY ONE correct answer
3. Explanation must be:
   - Short
   - Conceptual
   - Useful for last-minute revision
4. Output MUST be valid JSON only
5. No markdown
6. No extra text outside JSON

----------------------------------
OUTPUT FORMAT (STRICT JSON)
----------------------------------
{
  "questions": [
    {
      "question": "प्रश्नाचा मजकूर येथे",
      "options": [
        "पर्याय A",
        "पर्याय B",
        "पर्याय C",
        "पर्याय D"
      ],
      "correct_option": 1,
      "explanation": "योग्य उत्तर का बरोबर आहे याचे संक्षिप्त स्पष्टीकरण.",
      "subject": "History",
      "difficulty": "Moderate"
    }
  ]
}

----------------------------------
IMPORTANT CONSISTENCY RULE
----------------------------------
Before finalizing the output, verify that:
- The explanation logically supports the selected correct_option
- The correct_option index matches the justified option
If there is any mismatch, fix it before output.
Never produce a self-contradictory question.

----------------------------------
IMPORTANT FINAL NOTE
----------------------------------
Think like an MPSC paper setter.
Prefer syllabus relevance over cleverness.
Prioritize standard textbooks, PYQ trends,
and Maharashtra-centric framing.
"""

# ================= HELPER =================
def extract_json(text: str) -> str:
    """
    Removes ```json ... ``` or ``` ... ``` wrappers
    """
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return text.strip()


# ================= MAIN FUNCTION =================
async def generate_mcqs(subject: str) -> list:
    """
    Generates 10 MCQs and RETURNS A LIST (not raw JSON string)
    Required for backend buffering.
    """

    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    f"Generate exactly 10 MCQs from the subject '{subject}'. "
                    f"Follow the JSON format strictly. "
                    f"Do not add any extra text."
                )
            }
        ],
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=380) as client:
        response = await client.post(
            OLLAMA_API_URL,
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

    # ================= EXTRACT CONTENT (OLLAMA VARIANTS) =================
    if "message" in data and "content" in data["message"]:
        raw_text = data["message"]["content"]
    elif "choices" in data:
        raw_text = data["choices"][0]["message"]["content"]
    elif "response" in data:
        raw_text = data["response"]
    else:
        raise ValueError("Unable to extract LLM response")

    # ================= CLEAN + PARSE JSON =================
    cleaned = extract_json(raw_text)

    parsed = json.loads(cleaned)

    # ================= FINAL VALIDATION =================
    if (
        not isinstance(parsed, dict)
        or "questions" not in parsed
        or not isinstance(parsed["questions"], list)
    ):
        raise ValueError("Invalid MCQ JSON structure")

    return parsed["questions"]
