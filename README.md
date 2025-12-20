# ✧ LuminaAI ✧

<div align="center">
  <img src="https://img.shields.io/badge/LuminaAI-F43E01?style=for-the-badge&logo=rocket" alt="LuminaAI" />
  <img src="https://img.shields.io/badge/Built%20with-FastAPI-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Frontend-React%20Vite-61DAFB?style=for-the-badge&logo=react" alt="React Vite" />
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%203-4285F4?style=for-the-badge&logo=google-gemini" alt="Gemini 3" />
</div>

---

### **Experience elite, private document analysis.**
Lumina is a premium, localized Retrieval-Augmented Generation (RAG) platform. It allows you to chat with your documents using state-of-the-art AI while keeping the heavy lifting (extraction, chunking, and embedding) local.

<br/>

## 🌟 **Key Features**

🚀 **Next-Gen AI**: Integrated with **Gemini 3 Flash** for ultra-fast, intelligent responses.  
📄 **Multi-Format Mastery**: Support for PDF, DOCX, TXT, Images, CSV, and SQLite.  
👁️ **OCR Integration**: Automatic Tesseract-powered OCR for scanned documents and images.  
🛡️ **Privacy First**: Embeddings and indexing happen locally via SentenceTransformers.  
⚡ **Liquid UI**: A stunning, high-performance interface built with React 19, Vite, and Tailwind.  
📦 **Infrastructure**: Fully containerized with Docker for seamless deployment.

<br/>

## 🛠️ **Tech Stack**

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: React 19, Vite, Tailwind CSS
- **AI/LLM**: Google Gemini API (`gemini-3-flash-preview`)
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **OCR**: Tesseract OCR
- **Containerization**: Docker & Docker Compose

<br/>

## 📂 **Project Architecture**

```bash
LuminaAI/
├── app/                # 🧠 Backend API (The Brain)
│   ├── api/            # Routes & Controllers
│   ├── core/           # Config & Security
│   ├── services/       # RAG logic (Chunker, Embedder, etc.)
│   └── models/         # Pydantic Schemas
├── frontend/           # 🎨 UI/UX (The Face)
│   ├── components/     # Atomic UI Elements
│   ├── services/       # API Integration
│   └── types.ts        # TypeScript Definitions
├── data/               # 💾 Persistent Storage
│   ├── uploads/        # Temp Files
│   └── faiss_index/    # Vector Databases
└── .env.example        # Configuration Map
```

<br/>

## 🚀 **Quick Start**

### **1. Preparation**
```bash
# Clone the repository
git clone https://github.com/shaikat-cse/LuminaAI.git
cd LuminaAI

# Setup environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### **2. Launch (The Easy Way)**
```bash
# Production Mode
docker-compose up --build -d

# Development Mode (Hot Reload)
docker-compose -f docker-compose.dev.yml up --build
```
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API Backend**: [http://localhost:9000](http://localhost:9000)
- **Swagger Docs**: [http://localhost:9000/docs](http://localhost:9000/docs)

<br/>

## ⚙️ **Configuration**

| Key | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | - | Your Google Gemini API Key |
| `GEMINI_MODEL` | `gemini-3-flash-preview`| Gemini model ID |
| `VITE_API_URL` | `http://localhost:9000/api/v1` | URL for frontend to API calls |
| `VECTOR_STORE_TYPE`| `faiss` | `faiss` or `chroma` |
| `CHUNK_SIZE` | `500` | Target tokens per chunk |

<br/>

## 📱 **Supported Formats**

- **PDF**: Advanced extraction via PyMuPDF & pdfplumber.
- **Word**: Full `.docx` support via python-docx.
- **Images**: OCR support for `.jpg`, `.jpeg`, and `.png`.
- **Data**: Analysis of `.csv` and `.sqlite` files.

<br/>

## 🤝 **Created By**

**Shaikat S.**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/shaikatsk)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/shaikat-cse)

---
<p align="center">MIT License © 2025 Shaikat S.</p>
