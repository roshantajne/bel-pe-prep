import streamlit as st
import requests
import time


# ================= CONFIG =================
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="BEL PE CBT Practice",
    layout="centered"
)

st.title("🧪 BEL Probationary Engineer – CBT Practice")

# ================= SESSION INIT =================
if "practice_started" not in st.session_state:
    st.session_state.practice_started = False

if "current_question" not in st.session_state:
    st.session_state.current_question = None

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "locked" not in st.session_state:
    st.session_state.locked = False

if "attempted" not in st.session_state:
    st.session_state.attempted = 0

if "correct" not in st.session_state:
    st.session_state.correct = 0

if "qa_log" not in st.session_state:
    st.session_state.qa_log = []

if "subject" not in st.session_state:
    st.session_state.subject = "Data Structures"

if "is_prefetching" not in st.session_state:
    st.session_state.is_prefetching = False

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Practice Setup")

selected_subject = st.sidebar.selectbox(
    "Select Subject",
    [
    "Computer Networks",
    "DBMS",
    "Compiler Design",
    "Digital Logic"
    "Digital Logic",
    "Object-Oriented Programming (OOPs)",
    "Computer Architecture",
    "Algorithms",
    "Artificial Intelligence / Machine Learning (BASIC ONLY)"
    ]
)

if st.sidebar.button("▶️ Start Practice"):
    st.session_state.subject = selected_subject
    st.session_state.practice_started = True
    st.session_state.current_question = None
    st.session_state.qa_log = []
    st.session_state.correct = 0
    st.session_state.attempted = 0



st.sidebar.divider()
st.sidebar.subheader("📄 All Questions PDF")

all_pdf_url = f"{BACKEND_URL}/download-pdf"

st.sidebar.markdown(
    f"""
    <form action="{all_pdf_url}" method="get" target="_blank">
        <button type="submit" style="
            width: 100%;
            padding: 10px;
            margin-bottom: 8px;
            background-color: #16a34a;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 600;
        ">
            ⬇️ Download ALL Questions (PDF)
        </button>
    </form>
    """,
    unsafe_allow_html=True
)


# st.sidebar.markdown(
#     f"[⬇️ Download ALL Practice Questions (PDF)]({pdf_url})",
#     unsafe_allow_html=True
# )
# st.sidebar.download_button(
#         label=f"⬇️ Download All Questions",
#         data=requests.get(pdf_url).content,
#         file_name=f"BEL_PE_All_Practice_Questions.pdf",
#         mime="application/pdf"
#     )

st.sidebar.divider()
st.sidebar.subheader("📄 Subject-wise PDFs")

subjects = [
    "Data Structures",
    "Operating Systems",
    "Computer Networks",
    "DBMS",
    "Compiler Design",
    "Digital Logic",
    "Object-Oriented Programming (OOPs)",
    "Computer Architecture",
    "Algorithms",
    "Artificial Intelligence / Machine Learning (BASIC ONLY)"
]

for sub in subjects:
    pdf_url = f"{BACKEND_URL}/download-pdf/{sub}"

    st.sidebar.markdown(
        f"""
        <form action="{pdf_url}" method="get" target="_blank">
            <button type="submit" style="
                width: 100%;
                padding: 8px;
                margin-bottom: 6px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            ">
                ⬇️ Download {sub}
            </button>
        </form>
        """,
        unsafe_allow_html=True
    )


# ================= FETCH QUESTION (SAFE) =================
def fetch_question():
    res = requests.get(
        f"{BACKEND_URL}/next-question",
        params={"subject": st.session_state.subject},
        timeout=500
    )
    st.session_state.current_question = res.json()
    st.session_state.selected_option = None
    st.session_state.locked = False


# ================= INITIAL LOAD =================
if not st.session_state.practice_started:
    st.info("👈 Select a subject and click **Start Practice** to begin.")
    st.stop()

if st.session_state.current_question is None:
    fetch_question()

q = st.session_state.current_question
if q is None:
    st.warning("Loading question... please wait.")
    st.stop()

# ================= QUESTION DISPLAY =================
st.markdown(f"### 📘 Subject: `{q['subject']}`")
st.markdown(f"**Q. {q['question']}**")

st.session_state.selected_option = st.radio(
    "Choose an option:",
    options=list(range(4)),
    format_func=lambda x: q["options"][x],
    disabled=st.session_state.locked
)

# ================= SUBMIT =================
if st.button("Submit Answer", disabled=st.session_state.locked):
    st.session_state.locked = True
    st.session_state.attempted += 1

    correct = st.session_state.selected_option == q["correct_option"]

    if correct:
        st.session_state.correct += 1
        st.success("✅ Correct Answer")
    else:
        st.error(
            f"❌ Wrong Answer\n\nCorrect Answer: "
            f"{q['options'][q['correct_option']]}"
        )

    # ✅ DEFINE attempt_data FIRST
    attempt_data = {
        "question": q["question"],
        "options": q["options"],
        "selected_option": st.session_state.selected_option,
        "correct_option": q["correct_option"],
        "explanation": q["explanation"],
        "subject": q["subject"],
        "result": "Correct" if correct else "Wrong"
    }

    # ✅ Save locally (session)
    st.session_state.qa_log.append(attempt_data)

    # ✅ Save permanently (backend)
    try:
        requests.post(
            f"{BACKEND_URL}/save-attempt",
            json=attempt_data,
            timeout=10
        )
    except Exception:
        st.warning("⚠️ Could not save attempt to server.")

    # ✅ Show explanation
    st.info(f"📘 **Explanation:** {q['explanation']}")


# ================= NEXT =================
    st.button("Next Question", on_click=fetch_question)
    
    # st.experimental_rerun()

# ================= STATS =================
st.divider()
st.subheader("📊 Performance")

if st.session_state.attempted > 0:
    accuracy = (st.session_state.correct / st.session_state.attempted) * 100
else:
    accuracy = 0

st.write(f"**Attempted:** {st.session_state.attempted}")
st.write(f"**Correct:** {st.session_state.correct}")
st.write(f"**Accuracy:** {accuracy:.2f}%")

# ================= TXT EXPORT =================
def generate_txt():
    lines = []
    for i, q in enumerate(st.session_state.qa_log, start=1):
        lines.append(f"Q{i}. {q['question']}")
        for idx, opt in enumerate(q["options"]):
            lines.append(f"   {chr(65+idx)}. {opt}")
        lines.append(f"Selected Answer: {chr(65 + q['selected_option'])}")
        lines.append(f"Correct Answer: {chr(65 + q['correct_option'])}")
        lines.append(f"Result: {q['result']}")
        lines.append(f"Explanation: {q['explanation']}")
        lines.append("-" * 60)
    return "\n".join(lines)

if st.session_state.qa_log:
    st.download_button(
        label="📥 Download Practice Questions (TXT)",
        data=generate_txt(),
        file_name="BEL_PE_Practice_Questions.txt",
        mime="text/plain"
    )
