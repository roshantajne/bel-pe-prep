# BEL Probationary Engineer Exam Preparation Platform

A full-stack, cloud-ready exam preparation platform designed for **BEL Probationary Engineer (Computer Science) CBT**, built using **Python, FastAPI, Streamlit, and LLMs**.  
The system focuses on **PYQ-pattern-based MCQ practice**, low-latency question delivery, and structured revision support.

---

## 🚀 Features

- **BEL PE CBT–Aligned MCQ Practice**
  - Concept-based, definition-oriented questions
  - Easy–Moderate (GATE-lite) difficulty
  - Strict PYQ pattern alignment

- **Backend-Driven Buffered Question Engine**
  - Concurrent in-memory buffering
  - Background prefetching for instant question delivery
  - Frontend remains lightweight and responsive

- **LLM-Powered MCQ Generation**
  - Uses DeepSeek via Ollama Cloud
  - Strict JSON validation
  - Automatic correction of answer–explanation mismatches

- **Controlled Practice Flow**
  - Subject selection with explicit **Start Practice**
  - One-question-at-a-time CBT-style interface
  - Real-time answer validation and explanation

- **Persistent Cloud Storage**
  - Stores attempted questions using **Google Docs API**
  - Works reliably on stateless platforms like Render

- **Revision & Export**
  - Subject-wise PDF generation
  - Cumulative PDF of all attempted questions
  - One-click downloads via backend APIs

- **Dockerized & Cloud-Ready**
  - Separate frontend and backend containers
  - Prepared for deployment on Render

---

## 🧱 Tech Stack

**Backend**
- Python
- FastAPI
- AsyncIO
- Ollama Cloud (DeepSeek model)
- Google Docs API
- ReportLab (PDF generation)

**Frontend**
- Streamlit
- Requests

**Infrastructure**
- Docker
- Docker Compose
- Render

---

## 📁 Project Structure

bel-prep/
├── backend/
│ ├── main.py
│ ├── agent.py
│ ├── buffer.py
│ ├── storage.py
│ ├── pdf_generator.py
│ ├── requirements.txt
│ └── Dockerfile
│
├── frontend/
│ ├── app.py
│ ├── requirements.txt
│ └── Dockerfile
│
├── docker-compose.yml
└── README.md

---

## ⚙️ Architecture Overview
Streamlit (Frontend)
|
| GET /next-question
▼
FastAPI (Backend)

In-memory subject-wise buffers
Concurrent background prefetch
LLM-based MCQ generation
Google Docs persistence


- All concurrency and buffering logic lives in the backend  
- Frontend only renders questions and sends user actions

---

## 🧪 How It Works

1. User selects a subject and clicks **Start Practice**
2. Frontend requests `/next-question`
3. Backend serves a question from its buffer
4. Backend refills buffer concurrently when low
5. User submits answer → backend stores attempt
6. PDFs are generated on demand from stored attempts

---

## 🐳 Run Locally with Docker

### 1️⃣ Build and start services

```bash
docker compose build
docker compose up
```

## Environment Variables
OLLAMA_API_KEY=your_ollama_api_key
GOOGLE_SERVICE_ACCOUNT_JSON={service_account_json}
GOOGLE_DOC_ID=your_google_doc_id

## 📌Author
Built by Roshan Tajane
Focused on backend systems, exam platforms, and AI-powered applications.
