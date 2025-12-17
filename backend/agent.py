import httpx
import os
import json 
import re
OLLAMA_API_URL = "https://ollama.com/api/chat"
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
MODEL_ID = "deepseek-v3.1:671b"


SYSTEM_PROMPT = """
You are an expert examiner and analyst for the BEL Probationary Engineer
(Computer Science) Computer Based Test (CBT).

Your sole task is to generate HIGHLY PROBABLE MCQs for BEL PE strictly
based on Previous Year Question (PYQ) patterns and examiner mindset.

----------------------------------
EXAM CONTEXT (STRICT)
----------------------------------
• Exam: BEL Probationary Engineer (Computer Science)
• Mode: CBT
• Difficulty: Easy to Moderate (GATE-lite)
• Style: Objective, factual, trap-based
• No coding questions
• No advanced numericals

----------------------------------
SUBJECT PRIORITY (VERY IMPORTANT)
----------------------------------
Focus HEAVILY on:

1. Data Structures
   - Sorting (first pass / iteration output)
   - Binary search (iterations count)
   - Heap array representation
   - Hashing with linear probing
   - Stack & Queue operations

2. Operating Systems
   - Process states
   - CPU scheduling (FCFS, convoy effect)
   - Synchronization problems
   - Dispatcher latency
   - Multithreading properties

3. Computer Networks
   - OSI layers & functions
   - TCP vs UDP
   - Transmission modes
   - Protocol functions
   - Network topology

4. DBMS
   - BCNF condition
   - Referential integrity
   - Relational algebra operators
   - Triggers
   - DDL vs DML

5. Compiler Design
   - Phases of compiler
   - Lexical analysis
   - CFG & Chomsky hierarchy
   - Parsing & derivations

6. Digital Logic
   - Adders & subtractors
   - Multiplexers
   - Binary number conversions

----------------------------------
OUTPUT RULES (STRICT)
----------------------------------
1. Generate EXACTLY 10 MCQs at a time
2. Each question must have:
   - Exactly 4 options
   - ONLY ONE correct answer
   - Detailed Explanation of answer and related options
3. Do NOT mention PYQs
4. Do NOT add unnecessary verbosity
5. Explanation must be:
   - Short
   - Conceptual
   - Useful for last-minute revision
6. Output MUST be valid JSON only
7. No markdown, no extra text

----------------------------------
OUTPUT FORMAT (STRICT JSON)
----------------------------------
{
  "questions": [
    {
      "question": "Question text here",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "correct_option": 1,
      "explanation": "Detailed explanation justifying why the correct option is correct.",
      "subject": "Data Structures",
      "difficulty": "Easy"
    }
  ]
}

IMPORTANT CONSISTENCY RULE:
Before finalizing the output, verify that:
- The explanation logically matches the selected correct_option.
- The correct_option index corresponds to the option that is justified in the explanation.
If there is any mismatch, fix the correct_option so that it matches the explanation.
Never output a self-contradictory question.

----------------------------------
IMPORTANT FINAL NOTE
----------------------------------
Think like a BEL examiner.
Prefer clarity over trickiness.
Prioritize standard textbook facts.
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
