import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

OUTPUT_DIR = "data"
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "BEL_PE_All_Practice_Questions.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_pdf(questions: list):
    styles = getSampleStyleSheet()
    story = []

    if not questions:
        story.append(
            Paragraph(
                "<b>No questions attempted yet.</b><br/>"
                "Start practicing to generate your PDF.",
                styles["Normal"]
            )
        )
    else:
        for i, q in enumerate(questions, start=1):
            story.append(Paragraph(f"<b>Q{i}. {q['question']}</b>", styles["Normal"]))
            story.append(Spacer(1, 6))

            for idx, opt in enumerate(q["options"]):
                story.append(Paragraph(f"{chr(65+idx)}. {opt}", styles["Normal"]))

            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"<b>Correct Answer:</b> {chr(65 + q['correct_option'])}",
                styles["Normal"]
            ))
            story.append(Paragraph(
                f"<b>Explanation:</b> {q['explanation']}",
                styles["Normal"]
            ))
            story.append(Spacer(1, 12))

    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=A4)
    doc.build(story)

    return OUTPUT_PDF

def generate_subject_pdf(questions: list, subject: str):
    styles = getSampleStyleSheet()
    story = []

    filtered = [q for q in questions if q["subject"] == subject]

    if not filtered:
        story.append(
            Paragraph(
                f"<b>No attempted questions for subject: {subject}</b>",
                styles["Normal"]
            )
        )
    else:
        for i, q in enumerate(filtered, start=1):
            story.append(Paragraph(f"<b>Q{i}. {q['question']}</b>", styles["Normal"]))
            story.append(Spacer(1, 6))

            for idx, opt in enumerate(q["options"]):
                story.append(Paragraph(f"{chr(65+idx)}. {opt}", styles["Normal"]))

            story.append(Spacer(1, 6))
            story.append(Paragraph(
                f"<b>Correct Answer:</b> {chr(65 + q['correct_option'])}",
                styles["Normal"]
            ))
            story.append(Paragraph(
                f"<b>Explanation:</b> {q['explanation']}",
                styles["Normal"]
            ))
            story.append(Spacer(1, 12))

    filename = f"BEL_PE_{subject.replace(' ', '_')}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    doc.build(story)

    return pdf_path

