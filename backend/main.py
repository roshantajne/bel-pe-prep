import asyncio
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import Body

from agent import generate_mcqs
from buffer import (
    QUESTION_BUFFER,
    ensure_subject,
    refill_buffer,
    LOW_WATER_MARK
)
from storage import save_question, load_all_questions, append_to_google_doc
from pdf_generator import generate_pdf, generate_subject_pdf

app = FastAPI()


# -------------------- STARTUP --------------------
@app.on_event("startup")
async def startup_event():
    # Optional warm-up
    asyncio.create_task(refill_buffer("Data Structures", generate_mcqs))


# -------------------- NEXT QUESTION --------------------
@app.get("/next-question")
async def next_question(subject: str = "Data Structures"):
    ensure_subject(subject)

    # Trigger background refill (NON-BLOCKING)
    if len(QUESTION_BUFFER[subject]) <= LOW_WATER_MARK:
        asyncio.create_task(refill_buffer(subject, generate_mcqs))

    # First time / emergency fill
    if not QUESTION_BUFFER[subject]:
        await refill_buffer(subject, generate_mcqs)

    # Serve instantly
    return QUESTION_BUFFER[subject].pop(0)


# -------------------- SAVE ANSWER --------------------
@app.post("/save-attempt")
def save_attempt(attempt: dict = Body(...)):
    save_question(attempt)
    formatted = f"""
Q. {attempt['question']}
Options: {attempt['options']}
Selected: {attempt['selected_option']}
Correct: {attempt['correct_option']}
Explanation: {attempt['explanation']}
Result: {attempt['result']}
------------------------------
"""
    append_to_google_doc(formatted)
    return {"status": "saved"}


# -------------------- ALL QUESTIONS PDF --------------------
@app.get("/download-pdf")
def download_all_pdf():
    questions = load_all_questions()
    pdf_path = generate_pdf(questions)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="BEL_PE_All_Practice_Questions.pdf"
    )


# -------------------- SUBJECT PDF --------------------
@app.get("/download-pdf/{subject}")
def download_subject_pdf(subject: str):
    questions = load_all_questions()
    pdf_path = generate_subject_pdf(questions, subject)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"BEL_PE_{subject.replace(' ', '_')}.pdf"
    )
